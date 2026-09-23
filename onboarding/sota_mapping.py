"""Sota import columns: (header, value getter, required).

ponytail: placeholder columns from BRD §8. Replace headers/order once Sota's import fields arrive (Q1).
"""
from django.utils import timezone


def _contact(field):
    def get(p):
        c = p.contacts.first()
        return getattr(c, field) if c else ""
    return get


def _rep(field):
    return lambda p: getattr(p.sales_rep, field) if p.sales_rep else ""


def _conditions(p):
    from .services import conditions
    return conditions(p)


def _approved_at(p):
    return timezone.localtime(p.decided_at).strftime("%Y-%m-%d") if p.decided_at else ""


_TAIL = [
    ("conditions_text", _conditions, False),
    ("sales_rep_name", _rep("full_name"), False),
    ("sales_rep_fms_code", _rep("fms_sales_code"), None),  # required flag set per type below
    ("primary_contact_name", _contact("name"), False),
    ("primary_contact_email", _contact("email"), False),
    ("primary_contact_phone", _contact("phone"), False),
    ("request_no", lambda p: p.request_no, True),
    ("approved_at", _approved_at, False),
]


def _tail(rep_code_required):
    return [(h, g, rep_code_required if r is None else r) for h, g, r in _TAIL]


MAPPING = {
    "client": [
        ("client_code", lambda p: p.client_code, False),
        ("legal_name", lambda p: p.legal_name, True),
        ("mst", lambda p: p.mst, True),
        ("address", lambda p: p.address, True),
        ("invoice_name", lambda p: p.invoice_name, True),
        ("invoice_email", lambda p: p.invoice_email, True),
        ("payment_terms_days", lambda p: p.payment_terms_days, True),
        ("credit_limit_vnd", lambda p: p.credit_limit_vnd, False),
        ("billing_currency", lambda p: p.currency, True),
    ] + _tail(True),
    "vendor": [
        ("legal_name", lambda p: p.legal_name, True),
        ("mst_or_foreign_reg", lambda p: p.mst or p.foreign_reg_no, True),
        ("country", lambda p: p.country, True),
        ("vendor_type", lambda p: p.get_vendor_type_display(), True),
        ("payment_terms_days", lambda p: p.payment_terms_days, True),
        ("billing_currency", lambda p: p.currency, True),
    ] + _tail(False),  # Q4: vendor salesperson optional for now
}
