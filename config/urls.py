"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from resumes.views import (ResumeViewSet, ProjectViewSet, ExperienceViewSet,
                           EducationViewSet, SkillViewSet, AchievementViewSet)
from users.views import RegisterAPIView, MeAPIView

from resumes.views import (ResumeViewSet, ProjectViewSet, ExperienceViewSet,
                           EducationViewSet, SkillViewSet, AchievementViewSet,
                           IntegrationWebhookAPIView)
from resumes.views import (
                           ResumeViewSet, ProjectViewSet, ExperienceViewSet,
                           EducationViewSet, SkillViewSet, AchievementViewSet,
                           IntegrationWebhookAPIView, resume_pdf_view)


router = routers.DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'experiences', ExperienceViewSet, basename='experience')
router.register(r'educations', EducationViewSet, basename='education')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'achievements', AchievementViewSet, basename='achievement')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # auth
    path('api/auth/register/', RegisterAPIView.as_view(), name='auth-register'),
    path('api/auth/me/', MeAPIView.as_view(), name='auth-me'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API schema / docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # webhook integrations endpoint
    path('api/integrations/webhook/', IntegrationWebhookAPIView.as_view(), name='integration-webhook'),
    path('api/resumes/<int:pk>/export_pdf/', resume_pdf_view, name='resume-export-pdf'),

]
