# Resume System Backend

Small Django + DRF backend to manage user resumes, projects, experiences, skills and achievements.

---

## Features
- JWT authentication (Simple JWT)
- Resume CRUD and child resources: Projects, Experiences, Educations, Skills, Achievements
- Resume summary generator (rule-based; optional OpenAI integration)
- Secure webhook endpoint for external integrations (`X-WEBHOOK-SECRET`)
- Simple PDF export endpoint
- OpenAPI (Swagger) docs at `/api/docs/`
- Docker + docker-compose and Render-friendly deployment
- Basic tests and GitHub Actions CI

---

## Quick start (local)

1. Copy `.env.example` → `.env` and update values (see **Environment** below).

2. Create virtualenv & install:

```bash
python -m venv venv
# mac / linux
source venv/bin/activate
# windows (PowerShell)
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
