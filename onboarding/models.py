import re
import unicodedata

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

USER = settings.AUTH_USER_MODEL
mst_validator = RegexValidator(
    r"^\d{10}(-\d{3})?$",
    "MST phải gồm 10 chữ số, hoặc 10 chữ số + '-' + 3 chữ số (chi nhánh).",
)
YES_NO_NA = [("Y", "Có"), ("N", "Không"), ("NA", "N/A")]
CURRENCIES = [("VND", "VND"), ("USD", "USD"), ("EUR", "EUR")]


def normalize_name(name):
    s = unicodedata.normalize("NFKD", name.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


class SalesRep(models.Model):
    full_name = models.CharField("Họ tên", max_length=200)
    email = models.EmailField("Email", blank=True)
    fms_sales_code = models.CharField("Mã sales Sota", max_length=50, blank=True)
    active = models.BooleanField("Đang hoạt động", default=True)

    class Meta:
        verbose_name = verbose_name_plural = "Nhân viên kinh doanh"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.fms_sales_code or 'chưa có mã Sota'})"


class Partner(models.Model):
    """One onboarding request = one partner record (merged for the interim tool)."""

    class Type(models.TextChoices):
        CLIENT = "client", "Khách hàng"
        VENDOR = "vendor", "Nhà cung cấp"

    class State(models.TextChoices):
        DRAFT = "draft", "Nháp"
        IN_REVIEW = "in_review", "Đang duyệt"
        CHANGES = "changes_requested", "Yêu cầu chỉnh sửa"
        ESCALATED = "escalated", "Chờ cấp trên duyệt"
        APPROVED = "approved", "Đã duyệt"
        REJECTED = "rejected", "Từ chối"
        EXPORTED = "exported", "Đã xuất Sota"

    class VendorType(models.TextChoices):
        CARRIER = "carrier", "Hãng vận chuyển"
        COLOADER = "coloader", "Co-loader"
        AGENT = "agent", "Đại lý nước ngoài"
        TRUCKER = "trucker", "Nhà xe"
        CUSTOMS = "customs", "Đại lý hải quan"
        WAREHOUSE = "warehouse", "Kho"

    # Status (never edited by hand)
    request_no = models.CharField("Số yêu cầu", max_length=20, blank=True, editable=False)
    type = models.CharField("Loại", max_length=10, choices=Type.choices, editable=False)
    state = models.CharField("Trạng thái", max_length=20, choices=State.choices, default=State.DRAFT, editable=False)
    requester = models.ForeignKey(USER, on_delete=models.PROTECT, verbose_name="Người tạo", editable=False)
    round = models.PositiveIntegerField("Vòng duyệt", default=0, editable=False)
    created_at = models.DateTimeField("Tạo lúc", auto_now_add=True)
    submitted_at = models.DateTimeField("Gửi duyệt lúc", null=True, editable=False)
    decided_at = models.DateTimeField("Quyết định lúc", null=True, editable=False)
    last_exported_at = models.DateTimeField("Xuất Sota lần cuối", null=True, editable=False)
    changed_since_export = models.BooleanField("Thay đổi sau khi xuất", default=False, editable=False)

    # Common
    legal_name = models.CharField("Tên pháp lý", max_length=300)
    legal_name_normalized = models.CharField(max_length=300, editable=False, db_index=True)
    mst = models.CharField("MST", max_length=14, blank=True, validators=[mst_validator], db_index=True)
    foreign_reg_no = models.CharField("Số đăng ký nước ngoài", max_length=100, blank=True)
    address = models.CharField("Địa chỉ đăng ký", max_length=500, blank=True)
    country = models.CharField("Quốc gia", max_length=100, default="Việt Nam")
    sales_rep = models.ForeignKey(
        SalesRep, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Nhân viên kinh doanh",
        limit_choices_to={"active": True},
    )
    payment_terms_days = models.PositiveIntegerField("Thời hạn thanh toán (ngày)", null=True, blank=True)
    currency = models.CharField("Tiền tệ thanh toán", max_length=3, choices=CURRENCIES, default="VND")
    service_scope = models.CharField("Phạm vi dịch vụ", max_length=300, blank=True,
                                     help_text="VD: cước, hải quan, vận tải, kho")
    notes = models.TextField("Ghi chú", blank=True)
    duplicate_justification = models.TextField("Lý do tạo dù trùng", blank=True,
                                               help_text="Bắt buộc nếu hệ thống cảnh báo trùng MST/tên.")

    # Client
    client_code = models.CharField("Mã khách hàng", max_length=50, blank=True, help_text="Do Tài chính nhập.")
    invoice_name = models.CharField("Tên xuất hoá đơn", max_length=300, blank=True)
    invoice_address = models.CharField("Địa chỉ xuất hoá đơn", max_length=500, blank=True)
    invoice_email = models.EmailField("Email nhận HĐĐT", blank=True)
    credit_limit_vnd = models.PositiveBigIntegerField("Hạn mức công nợ đề xuất (VND)", null=True, blank=True)
    expected_monthly_revenue_vnd = models.PositiveBigIntegerField("Doanh thu dự kiến/tháng (VND)", null=True, blank=True)
    pass_through = models.BooleanField("Có thu hộ / chi hộ", default=False)
    pass_through_desc = models.TextField("Mô tả thu hộ / chi hộ", blank=True)
    registration_link = models.URLField("Link ĐKKD (SharePoint)", blank=True)
    contract_link = models.URLField("Link hợp đồng/báo giá (SharePoint)", blank=True)

    # Vendor
    vendor_type = models.CharField("Loại NCC", max_length=20, choices=VendorType.choices, blank=True)
    requesting_department = models.CharField("Bộ phận đề xuất", max_length=200, blank=True)
    licence_link = models.URLField("Link giấy phép (SharePoint)", blank=True)
    insurance_link = models.URLField("Link chứng nhận bảo hiểm (SharePoint)", blank=True)
    rate_agreement_link = models.URLField("Link thoả thuận giá (SharePoint)", blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "Đối tác"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.request_no} – {self.legal_name}"

    def save(self, *args, **kwargs):
        self.legal_name_normalized = normalize_name(self.legal_name)
        super().save(*args, **kwargs)
        if not self.request_no:
            self.request_no = f"REQ-{self.created_at:%Y}-{self.pk:04d}"
            Partner.objects.filter(pk=self.pk).update(request_no=self.request_no)

    def current_reviews(self):
        return self.reviews.filter(round=self.round)


