"""One end-to-end check of the BRD §14 UAT flow."""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from . import services
from .models import Partner, Review, SalesRep

S, D, K = Partner.State, Review.Decision, Review.Kind


class FlowTest(TestCase):
    def setUp(self):
        self.sales, self.fin, self.legal, self.boss, self.ops = (
            User.objects.create_user(n, password="Xx!23456789") for n in ("s", "f", "l", "b", "o"))
        self.rep = SalesRep.objects.create(full_name="Rep", fms_sales_code="S1")

    def client_partner(self, **kw):
        data = dict(type="client", requester=self.sales, legal_name="Công ty TNHH Á Đông", mst="0101234567",
                    address="HN", sales_rep=self.rep, invoice_name="X", invoice_email="x@x.vn",
                    payment_terms_days=30)
        data.update(kw)
        return Partner.objects.create(**data)

    def review(self, p, kind, user, decision, **kw):
        r = Review(partner=p, kind=kind, reviewer=user, decision=decision, **kw)
        r.full_clean(exclude=["round"])
        services.record_review(r, user)
        p.refresh_from_db()

    def test_uat_flow(self):
        with self.assertRaises(ValidationError):  # UAT 2: bad MST
            self.client_partner(mst="123").full_clean()

        p = self.client_partner(credit_limit_vnd=10**12)
        services.submit(p, self.sales)
        with self.assertRaises(ValidationError):  # UAT 6: no self-review
            self.review(p, K.FINANCE, self.sales, D.APPROVE)

        # UAT 4: changes requested, resubmit resets reviews
        self.review(p, K.FINANCE, self.fin, D.APPROVE)
        self.review(p, K.LEGAL, self.legal, D.CHANGES, comment="Thiếu ĐKKD")
        self.assertEqual(p.state, S.CHANGES)
        services.submit(p, self.sales)
        self.assertEqual(p.current_reviews().count(), 0)

        # UAT 5: over threshold escalates
        self.review(p, K.FINANCE, self.fin, D.APPROVE)
        self.review(p, K.LEGAL, self.legal, D.APPROVE)
        self.assertEqual(p.state, S.ESCALATED)
        self.review(p, K.APPROVER, self.boss, D.APPROVE)
        self.assertEqual(p.state, S.APPROVED)

        # UAT 3: duplicate needs justification
        dup = self.client_partner(legal_name="CONG TY TNHH A DONG", mst="0109999999")
        with self.assertRaises(ValidationError):
            services.submit(dup, self.sales)

        # UAT 7/8: export, missing Sota code goes to exceptions
        bad = self.client_partner(mst="0108888888", legal_name="B", sales_rep=SalesRep.objects.create(full_name="NoCode"),
                                  state=S.APPROVED)
        batch, exc = services.export([p, bad], self.ops, "client")
        self.assertEqual(batch.partner_ids, [p.pk])
        self.assertEqual(exc[0]["request_no"], bad.request_no)
        self.assertTrue(batch.csv.startswith("﻿"))
        p.refresh_from_db()
        self.assertEqual(p.state, S.EXPORTED)

    def test_lockout_and_forced_password_change(self):
        u = User.objects.create_user("new", password="Temp@12345")
        for _ in range(5):
            self.client.post("/login/", {"username": "new", "password": "wrong"})
        self.assertFalse(self.client.login(username="new", password="Temp@12345"))  # UAT 1: locked
        u.guard.locked_until = None
        u.guard.save()
        self.client.login(username="new", password="Temp@12345")
        self.assertRedirects(self.client.get("/"), "/password_change/")
