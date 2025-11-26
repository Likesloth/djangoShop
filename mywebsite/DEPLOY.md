# Deploy to Vercel + Neon

## Prerequisites
- Vercel account + Vercel CLI (`npm i -g vercel`).
- Neon account with permission to create a database.
- Python 3.12 (or compatible) locally for testing.

## 1) Create the Neon database
1. In Neon, create a new project and database (any branch is fine).
2. Copy the connection string and append `?sslmode=require` if Neon did not include it. It should look like  
   `postgresql://<user>:<password>@<host>/<db-name>?sslmode=require`.

## 2) Environment variables
Set these in Vercel Project Settings → Environment Variables (and optionally in a local `.env` file for testing):
- `SECRET_KEY` – long random string.
- `DEBUG` – `False` in Vercel.
- `DATABASE_URL` – the Neon URL from step 1.
- `ALLOWED_HOSTS` – `.vercel.app,your-custom-domain.com` (comma-separated).
- `CSRF_TRUSTED_ORIGINS` – `https://<your-project>.vercel.app,https://<custom-domain>` (comma-separated).
- `DJANGO_SETTINGS_MODULE` – `mywebsite.settings` (already provided in `vercel.json` but safe to set).

## 3) Local smoke test
```bash
cd mywebsite
python -m venv .venv && .\.venv\Scripts\activate  # or source .venv/bin/activate on Linux/macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 4) Deploy to Vercel
```bash
cd mywebsite
vercel login
vercel link    # link the project if not already
vercel --prod  # triggers install, collectstatic, and deployment
```
- `vercel.json` routes everything to `mywebsite/wsgi.py` and serves collected static files from `staticfiles/`.

## 5) Run migrations against Neon from Vercel
After the first deploy (and whenever models change):
```bash
vercel exec "python manage.py migrate --noinput"
# Optional: create an admin user
vercel exec "python manage.py createsuperuser"
```

## 6) Notes
- Static files are handled by Whitenoise and collected during the Vercel build (`collectstatic`).
- Vercel’s filesystem is ephemeral; move user uploads (`MEDIA_ROOT`) to object storage (e.g., S3/Cloudinary) for production durability.
- If you use Tailwind via `django-tailwind`, ensure assets are built before `collectstatic` (e.g., run `python manage.py tailwind build` locally or add it to the Vercel build command after configuring Node on Vercel).
