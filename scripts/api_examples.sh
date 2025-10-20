# scripts/api_examples.sh
BASE="http://127.0.0.1:8000"
# 1. Register (if needed)
curl -X POST $BASE/api/auth/register/ -H "Content-Type: application/json" -d '{"username":"demo2","email":"demo2@example.com","password":"DemoPass123","first_name":"Demo"}'

# 2. Get token
curl -X POST $BASE/api/token/ -H "Content-Type: application/json" -d '{"username":"demo","password":"DemoPass123"}'

# 3. List resumes (use token from previous step)
# export TOKEN="eyJ..." then:
# curl -H "Authorization: Bearer $TOKEN" $BASE/api/resumes/

# 4. Create resume
# curl -X POST $BASE/api/resumes/ -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"title":"My Resume"}'

# 5. Generate summary
# curl -X POST $BASE/api/resumes/1/generate_summary/ -H "Authorization: Bearer $TOKEN"

# 6. Export PDF
# curl -X GET $BASE/api/resumes/1/export_pdf/ -H "Authorization: Bearer $TOKEN" --output demo_resume.pdf

# 7. Webhook (test)
curl -X POST $BASE/api/integrations/webhook/ -H "Content-Type: application/json" -H "X-WEBHOOK-SECRET: change-this-in-prod" -d '{"source":"hack","external_id":"x1","type":"achievement","data":{"title":"Prize"},"target_resume_id":1}'
