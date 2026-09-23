"""State machine, review rules, and Sota export. Every state change goes through here."""
import csv
import io

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import AuditLog, ExportBatch, Partner, Review
from .sota_mapping import MAPPING

S = Partner.State
D = Review.Decision
K = Review.Kind

ALLOWED = {
    S.DRAFT: {S.IN_REVIEW},
    S.CHANGES: {S.IN_REVIEW},
    S.IN_REVIEW: {S.CHANGES, S.REJECTED, S.ESCALATED, S.APPROVED},
    S.ESCALATED: {S.APPROVED, S.REJECTED},
    S.APPROVED: {S.EXPORTED},
}
REQUIRED = {
    Partner.Type.CLIENT: ["mst", "address", "sales_rep", "invoice_name", "invoice_email", "payment_terms_days"],
    Partner.Type.VENDOR: ["vendor_type", "country", "payment_terms_days"],
}


def log(partner, user, action, before=None, after=None):
    AuditLog.objects.create(partner=partner, user=user, action=action, before=before, after=after)


def transition(partner, user, to):
    if to not in ALLOWED.get(partner.state, ()):
        raise ValidationError(f"Không thể chuyển từ '{partner.get_state_display()}' sang '{S(to).label}'.")
    before = partner.state
    partner.state = to
    if to in (S.APPROVED, S.REJECTED):
        partner.decided_at = timezone.now()
    partner.save()
    log(partner, user, "state", {"state": before}, {"state": to})


def find_duplicates(partner):
    q = Q(legal_name_normalized=partner.legal_name_normalized)
    if partner.mst:
        q |= Q(mst=partner.mst)
    return Partner.objects.filter(q).exclude(pk=partner.pk).exclude(state__in=[S.DRAFT, S.REJECTED])


@transaction.atomic
def submit(partner, user):
    if partner.requester_id != user.id:
        raise ValidationError(f"{partner.request_no}: chỉ người tạo mới được gửi duyệt.")
    labels = {f.name: f.verbose_name for f in Partner._meta.fields}
    missing = [labels[f] for f in REQUIRED[partner.type] if getattr(partner, f) in (None, "")]
    if partner.type == Partner.Type.VENDOR and not (partner.mst or partner.foreign_reg_no):
        missing.append("MST hoặc số đăng ký nước ngoài")
    if missing:
        raise ValidationError(f"{partner.request_no}: thiếu {', '.join(missing)}.")
    dups = find_duplicates(partner)
    if dups and not partner.duplicate_justification.strip():
        nos = ", ".join(d.request_no for d in dups)
        raise ValidationError(f"{partner.request_no}: trùng MST/tên với {nos}. Nhập 'Lý do tạo dù trùng' rồi gửi lại.")
    partner.round += 1  # earlier reviews stay visible but no longer count
    partner.submitted_at = timezone.now()
    transition(partner, user, S.IN_REVIEW)


def validate_review(review):
    """Called from Review.clean() so errors show on the admin form."""
    if not review.partner_id:
        return
    p = review.partner
    expected = S.ESCALATED if review.kind == K.APPROVER else S.IN_REVIEW
    if p.state != expected:
        raise ValidationError(f"Đối tác đang ở trạng thái '{p.get_state_display()}', không thể duyệt.")
    if p.requester_id == review.reviewer_id:
        raise ValidationError("Không được tự duyệt yêu cầu của chính mình.")
    if p.current_reviews().filter(kind=review.kind).exists():
        raise ValidationError("Vòng duyệt này đã có kết quả cho bộ phận của bạn.")
    if review.kind == K.APPROVER and review.decision not in (D.APPROVE, D.REJECT):
        raise ValidationError("Cấp trên chỉ chọn Duyệt hoặc Từ chối.")
    if review.decision != D.APPROVE and not review.comment.strip():
        raise ValidationError({"comment": "Bắt buộc nhận xét khi không duyệt thẳng."})
    if review.decision == D.APPROVE_COND and not review.conditions_text.strip():
        raise ValidationError({"conditions_text": "Bắt buộc nhập điều kiện."})


def needs_escalation(partner, legal_review):
    return (
        (partner.credit_limit_vnd or 0) > settings.ESCALATION_CREDIT_LIMIT_VND
        or (partner.payment_terms_days or 0) > settings.ESCALATION_PAYMENT_DAYS
        or legal_review.standard_contract == "N"
    )


@transaction.atomic
def record_review(review, user):
    p = review.partner
    review.reviewer = user
    review.round = p.round
    review.save()
    log(p, user, f"review:{review.kind}", None, {"decision": review.decision, "comment": review.comment})
    if review.kind == K.APPROVER:
        return transition(p, user, S.APPROVED if review.decision == D.APPROVE else S.REJECTED)
    if review.decision == D.CHANGES:
        return transition(p, user, S.CHANGES)
    if review.decision == D.REJECT:
        return transition(p, user, S.REJECTED)
    done = {r.kind: r for r in p.current_reviews().filter(kind__in=[K.FINANCE, K.LEGAL])}
    if len(done) == 2:
        transition(p, user, S.ESCALATED if needs_escalation(p, done[K.LEGAL]) else S.APPROVED)


def conditions(partner):
    reviews = partner.reviews.filter(round=partner.round, decision=D.APPROVE_COND)
    return " | ".join(f"{r.get_kind_display()}: {r.conditions_text}" for r in reviews)


@transaction.atomic
def export(partners, user, ptype):
    """Returns (batch or None, exceptions). Incomplete rows are never exported (FR-13)."""
    columns = MAPPING[ptype]
    rows, exported, exceptions = [], [], []
    for p in partners:
        if p.type != ptype or p.state not in (S.APPROVED, S.EXPORTED):
            exceptions.append({"request_no": p.request_no, "reason": "Chưa được duyệt hoặc sai loại."})
            continue
        values = [get(p) for _, get, _ in columns]
        missing = [h for (h, _, req), v in zip(columns, values) if req and v in (None, "")]
        if missing:
            exceptions.append({"request_no": p.request_no, "reason": "Thiếu: " + ", ".join(missing)})
            continue
        rows.append(values)
        exported.append(p)
    if not rows:
        return None, exceptions
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([h for h, _, _ in columns])
    w.writerows(rows)
    now = timezone.now()
    batch = ExportBatch.objects.create(
        type=ptype, created_by=user, file_name=f"sota_{ptype}_{timezone.localtime(now):%Y%m%d_%H%M%S}.csv",
        partner_ids=[p.pk for p in exported], exceptions=exceptions, csv="﻿" + buf.getvalue(),
    )
    for p in exported:
        if p.state == S.APPROVED:
            transition(p, user, S.EXPORTED)
        p.last_exported_at, p.changed_since_export = now, False
        p.save()
        log(p, user, "export", None, {"batch": batch.file_name})
    return batch, exceptions
