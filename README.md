# VNPL Partner Onboarding (interim)

Django admin app for the client/vendor approval flow in `BRDv3.md`. Retire when Polaris CRM goes live.

## Run locally
```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed --demo        # roles + demo users (password Vnpl@2026demo)
python manage.py runserver          # http://127.0.0.1:8000
python manage.py test onboarding
```

## Deploy (Render + Neon)
- Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed`
- Start: `gunicorn config.wsgi`
- Env: `DATABASE_URL` (Neon), `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS=https://<host>`,
  optional `ESCALATION_CREDIT_LIMIT_VND`, `ESCALATION_PAYMENT_DAYS`.
- First admin: `python manage.py createsuperuser` in the Render shell.

## Where things live
- State machine, review rules, export: `onboarding/services.py`
- Sota CSV columns: `onboarding/sota_mapping.py` (placeholder until Q1)
- Roles/permissions: `onboarding/management/commands/seed.py`
