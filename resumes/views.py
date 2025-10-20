# resumes/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ParseError, NotFound
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse

from .models import Resume, Project, Experience, Education, Skill, Achievement
from .serializers import (ResumeSerializer, ProjectSerializer,
                          ExperienceSerializer, EducationSerializer,
                          SkillSerializer, AchievementSerializer)
from .permissions import IsOwnerOrReadOnly

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# optional OpenAI usage
OPENAI_AVAILABLE = False
try:
    import openai
    OPENAI_AVAILABLE = True
    openai.api_key = settings.OPENAI_API_KEY or None
except Exception:
    OPENAI_AVAILABLE = False


class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return Resume.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_summary(self, request, pk=None):
        """
        Generate a professional summary for the resume.
        Behavior:
          - If OPENAI_API_KEY is configured and openai package is available -> try calling OpenAI (non-blocking fallback).
          - Otherwise -> fallback to rule-based summary built from skills/projects/experiences.
        """
        resume = self.get_object()

        # RULE-BASED summary builder (always available)
        def rule_based_summary(user, resume_obj):
            skills_qs = resume_obj.skills.all()[:8]
            top_skills = [s.name for s in skills_qs]
            proj_qs = resume_obj.projects.all()[:3]
            projects = [p.title for p in proj_qs]
            exp_qs = resume_obj.experiences.all().order_by('-start_date')[:2]
            roles = [f"{e.role} at {e.company}" for e in exp_qs]

            parts = []
            name = user.first_name or user.username
            parts.append(f"{name} is a backend developer experienced in {', '.join(top_skills) if top_skills else 'web development and backend systems'}.")
            if roles:
                parts.append("Recent roles: " + "; ".join(roles) + ".")
            if projects:
                parts.append("Recent projects: " + ", ".join(projects) + ".")
            return " ".join(parts)

        # If OpenAI available and key set, attempt improved summary
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                prompt = (
                    "Write a short (2-3 sentence) professional resume summary for a backend developer "
                    "given the following details. Use a confident, concise tone.\n\n"
                    f"Name: {request.user.first_name or request.user.username}\n"
                    f"Skills: {', '.join([s.name for s in resume.skills.all()[:10]])}\n"
                    f"Top Projects: {', '.join([p.title for p in resume.projects.all()[:5]])}\n"
                    f"Recent Roles: {', '.join([f'{e.role} at {e.company}' for e in resume.experiences.all()[:3]])}\n\n"
                    "Summary:"
                )
                # Use completion call depending on openai client version
                if hasattr(openai, "ChatCompletion"):
                    # for new OpenAI package
                    resp = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=120,
                        n=1,
                    )
                    summary_text = resp.choices[0].message.content.strip()
                else:
                    resp = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=prompt,
                        max_tokens=120,
                        n=1,
                    )
                    summary_text = resp.choices[0].text.strip()

                if summary_text:
                    resume.summary_text = summary_text
                    resume.save()
                    return Response({'summary': summary_text}, status=status.HTTP_200_OK)
            except Exception:
                # if anything fails, fallback to rule-based summary (do not crash)
                pass

        # fallback
        summary = rule_based_summary(request.user, resume)
        resume.summary_text = summary
        resume.save()
        return Response({'summary': summary}, status=status.HTTP_200_OK)


#
# Child viewsets and fix to permission handling (use DRF exceptions)
#
class BaseChildViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(resume__owner=self.request.user)

    def perform_create(self, serializer):
        resume = serializer.validated_data.get('resume')
        if resume.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only add items to your own resumes.")
        serializer.save()


