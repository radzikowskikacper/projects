from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..projects.models import Project

class Team(models.Model):
    project_preference = models.ForeignKey('projects.Project',
                                           verbose_name=_('project preference'),
                                           null=True,
                                           blank=True,
                                           on_delete=models.SET_NULL,)
    course = models.ForeignKey('courses.Course',
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
    def member_count(self):
        return self.student_set.count()

    @property
    def is_full(self):
        return self.student_set.count() == 2

    @property
    def is_locked(self):
        return self.project_assigned is not None

    @property
    def team_members(self):
        return self.student_set.all()

    @staticmethod
    def remove_empty():
        for team in Team.objects.all():
            if team.student_set.count() == 0:
                team.delete()

    def __str__(self):
        tmp_str = ""
        for student in self.student_set.all().order_by('user__last_name'):
            if tmp_str != "":
                tmp_str += ", "
            tmp_str += student.user.last_name

        if tmp_str == "":
            return "Team " + str(self.pk)
        else:
            return tmp_str
