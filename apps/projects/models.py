from django.db import models
from random import randint
from django.utils.translation import ugettext_lazy as _
from markdownx.models import MarkdownxField

class Project(models.Model):
    title = models.CharField(verbose_name=_('title'), max_length=255)

    description = MarkdownxField(verbose_name=_('desciption'))

    course = models.ForeignKey('courses.Course',
                               verbose_name=_('course'),
                               null=True,
                               blank=False)
    lecturer = models.ForeignKey('lecturers.Lecturer',
                                 verbose_name=_('lecturer'),
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=False)
    team_assigned = models.OneToOneField('teams.Team',
                                         verbose_name=_('team assigned'),
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         blank=True)

    class Meta:
#        unique_together = ('lecturer', 'title', 'course')
        ordering = ['lecturer', 'course', 'title']
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def teams_with_preference(self):
        return self.team_set.all()

    def status(self):
        if self.team_assigned is None:
            return "free"
        else:
            return "occupied"

    def assign_team(self, team):
        self.team_assigned = team
        self.save()

    def assign_random_team(self):
        teams = list(self.teams_with_preference().filter(project=None))
        full_teams = [x for x in teams if x.is_full]
        if len(full_teams) > 0:
            teams = full_teams
        if len(teams) > 0:
            random_idx = randint(0, len(teams) - 1)
            self.team_assigned = teams[random_idx]
            try:
                self.save()
                return True
            except Exception as e:
                logger.error("Project cannot be saved. " + str(e))
        return False

    def __str__(self):
        return self.title
