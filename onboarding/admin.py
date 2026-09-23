from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Q
from django.http import HttpResponse

from . import services
from .models import (
    ApproverDecision, AuditLog, ClientRequest, Comment, Contact, ExportBatch, FinanceReview,
    LegalReview, LoginGuard, Partner, Review, SalesRep, VendorRequest,
)

S = Partner.State
K = Review.Kind
REVIEW_GROUPS = {"Finance": K.FINANCE, "Legal": K.LEGAL, "Approver": K.APPROVER}
SEE_ALL_GROUPS = {"Finance", "Legal", "Approver", "Exporter"}


def groups(user):
    return set(user.groups.values_list("name", flat=True))


def sees_all(user):
    return user.is_superuser or bool(groups(user) & SEE_ALL_GROUPS)


class QueueFilter(admin.SimpleListFilter):
    title = "Hàng đợi"
    parameter_name = "queue"

    def lookups(self, request, model_admin):
        return [("mine", "Yêu cầu của tôi"), ("awaiting", "Chờ tôi duyệt"), ("ready", "Sẵn sàng xuất Sota")]

    def queryset(self, request, qs):
        u = request.user
        if self.value() == "mine":
            return qs.filter(requester=u)
        if self.value() == "ready":
            return qs.filter(Q(state=S.APPROVED) | Q(state=S.EXPORTED, changed_since_export=True))
        if self.value() == "awaiting":
            q, g = Q(pk__in=[]), groups(u)
            for name, kind in REVIEW_GROUPS.items():
                if name in g or u.is_superuser:
                    done = Review.objects.filter(partner=OuterRef("pk"), round=OuterRef("round"), kind=kind)
                    qs = qs.annotate(**{f"done_{kind}": Exists(done)})
                    state = S.ESCALATED if kind == K.APPROVER else S.IN_REVIEW
                    q |= Q(state=state, **{f"done_{kind}": False})
            return qs.filter(q).exclude(requester=u)
        return qs


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    can_delete = False

    def _editable(self, request, obj):
        return obj is None or self.admin_site._registry[type(obj)].editable_fields(request, obj) != []

    def has_add_permission(self, request, obj=None):
        return self._editable(request, obj)

    def has_change_permission(self, request, obj=None):
        return self._editable(request, obj)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    can_delete = False
    fields = ("created_at", "author", "text")
    readonly_fields = ("created_at", "author")

    def has_change_permission(self, request, obj=None):
        return False  # comments are append-only


class ReadOnlyInline(admin.TabularInline):
    extra = 0
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        return self.fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReviewInline(ReadOnlyInline):
    model = Review
    fields = ("round", "kind", "reviewer", "decision", "conditions_text", "comment", "created_at")
    verbose_name_plural = "Lịch sử duyệt"


class AuditInline(ReadOnlyInline):
    model = AuditLog
    fields = ("at", "user", "action", "before", "after")
    verbose_name_plural = "Nhật ký"


class PartnerAdminBase(admin.ModelAdmin):
    kind = None
    data_fieldsets = ()
    status_fields = ("request_no", "state", "round", "requester", "submitted_at", "decided_at",
                     "last_exported_at", "changed_since_export")
    list_display = ("request_no", "legal_name", "mst", "state", "sales_rep", "requester", "submitted_at",
                    "changed_since_export")
    list_filter = (QueueFilter, "state", "sales_rep")
    search_fields = ("request_no", "legal_name", "mst")
    inlines = [ContactInline, CommentInline, ReviewInline, AuditInline]
    actions = ["submit_selected", "export_selected"]

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(type=self.kind).select_related("sales_rep", "requester")
        return qs if sees_all(request.user) else qs.filter(requester=request.user)

    def data_fields(self):
        return [f for _, opts in self.data_fieldsets for f in opts["fields"]]

    def editable_fields(self, request, obj):
        u, data = request.user, self.data_fields()
        requester_fields = [f for f in data if f != "client_code"]
        if obj is None:
            return requester_fields
        if u.is_superuser:
            return data
        if obj.requester_id == u.id and obj.state in (S.DRAFT, S.CHANGES):
            return requester_fields
        if "Finance" in groups(u) and obj.state not in (S.DRAFT, S.REJECTED):
            # ponytail: Finance editing the salesperson counts as the §5 "Finance acknowledgement".
            return [f for f in ("sales_rep", "client_code") if f in data]
        return []

    def get_fieldsets(self, request, obj=None):
        status = [("Trạng thái", {"fields": self.status_fields})] if obj else []
        return status + list(self.data_fieldsets)

    def get_readonly_fields(self, request, obj=None):
        editable = self.editable_fields(request, obj)
        return list(self.status_fields) + [f for f in self.data_fields() if f not in editable]

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.type, obj.requester = self.kind, request.user
            super().save_model(request, obj, form, change)
            services.log(obj, request.user, "create")
        elif form.changed_data:
            old = Partner.objects.get(pk=obj.pk)
            before = {f: str(getattr(old, f)) for f in form.changed_data}
            after = {f: str(getattr(obj, f)) for f in form.changed_data}
            if obj.state == S.EXPORTED:
                obj.changed_since_export = True
            super().save_model(request, obj, form, change)
            services.log(obj, request.user, "edit", before, after)

    def save_formset(self, request, form, formset, change):
        for item in formset.save(commit=False):
            if isinstance(item, Comment):
                item.author = request.user
                item.save()
                services.log(form.instance, request.user, "comment", None, {"text": item.text})
            else:
                item.save()

    @admin.action(description="Gửi duyệt")
    def submit_selected(self, request, queryset):
        for p in queryset:
            try:
                services.submit(p, request.user)
                messages.success(request, f"{p.request_no}: đã gửi duyệt.")
            except ValidationError as e:
                messages.error(request, " ".join(e.messages))

    @admin.action(description="Xuất CSV cho Sota", permissions=["export"])
    def export_selected(self, request, queryset):
        batch, exceptions = services.export(list(queryset), request.user, self.kind)
        for e in exceptions:
            messages.warning(request, f"Không xuất {e['request_no']}: {e['reason']}")
        if batch:
            resp = HttpResponse(batch.csv, content_type="text/csv; charset=utf-8")
            resp["Content-Disposition"] = f'attachment; filename="{batch.file_name}"'
            return resp

    def has_export_permission(self, request):
        return request.user.is_superuser or "Exporter" in groups(request.user)


