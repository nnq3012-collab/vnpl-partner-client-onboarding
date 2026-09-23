"""FR-01: lockout after 5 failures for 15 min, forced password change, staff-by-default users."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import LoginGuard

User = get_user_model()
MAX_FAILURES = 5
LOCK_FOR = timedelta(minutes=15)


class LockoutBackend(ModelBackend):
    def user_can_authenticate(self, user):
        g = LoginGuard.objects.filter(user=user).first()
        locked = g and g.locked_until and g.locked_until > timezone.now()
        return super().user_can_authenticate(user) and not locked


@receiver(user_login_failed)
def on_login_failed(sender, credentials, **kwargs):
    user = User.objects.filter(username=credentials.get("username")).first()
    if not user:
        return
    g, _ = LoginGuard.objects.get_or_create(user=user)
    g.failed_attempts += 1
    if g.failed_attempts >= MAX_FAILURES:
        g.failed_attempts, g.locked_until = 0, timezone.now() + LOCK_FOR
    g.save()


@receiver(user_logged_in)
def on_login(sender, user, **kwargs):
    LoginGuard.objects.update_or_create(user=user, defaults={"failed_attempts": 0, "locked_until": None})


@receiver(pre_save, sender=User)
def staff_by_default(sender, instance, **kwargs):
    # The whole app is the Django admin, so every account needs staff access.
    if not instance.pk:
        instance.is_staff = True


@receiver(post_save, sender=User)
def create_guard(sender, instance, created, **kwargs):
    if created:
        LoginGuard.objects.get_or_create(user=instance)


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        u = request.user
        if u.is_authenticated:
            g, _ = LoginGuard.objects.get_or_create(user=u)
            if request.path == reverse("admin:password_change_done"):
                if g.must_change_password:
                    g.must_change_password = False
                    g.save()
            elif g.must_change_password and request.path not in (
                reverse("admin:password_change"), reverse("admin:logout"), reverse("admin:jsi18n"),
            ):
                return redirect("admin:password_change")
        return self.get_response(request)
