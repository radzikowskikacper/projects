from django.contrib import admin
from django.contrib.auth.models import *
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from .models import *
from projects_helper.apps.students.models import *
from projects_helper.apps.lecturers.models import *
from django.utils.translation import ugettext_lazy as _


class CASUserAdmin(UserAdmin):
    model = CAS_User

    fieldsets = (
        (None, {'fields': ('user_type',)}),
    ) + UserAdmin.fieldsets
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_superuser')


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = ('__str__', 'team_count', 'team_assigned', 'lecturer', 'course')
    search_fields = ['title', 'lecturer__user__first_name', 'lecturer__user__last_name']

    def team_count(self, obj):
        return obj.team_set.count()
    team_count.short_description = _("Teams with preference")


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ('__str__', 'project_preference',
                    'project_assigned', 'get_lecturer', 'course')
    search_fields = ['project_preference__title', 'course__name', 'course__code']

    def get_lecturer(self, obj):
        if obj.project_preference:
            return obj.project_preference.lecturer
    get_lecturer.short_description = _("Lecturer")


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ('code', 'name', 'project_count', 'team_count', 'lecturer_count')
    search_fields = ['name']

    def project_count(self, obj):
        return obj.project_set.count()
    project_count.short_description = _("Projects")

    def team_count(self, obj):
        return obj.team_set.count()
    team_count.short_description = _("Teams")

    def lecturer_count(self, obj):
        return obj.project_set.order_by('lecturer__user_id').distinct('lecturer').count()
    lecturer_count.short_description = _("Lecturers")


class LecturerAdmin(admin.ModelAdmin):
    model = Course
    list_display = ('__str__', 'project_count', 'team_count', 'is_superuser')
    search_fields = ['user__first_name', 'user__last_name']

    def project_count(self, obj):
        return obj.project_set.count()
    project_count.short_description = _("Projects")

    def team_count(self, obj):
        return Team.objects.filter(project_preference__lecturer=obj).count()
    team_count.short_description = _("Teams")

    def is_superuser(self, obj):
        if obj.user.is_superuser:
            return _("Yes")
    is_superuser.short_description = _("Administrator")


class StudentAdmin(admin.ModelAdmin):
    model = Student
    list_display = ('__str__', 'teams_count', 'courses_count')
    search_fields = ['user__first_name', 'user__last_name']

    def teams_count(self, obj):
        return obj.teams.count()
    teams_count.short_description = _("Teams")

    def courses_count(self, obj):
        return obj.teams.order_by('course_id').distinct('course').count()
    courses_count.short_description = _("Courses")


admin.site.register(CAS_User, CASUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(Group)
