# resumes/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Resume, Project, Experience, Education, Skill, Achievement
from .serializers import (ResumeSerializer, ProjectSerializer,
                          ExperienceSerializer, EducationSerializer,
                          SkillSerializer, AchievementSerializer)
from .permissions import IsOwnerOrReadOnly

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        # only return resumes belonging to current user
        return Resume.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_summary(self, request, pk=None):
        """
        Simple rule-based summary generator (Day 2: basic).
        We'll extend this in Day 3 with better rules or optional AI.
        """
        resume = self.get_object()
        # collect top skills and projects
        skills_qs = resume.skills.all()[:6]
        skills = [s.name for s in skills_qs]
        proj_qs = resume.projects.all()[:3]
        projects = [p.title for p in proj_qs]

        summary = (
            f"{request.user.first_name or request.user.username} is a backend developer "
            f"experienced in {', '.join(skills) if skills else 'web development'}. "
        )
        if projects:
            summary += "Recent projects: " + ", ".join(projects) + "."

        resume.summary_text = summary
        resume.save()
        return Response({'summary': summary}, status=status.HTTP_200_OK)

#
# Child viewsets: filter by resume ownership; require 'resume' field on create/update but validate owner
#

class BaseChildViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        # restrict to objects whose resume owner == request.user
        qs = super().get_queryset()
        return qs.filter(resume__owner=self.request.user)

    def perform_create(self, serializer):
        # ensure resume belongs to user
        resume = serializer.validated_data.get('resume')
        if resume.owner != self.request.user:
            raise PermissionError("You can only add items to your own resumes.")
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
