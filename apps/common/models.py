from enum import Enum

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from random import randint


class Team(models.Model):
    project_preference = models.ForeignKey('common.Project',
                                           null=True,
                                           blank=True)

    def select_preference(self, project):
        if not self.is_locked:
            self.project_preference = project
        else:
            self.project_preference = self.project_assigned

    @property
    def project_assigned(self):
        try:
            project = Project.objects.get(team_assigned=self)
            return project
        except models.ObjectDoesNotExist:
            return None

    @property
    def students_in_team(self):
        return self.student_set.all()

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
            if len(team.students_in_team) == 0:
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
    title = models.CharField(max_length=255)
    description = models.TextField()

    lecturer = models.ForeignKey('common.Lecturer',
                                 on_delete=models.CASCADE)
    team_assigned = models.OneToOneField('common.Team',
                                         null=True,
                                         blank=True)

    class Meta:
        unique_together = ('lecturer', 'title',)

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


class CustomUser(AbstractUser):
    type_choices = (
        ('SU', 'SuperUser'),
        ('S', 'Student'),
        ('L', 'Lecturer'),
    )
    user_type = models.CharField(max_length=2,
                                 choices=type_choices,
                                 default='SU')


class Student(models.Model):
    user = models.OneToOneField(CustomUser,
                                primary_key=True)
    team = models.ForeignKey('common.Team',
                             blank=True)

    @property
    def is_assigned_to_project(self):
        val = self.project_assigned is not None
        return val

    @property
    def project_assigned(self):
        return self.team.project_assigned

    @property
    def project_preference(self):
        return self.team.project_preference

    def new_team(self):
        if not self.team.is_locked:
            team = Team()
            team.save()
            self.join_team(team)

    def join_team(self, team):
        if not self.team.is_locked and not team.is_full:
            self.team = team

    def save(self, *args, **kwargs):
        if self.team_id is None:
            self.team = Team.objects.create()
        return super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class Lecturer(models.Model):
    user = models.OneToOneField(CustomUser,
                                primary_key=True)

    def __str__(self):
        return self.user.username
