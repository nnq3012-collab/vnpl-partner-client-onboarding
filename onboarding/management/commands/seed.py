from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

from onboarding.models import LoginGuard, SalesRep

PARTNERS = ["view_clientrequest", "change_clientrequest", "view_vendorrequest", "change_vendorrequest"]
REVIEWS = ["view_financereview", "view_legalreview", "view_approverdecision"]
COMMON = ["view_salesrep", "add_comment", "view_comment", "view_review", "view_auditlog",
          "add_contact", "change_contact", "view_contact"]
ROLES = {
    "Sales": ["add_clientrequest", "change_clientrequest", "view_clientrequest"],
    "Procurement": ["add_vendorrequest", "change_vendorrequest", "view_vendorrequest"],
    "Finance": PARTNERS + REVIEWS + ["add_financereview"],
    "Legal": PARTNERS + REVIEWS + ["add_legalreview"],
    "Approver": PARTNERS + REVIEWS + ["add_approverdecision"],
    "Exporter": PARTNERS + ["view_exportbatch"],
}
DEMO_USERS = {"sales1": "Sales", "proc1": "Procurement", "fin1": "Finance", "legal1": "Legal",
              "boss1": "Approver", "ops1": "Exporter"}
DEMO_PASSWORD = "Vnpl@2026demo"


class Command(BaseCommand):
    help = "Create role groups (idempotent). --demo also adds demo users and salespeople."

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true")

    def handle(self, demo, **opts):
        for name, codes in ROLES.items():
            g, _ = Group.objects.get_or_create(name=name)
            perms = Permission.objects.filter(content_type__app_label="onboarding", codename__in=codes + COMMON)
            g.permissions.set(perms)
        self.stdout.write("Roles ready: " + ", ".join(ROLES))
        if not demo:
            return
        SalesRep.objects.get_or_create(full_name="Nguyễn Văn An", defaults={"fms_sales_code": "S001"})
        SalesRep.objects.get_or_create(full_name="Trần Thị Bình", defaults={"fms_sales_code": ""})
        users = dict(DEMO_USERS, admin=None)
        for username, group in users.items():
            u, created = User.objects.get_or_create(username=username, defaults={"is_superuser": group is None})
            if created:
                u.set_password(DEMO_PASSWORD)
                u.save()
            if group:
                u.groups.add(Group.objects.get(name=group))
            LoginGuard.objects.filter(user=u).update(must_change_password=False)
        self.stdout.write(f"Demo users {', '.join(users)} / password {DEMO_PASSWORD}")
