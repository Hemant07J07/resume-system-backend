# scripts/create_demo_data.py
"""
Run: python manage.py runscript create_demo_data
Or run via shell: python manage.py shell -c "exec(open('scripts/create_demo_data.py').read())"
"""
from django.contrib.auth import get_user_model
from resumes.models import Resume, Project, Experience, Skill, Achievement, Education
User = get_user_model()

username = "demo"
password = "DemoPass123"

user, created = User.objects.get_or_create(username=username, defaults={
    "email": "demo@example.com",
    "first_name": "Demo",
    "last_name": "User"
})
if created:
    user.set_password(password)
    user.save()
    print(f"Created user {username}/{password}")
else:
    print(f"User {username} already exists")

resume = Resume.objects.create(owner=user, title="Demo Resume", summary_text="Sample summary created for demo.")
print("Created resume id:", resume.id)

Project.objects.create(resume=resume, title="SmartResume", description="Auto resume generator", tech_stack="Django,DRF")
Experience.objects.create(resume=resume, company="InternCo", role="Backend Intern", start_date="2024-01-01", description="Worked on backend features")
Education.objects.create(resume=resume, institute="ABC University", degree="B.Tech", start_date="2019-07-01", end_date="2023-05-01")
Skill.objects.create(resume=resume, name="Django", level="Expert")
Achievement.objects.create(resume=resume, title="1st Prize - SmartResume Hack", issuer="Hackathon", description="Built resume auto-generator")

print("Demo data created. Resume id:", resume.id)
