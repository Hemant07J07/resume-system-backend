# resumes/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class ResumeApiTests(APITestCase):
    def setUp(self):
        # create user
        self.user = User.objects.create_user(username='testuser', password='Testpass123')
        self.token_url = reverse('token_obtain_pair')
        resp = self.client.post(self.token_url, {'username': 'testuser', 'password': 'Testpass123'}, format='json')
        self.assertIn('access', resp.data)
        self.access = resp.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.access}'}

    def test_create_resume_and_project_and_generate_summary(self):
        # create resume
        resp = self.client.post('/api/resumes/', {'title': 'My Test Resume'}, format='json', **self.auth_header)
        self.assertEqual(resp.status_code, 201)
        resume_id = resp.data['id']

        # create project
        proj_payload = {'resume': resume_id, 'title': 'Test Project', 'description': 'desc', 'tech_stack': 'Django'}
        resp2 = self.client.post('/api/projects/', proj_payload, format='json', **self.auth_header)
        self.assertEqual(resp2.status_code, 201)

        # generate summary
        resp3 = self.client.post(f'/api/resumes/{resume_id}/generate_summary/', format='json', **self.auth_header)
        self.assertEqual(resp3.status_code, 200)
        self.assertIn('summary', resp3.data)
        self.assertTrue(len(resp3.data['summary']) > 10)

    def test_webhook_creates_achievement(self):
        # create resume first
        resp = self.client.post('/api/resumes/', {'title': 'Webhook Resume'}, format='json', **self.auth_header)
        self.assertEqual(resp.status_code, 201)
        resume_id = resp.data['id']

        # prepare webhook header secret from settings
        secret = settings.WEBHOOK_SECRET
        headers = {'HTTP_X_WEBHOOK_SECRET': secret}

        payload = {
            "source": "hackathon_platform",
            "external_id": "hack_0001",
            "type": "achievement",
            "data": {
                "title": "Won Hack",
                "description": "Built auto-resume",
                "date": "2025-10-01",
                "proof_url": "https://example.org/proof/1"
            },
            "target_resume_id": resume_id
        }

        resp2 = self.client.post('/api/integrations/webhook/', payload, format='json', **headers)
        self.assertIn(resp2.status_code, (200, 201))
        self.assertIn('created', resp2.data)
