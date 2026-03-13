# Resume System Backend

Django + Django REST Framework backend for managing resumes and related resources (projects, experience, education, skills, achievements). Includes JWT auth and built-in OpenAPI/Swagger docs.

## Features

- JWT authentication (Simple JWT)
- Resume CRUD + child resources: Projects, Experiences, Educations, Skills, Achievements
- Summary generation endpoint (rule-based; optional OpenAI enhancement)
- Webhook endpoint secured with `X-WEBHOOK-SECRET`
- PDF export endpoint
- OpenAPI schema + Swagger UI
- Docker + docker-compose support

## Tech stack

- Python / Django 5
- Django REST Framework
- Simple JWT
- drf-spectacular (OpenAPI + Swagger UI)

## API docs (Swagger)

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema (JSON): `http://127.0.0.1:8000/api/schema/`

### How to test APIs in Swagger (JWT)

1. Start the server (see **Run locally** or **Run with Docker** below).
2. Open Swagger UI at `http://127.0.0.1:8000/api/docs/`.
3. Create a user:
   - Use `POST /api/auth/register/`
   - Example body:
     ```json
     {
       "username": "demo",
       "email": "demo@example.com",
       "password": "DemoPass123",
       "first_name": "Demo"
     }
     ```
4. Get an access token:
   - Use `POST /api/token/`
   - Example body:
     ```json
     {"username": "demo", "password": "DemoPass123"}
     ```
   - Copy the `access` token.
5. Authenticate in Swagger:
   - Click **Authorize** in Swagger UI.
   - Paste the token using the format: `Bearer <access_token>`.
6. Use **Try it out** on endpoints like `GET /api/resumes/`.

Notes:
- Most API endpoints require authentication by default.
- You can also verify your token using `GET /api/auth/me/`.

## Environment variables

This project reads configuration from environment variables (Docker loads them automatically from `.env` via `docker-compose.yml`).

Common variables:

- `DEBUG` (e.g. `True` for local dev)
- `SECRET_KEY`
- `ALLOWED_HOSTS` (comma-separated; defaults to `localhost,127.0.0.1`)
- `WEBHOOK_SECRET` (used by `/api/integrations/webhook/`)
- `OPENAI_API_KEY` (optional)

See `.env.example` for a starting point.

## Run locally (SQLite)

Prereqs: Python 3.11+ recommended.

```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Server will be at `http://127.0.0.1:8000/`.

## Run with Docker

```bash
docker compose up --build
```

- App: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`

The container entrypoint runs migrations and starts Gunicorn.

Important:
- `docker-compose.yml` includes a Postgres service and sets `DATABASE_URL`, but the current Django settings default to SQLite (`db.sqlite3`). If you want the app to use Postgres, update `config/settings.py` to read `DATABASE_URL` (e.g. via `dj-database-url`) and add the appropriate dependency.

## Authentication

- Register: `POST /api/auth/register/`
- Get JWT: `POST /api/token/`
- Refresh JWT: `POST /api/token/refresh/`
- Current user: `GET /api/auth/me/`

Use the header:

`Authorization: Bearer <access_token>`

## Main API endpoints

All endpoints are under `/api/` and use trailing slashes.

- Resumes: `/api/resumes/`
- Projects: `/api/projects/`
- Experiences: `/api/experiences/`
- Educations: `/api/educations/`
- Skills: `/api/skills/`
- Achievements: `/api/achievements/`

Extra actions:

- Generate summary: `POST /api/resumes/{id}/generate_summary/`
- Export PDF: `GET /api/resumes/{id}/export_pdf/`

## Webhook endpoint

Endpoint:

- `POST /api/integrations/webhook/`

Header:

- `X-WEBHOOK-SECRET: <your-secret>`

Example payload:

```json
{
  "source": "hackathon_platform",
  "external_id": "hack_2025_12345",
  "type": "achievement",
  "data": {
    "title": "1st Prize - SmartResume Hack",
    "description": "Built a resume auto-generator",
    "date": "2025-10-15",
    "proof_url": "https://example.com/submission/123"
  },
  "target_resume_id": 1
}
```

## Scripts

- API curl examples: `scripts/api_examples.sh`
- Create demo data:
  ```bash
  python manage.py shell -c "exec(open('scripts/create_demo_data.py').read())"
  ```

## Tests

```bash
python manage.py test
```