class ClientRequest(Partner):
    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = "Khách hàng"


class VendorRequest(Partner):
    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = "Nhà cung cấp"


class Contact(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField("Họ tên", max_length=200)
    role_title = models.CharField("Chức danh", max_length=200, blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Điện thoại", max_length=50, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "Người liên hệ"

    def __str__(self):
        return self.name


class Review(models.Model):
    class Kind(models.TextChoices):
        FINANCE = "finance", "Tài chính"
        LEGAL = "legal", "Pháp chế"
        APPROVER = "approver", "Cấp trên"

    class Decision(models.TextChoices):
        APPROVE = "approve", "Duyệt"
        APPROVE_COND = "approve_cond", "Duyệt có điều kiện"
        CHANGES = "changes", "Yêu cầu chỉnh sửa"
        REJECT = "reject", "Từ chối"

    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="reviews", verbose_name="Đối tác")
    kind = models.CharField("Loại duyệt", max_length=10, choices=Kind.choices, editable=False)
    round = models.PositiveIntegerField("Vòng", editable=False)
    reviewer = models.ForeignKey(USER, on_delete=models.PROTECT, verbose_name="Người duyệt", editable=False)
    decision = models.CharField("Quyết định", max_length=15, choices=Decision.choices)
    conditions_text = models.TextField("Điều kiện", blank=True)
    comment = models.TextField("Nhận xét", blank=True)
    evidence_link = models.URLField("Link bằng chứng", blank=True)
    created_at = models.DateTimeField("Lúc", auto_now_add=True)

    # §7.4 Finance checklist
    mst_active = models.CharField("MST đang hoạt động (tra cứu thuế)", max_length=2, choices=YES_NO_NA, blank=True)
    invoice_complete = models.CharField("Thông tin hoá đơn đầy đủ", max_length=2, choices=YES_NO_NA, blank=True)
    terms_in_policy = models.CharField("Thời hạn thanh toán đúng chính sách", max_length=2, choices=YES_NO_NA, blank=True)
    credit_justified = models.CharField("Hạn mức phù hợp doanh thu", max_length=2, choices=YES_NO_NA, blank=True)
    prepayment_required = models.CharField("Cần tạm ứng/đặt cọc", max_length=2, choices=YES_NO_NA, blank=True)
    pass_through_agreed = models.CharField("Đã thống nhất xử lý thu hộ/chi hộ", max_length=2, choices=YES_NO_NA, blank=True)
    currency_clear = models.CharField("Điều khoản tiền tệ rõ ràng", max_length=2, choices=YES_NO_NA, blank=True)

    # §7.5 Legal checklist
    registration_verified = models.CharField("Đã xác minh ĐKKD", max_length=2, choices=YES_NO_NA, blank=True)
    signatory_verified = models.CharField("Đã xác minh thẩm quyền ký", max_length=2, choices=YES_NO_NA, blank=True)
    standard_contract = models.CharField("Dùng hợp đồng mẫu", max_length=2, choices=YES_NO_NA, blank=True)
    deviation_summary = models.TextField("Tóm tắt sai khác hợp đồng", blank=True)
    liability_ok = models.CharField("Điều khoản trách nhiệm/bảo hiểm chấp nhận được", max_length=2, choices=YES_NO_NA, blank=True)
    commodity_ok = models.CharField("Hàng hoá không bị hạn chế", max_length=2, choices=YES_NO_NA, blank=True)
    screening_done = models.CharField("Đã sàng lọc đối tượng hạn chế", max_length=2, choices=YES_NO_NA, blank=True)
    nda_required = models.CharField("Cần NDA", max_length=2, choices=YES_NO_NA, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "Kết quả duyệt"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} – {self.get_decision_display()}"

    def clean(self):
        from .services import validate_review
        validate_review(self)


class FinanceReview(Review):
    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = "Duyệt Tài chính"


class LegalReview(Review):
    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = "Duyệt Pháp chế"


class ApproverDecision(Review):
    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = "Duyệt cấp trên"


class Comment(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="comments")
    author = models.ForeignKey(USER, on_delete=models.PROTECT, verbose_name="Người viết", editable=False)
    text = models.TextField("Nội dung")
    created_at = models.DateTimeField("Lúc", auto_now_add=True)

    class Meta:
        verbose_name = verbose_name_plural = "Bình luận"
        ordering = ["created_at"]

    def __str__(self):
        return self.text[:50]


class AuditLog(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, null=True, related_name="audit")
    user = models.ForeignKey(USER, on_delete=models.PROTECT, null=True, verbose_name="Người thực hiện")
    action = models.CharField("Hành động", max_length=100)
    before = models.JSONField("Trước", null=True)
    after = models.JSONField("Sau", null=True)
    at = models.DateTimeField("Lúc", auto_now_add=True)

    class Meta:
        verbose_name = verbose_name_plural = "Nhật ký"
        ordering = ["-at"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Nhật ký chỉ được ghi thêm.")
        super().save(*args, **kwargs)


class ExportBatch(models.Model):
    type = models.CharField("Loại", max_length=10, choices=Partner.Type.choices)
    file_name = models.CharField("Tên file", max_length=200)
    created_by = models.ForeignKey(USER, on_delete=models.PROTECT, verbose_name="Người xuất")
    created_at = models.DateTimeField("Lúc", auto_now_add=True)
    partner_ids = models.JSONField("ID đối tác đã xuất", default=list)
    exceptions = models.JSONField("Ngoại lệ", default=list)
    csv = models.TextField("Nội dung CSV")

    class Meta:
        verbose_name = verbose_name_plural = "Lô xuất Sota"
        ordering = ["-created_at"]

    def __str__(self):
        return self.file_name


class LoginGuard(models.Model):
    user = models.OneToOneField(USER, on_delete=models.CASCADE, related_name="guard")
    must_change_password = models.BooleanField("Bắt đổi mật khẩu khi đăng nhập", default=True)
    failed_attempts = models.PositiveIntegerField("Số lần sai", default=0)
    locked_until = models.DateTimeField("Khoá đến", null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "Bảo mật đăng nhập"
