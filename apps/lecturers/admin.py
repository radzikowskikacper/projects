from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Lecturer
from ..teams.models import Team

class LecturerAdmin(admin.ModelAdmin):
    model = Lecturer
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

admin.site.register(Lecturer, LecturerAdmin)
