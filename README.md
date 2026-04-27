# StudyBud

A Django-based web application designed to connect people with similar study interests.  
**StudyBud** helps users find others who share their study goals and create a personalized favorites list to track preferred study partners.

---

## Features

- Connect with users who share similar study topics.  
- Add and manage favorite study buddies.  
- User authentication and session management.  
- Real-time chat rooms (if configured).  
- Responsive design built with HTML, CSS, and Django templates.  
- SQLite database for fast local setup.

---

## Prerequisites

Before running the app, ensure you have:

- **Python 3.12**
- **Django 5.2 LTS**
- **Git**
- (Optional) A virtual environment tool such as `venv` or `virtualenv`.

---

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/SaikrishnaSamudrala3/StudyBud.git
cd StudyBud

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # (Windows: .venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt

# Configure local environment
cp .env.example .env

# Run database migrations
python manage.py migrate

# (Optional) Create a superuser to access the admin panel
python manage.py createsuperuser
```

## Environment Variables

Use `.env` for local development and configure the same values in Vercel project settings for deployment.

- `DJANGO_SECRET_KEY`: required in production.
- `DJANGO_DEBUG`: use `False` in production.
- `DJANGO_ALLOWED_HOSTS`: comma-separated hosts, for example `your-domain.com,.vercel.app`.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated origins, for example `https://your-domain.com,https://*.vercel.app`.
- `DATABASE_URL`: use a hosted database URL in production. SQLite is fine for local development.
- `CORS_ALLOW_ALL_ORIGINS`: use `False` in production unless the API is intentionally public.
- `CORS_ALLOWED_ORIGINS`: comma-separated allowed origins when CORS is restricted.

## Vercel Deployment

Vercel now detects Django projects from `manage.py`. This repo includes `vercel.json` to run static collection during the build and `.python-version` to pin Python 3.12.

Before deploying, add the environment variables above in Vercel and run migrations against your production database.

## Docker

```bash
docker build -t studybud .
docker run --env-file .env -p 8000:8000 studybud
```

To run the app with Postgres in Docker:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000/
```

The Compose setup creates a local Postgres database and runs migrations automatically.
