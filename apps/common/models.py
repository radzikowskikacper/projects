from django.contrib.auth.models import AbstractUser
from django.db import models
from random import randint
from django.utils.translation import ugettext_lazy as _


class CAS_User(AbstractUser):
    type_choices = (
        ('SU', 'SuperUser'),
        ('S', 'Student'),
        ('L', 'Lecturer'),
        ('N', 'New'),
    )
    user_type = models.CharField(verbose_name=_('user type'),
                                 max_length=2,
                                 choices=type_choices,
                                 default='N')

class Course(models.Model):
    name = models.CharField(verbose_name=_('name'),
                            max_length=255,
                            primary_key=True)
    code = models.CharField(verbose_name=_('code'),
                            default='',
                            max_length=6,
                            blank=False)

    class Meta:
        ordering = ['name']
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def __str__(self):
        return self.name


class Team(models.Model):
    project_preference = models.ForeignKey('common.Project',
                                           verbose_name=_('project preference'),
                                           null=True,
                                           blank=True)
    course = models.ForeignKey('common.Course',
                               verbose_name=_('course'),
                               null=True,
                               blank=False)

    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    def select_preference(self, project):
        if not self.is_locked:
            self.project_preference = project
        else:
            self.project_preference = self.project_assigned

    def set_course(self, course):
        self.course = course

    @property
    def project_assigned(self):
        try:
            project = Project.objects.get(team_assigned=self)
            return project
        except models.ObjectDoesNotExist:
            return None

    @property
    def is_full(self):
        return len(self.student_set.all()) == 2

    @property
    def is_locked(self):
        val = self.project_assigned is not None
        return val

    @property
    def team_members(self):
        return self.student_set.all()

    @staticmethod
    def remove_empty():
        for team in Team.objects.all():
            if len(team.team_members) == 0:
                team.delete()

    def __str__(self):
        tmp_str = ""
        for student in self.student_set.all().order_by('user__username'):
            if tmp_str != "":
                tmp_str += ", "
            tmp_str += student.user.username

        if tmp_str == "":
            return "Team " + str(self.pk)
        else:
            return tmp_str


class Project(models.Model):
    title = models.CharField(verbose_name=_('title'), max_length=255)
    description = models.TextField(verbose_name=_('desciption'))

    course = models.ForeignKey('common.Course',
                               verbose_name=_('course'),
                               null=True,
                               blank=False)
    lecturer = models.ForeignKey('lecturers.Lecturer',
                                 verbose_name=_('lecturer'),
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=False)
    team_assigned = models.OneToOneField('common.Team',
                                         verbose_name=_('team assigned'),
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         blank=True)

    class Meta:
        unique_together = ('lecturer', 'title',)
        ordering = ['lecturer', 'course', 'title']
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def teams_with_preference(self):
        return Team.objects.filter(project_preference=self)

    def status(self):
        if self.team_assigned is None:
            return "free"
        else:
            return "occupied"

    def assign_random_team(self):
        teams = list(self.teams_with_preference().filter(project=None))
        full_teams = [x for x in teams if x.is_full]
        if len(full_teams) > 0:
            teams = full_teams
        if len(teams) > 0:
            random_idx = randint(0, len(teams) - 1)
            self.team_assigned = teams[random_idx]
            self.save()

    def __str__(self):
        return self.title
