from django.contrib import admin
from .models import Team
from django.utils.translation import ugettext_lazy as _

class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ('__str__', 'project_preference',
                    'project_assigned', 'get_lecturer', 'course')
    search_fields = ['project_preference__title', 'course__name', 'course__code']

    def get_lecturer(self, obj):
        if obj.project_preference:
            return obj.project_preference.lecturer
    get_lecturer.short_description = _("Lecturer")

admin.site.register(Team, TeamAdmin)
