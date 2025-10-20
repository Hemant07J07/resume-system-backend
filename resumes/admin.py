# resumes/admin.py
from django.contrib import admin
from .models import Resume, Project, Experience, Education, Skill, Achievement

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'title', 'last_updated')
    search_fields = ('owner__username', 'title')

admin.site.register(Project)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Achievement)
