# Resume System Backend

Small Django + DRF service to manage user resumes, projects, experiences, skills and achievements.
Includes:
- JWT auth (Simple JWT)
- Resume CRUD + child resources (projects, experiences, educations, skills, achievements)
- Resume summary generator (rule-based + optional OpenAI)
- Secure webhook endpoint for external integrations
- Simple PDF export endpoint
- OpenAPI (Swagger) docs at `/api/docs/`

## Quick start (local, docker)
1. Copy `.env.example` → `.env` and update values.
2. Build & run:
   ```bash
   docker-compose build
   docker-compose up -d