class ProjectViewSet(BaseChildViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ExperienceViewSet(BaseChildViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer

class EducationViewSet(BaseChildViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer

class SkillViewSet(BaseChildViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class AchievementViewSet(BaseChildViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


#
# Webhook integration endpoint
#
class IntegrationWebhookAPIView(APIView):
    """
    POST /api/integrations/webhook/
    Secure with HEADER: X-WEBHOOK-SECRET: <secret>
    Payload example:
    {
      "source":"hackathon_platform",
      "external_id":"hack_2025_12345",
      "type":"achievement",   # or "project"
      "data":{
         "title":"1st Prize - SmartResume Hack",
         "description":"Built a resume auto-generator",
         "date":"2025-10-15",
         "proof_url":"https://.../submission/123"
      },
      "target_resume_id": 1
    }
    The endpoint will attempt to attach the incoming data to the resume (create Achievement or Project).
    """

    permission_classes = (AllowAny,)  # we'll validate secret manually

    def post(self, request, *args, **kwargs):
        secret = request.headers.get('X-WEBHOOK-SECRET') or request.headers.get('X-Webhook-Secret')
        if not secret or secret != settings.WEBHOOK_SECRET:
            raise PermissionDenied("Invalid webhook secret")

        payload = request.data
        required_keys = ('source', 'external_id', 'type', 'data', 'target_resume_id')
        if not all(k in payload for k in required_keys):
            raise ParseError("Missing required fields in payload")

        target_id = payload.get('target_resume_id')
        try:
            resume = Resume.objects.get(pk=target_id)
        except Resume.DoesNotExist:
            raise NotFound("Target resume not found")

        # ensure resume owner exists but we do not require caller to be that owner
        # map types
        type_ = payload.get('type').lower()
        data = payload.get('data') or {}

        if type_ == 'achievement':
            ach = Achievement.objects.create(
                resume=resume,
                title=data.get('title', 'Achievement'),
                description=data.get('description', ''),
                issuer=data.get('issuer', '') or payload.get('source', ''),
                proof_url=data.get('proof_url', None),
                date=data.get('date', None) or None
            )
            serializer = AchievementSerializer(ach)
            return Response({'status': 'ok', 'created': 'achievement', 'item': serializer.data}, status=status.HTTP_201_CREATED)

        elif type_ == 'project':
            proj = Project.objects.create(
                resume=resume,
                title=data.get('title', 'Project'),
                description=data.get('description', ''),
                tech_stack=data.get('tech_stack', ''),
                link=data.get('link', None),
            )
            serializer = ProjectSerializer(proj)
            return Response({'status': 'ok', 'created': 'project', 'item': serializer.data}, status=status.HTTP_201_CREATED)

        else:
            # unsupported type -> create an Achievement as generic fallback
            ach = Achievement.objects.create(
                resume=resume,
                title=data.get('title', f'Imported from {payload.get("source")}'),
                description=str(data),
            )
            serializer = AchievementSerializer(ach)
            return Response({'status': 'ok', 'created': 'achievement_fallback', 'item': serializer.data}, status=status.HTTP_201_CREATED)


#
# Simple PDF export view
#
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resume_pdf_view(request, pk):
    """
    Return a simple PDF of the resume with basic fields.
    GET /api/resumes/{id}/export_pdf/
    """
    resume = get_object_or_404(Resume, pk=pk, owner=request.user)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, resume.title)
    y -= 25
    p.setFont("Helvetica", 12)
    p.drawString(40, y, f"Owner: {request.user.get_full_name() or request.user.username}")
    y -= 25

    if resume.summary_text:
        p.setFont("Helvetica-Oblique", 11)
        p.drawString(40, y, "Summary:")
        y -= 18
        text = p.beginText(40, y)
        text.setFont("Helvetica", 10)
        for line in resume.summary_text.splitlines():
            text.textLine(line)
            y -= 14
        p.drawText(text)
        y = text.getY() - 10

    # Projects
    projs = resume.projects.all()[:6]
    if projs:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(40, y, "Projects:")
        y -= 18
        p.setFont("Helvetica", 10)
        for pr in projs:
            p.drawString(50, y, f"- {pr.title} ({pr.tech_stack})")
            y -= 14
            if y < 80:
                p.showPage()
                y = height - 50

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename=resume_{resume.id}.pdf'
    })
