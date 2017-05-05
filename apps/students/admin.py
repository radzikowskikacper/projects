from django.contrib import admin
from .models import Student
from django.utils.translation import ugettext_lazy as _

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

admin.site.register(Student, StudentAdmin)
