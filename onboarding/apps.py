from django.apps import AppConfig


class OnboardingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "onboarding"
    verbose_name = "Duyệt đối tác"

    def ready(self):
        from . import auth  # noqa: F401  (registers signals)
