from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Course

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

admin.site.register(Course, CourseAdmin)
