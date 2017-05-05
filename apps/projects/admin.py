from django.utils.translation import ugettext_lazy as _
from .models import Project
from django.contrib import admin

class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = ('__str__', 'team_count', 'team_assigned', 'lecturer', 'course')
    search_fields = ['title', 'lecturer__user__first_name', 'lecturer__user__last_name']

    def team_count(self, obj):
        return obj.team_set.count()
    team_count.short_description = _("Teams with preference")

admin.site.register(Project, ProjectAdmin)
