from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from ..teams.models import Team

class Student(models.Model):
    user = models.OneToOneField(User,
                                verbose_name=_('user'),
                                primary_key=True)
    teams = models.ManyToManyField('teams.Team',
                                   verbose_name=_('teams'),
                                   blank=True)

    description = models.CharField(max_length=1023,
                                   verbose_name=_('description'))

    class Meta:
        ordering = ['user__username']
        verbose_name = _('student')
        verbose_name_plural = _('students')

    def team(self, selectedCourse):
        try:
            return self.teams.get(course=selectedCourse)
        except models.ObjectDoesNotExist:
            return None

    def project_assigned(self, selectedCourse):
        if (not self.teams) or (not self.teams.filter(course=selectedCourse).exists()):
            return None
        return self.teams.get(course=selectedCourse).project_assigned

    def project_preference(self, selectedCourse):
        if (not self.teams) or (not self.teams.filter(course=selectedCourse).exists()):
            return None
        return self.teams.get(course=selectedCourse).project_preference

    def new_team(self, selectedCourse):
        if (not self.teams) or (not self.team(selectedCourse)) or (not self.team.is_locked):
            team = Team(course=selectedCourse)
            team.save()
            self.join_team(team)
            return team
        else:
            return None

    def join_team(self, team):
        if (not self.teams) or (not team.is_locked and not team.is_full):
            self.teams.add(team)

    def leave_team(self, team):
        if self.teams and team and (not team.is_locked):
            if team.team_members.count() == 1:
                team.delete()
            else:
                self.teams.remove(team)

    def save(self, *args, **kwargs):
        if self.teams is None:
            self.teams.create()
        return super(Student, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # self.user.delete()
        Team.remove_empty()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()


# when removing multiple students or lecturers from the admin site, post_delete signals
# have to be catched and CustomUsers related to those users has to be deleted,
# because 'delete' method of Student/Lecturer isnt called in this case

@receiver(post_delete, sender=Student)
def post_delete_user_after_stud(sender, instance, *args, **kwargs):
    if instance.user is not None:  # just in case user is not specified or already deleted
     #       instance.user.delete()
        pass
    Team.remove_empty()