@admin.register(ClientRequest)
class ClientRequestAdmin(PartnerAdminBase):
    kind = Partner.Type.CLIENT
    data_fieldsets = (
        ("Thông tin chung", {"fields": ("legal_name", "mst", "address")}),
        ("Hoá đơn", {"fields": ("invoice_name", "invoice_address", "invoice_email")}),
        ("Thương mại", {"fields": ("sales_rep", "payment_terms_days", "credit_limit_vnd",
                                   "expected_monthly_revenue_vnd", "currency", "service_scope",
                                   "pass_through", "pass_through_desc")}),
        ("Tài liệu (SharePoint)", {"fields": ("registration_link", "contract_link")}),
        ("Khác", {"fields": ("client_code", "notes", "duplicate_justification")}),
    )


@admin.register(VendorRequest)
class VendorRequestAdmin(PartnerAdminBase):
    kind = Partner.Type.VENDOR
    list_filter = PartnerAdminBase.list_filter + ("vendor_type",)
    data_fieldsets = (
        ("Thông tin chung", {"fields": ("legal_name", "mst", "foreign_reg_no", "country", "address")}),
        ("Dịch vụ", {"fields": ("vendor_type", "service_scope", "payment_terms_days", "currency",
                                "requesting_department", "sales_rep")}),
        ("Tài liệu (SharePoint)", {"fields": ("licence_link", "insurance_link", "rate_agreement_link")}),
        ("Khác", {"fields": ("notes", "duplicate_justification")}),
    )


class ReviewAdminBase(admin.ModelAdmin):
    kind = None
    checklist = ()
    list_display = ("partner", "decision", "reviewer", "round", "created_at")
    list_filter = ("decision",)

    def get_fields(self, request, obj=None):
        return ("partner", "decision", "conditions_text", "comment", "evidence_link") + self.checklist

    def get_queryset(self, request):
        return super().get_queryset(request).filter(kind=self.kind)

    def get_form(self, request, obj=None, **kwargs):
        Form, kind = super().get_form(request, obj, **kwargs), self.kind

        class ReviewForm(Form):
            def __init__(self, *args, **kw):
                super().__init__(*args, **kw)
                self.instance.kind, self.instance.reviewer = kind, request.user

        return ReviewForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "partner":
            state = S.ESCALATED if self.kind == K.APPROVER else S.IN_REVIEW
            kwargs["queryset"] = Partner.objects.filter(state=state).exclude(requester=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        services.record_review(obj, request.user)

    def has_change_permission(self, request, obj=None):
        return False  # decisions are final; a resubmission starts a new round

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FinanceReview)
class FinanceReviewAdmin(ReviewAdminBase):
    kind = K.FINANCE
    checklist = ("mst_active", "invoice_complete", "terms_in_policy", "credit_justified",
                 "prepayment_required", "pass_through_agreed", "currency_clear")


@admin.register(LegalReview)
class LegalReviewAdmin(ReviewAdminBase):
    kind = K.LEGAL
    checklist = ("registration_verified", "signatory_verified", "standard_contract", "deviation_summary",
                 "liability_ok", "commodity_ok", "screening_done", "nda_required")


@admin.register(ApproverDecision)
class ApproverDecisionAdmin(ReviewAdminBase):
    kind = K.APPROVER

    def get_fields(self, request, obj=None):
        return ("partner", "decision", "comment")

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "decision":
            kwargs["choices"] = [(Review.Decision.APPROVE, "Duyệt"), (Review.Decision.REJECT, "Từ chối")]
        return super().formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(SalesRep)
class SalesRepAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "fms_sales_code", "active")
    list_filter = ("active",)
    search_fields = ("full_name", "email", "fms_sales_code")


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ExportBatch)
class ExportBatchAdmin(ReadOnlyAdmin):
    list_display = ("file_name", "type", "created_by", "created_at")


@admin.register(AuditLog)
class AuditLogAdmin(ReadOnlyAdmin):
    list_display = ("at", "user", "partner", "action")
    list_filter = ("action",)


class GuardInline(admin.StackedInline):
    model = LoginGuard
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False  # created automatically with the user


admin.site.unregister(User)


@admin.register(User)
class UserWithGuardAdmin(UserAdmin):
    inlines = [GuardInline]
