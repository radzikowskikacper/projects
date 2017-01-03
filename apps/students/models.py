from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from projects_helper.apps.common.models import *


class Student(models.Model):
    user = models.OneToOneField('common.CAS_User',
                                verbose_name=_('user'),
                                primary_key=True)
    team = models.ForeignKey('common.Team',
                             verbose_name=_('team'),
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)

    class Meta:
        ordering = ['user__username']
        verbose_name = _('student')
        verbose_name_plural = _('students')

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

    def new_team(self, selectedCourse):
        if not self.team.is_locked:
            team = Team(course=Course.objects.get(code=selectedCourse))
            team.save()
            self.join_team(team)

    def join_team(self, team):
        if not self.team.is_locked and not team.is_full:
            self.team = team

    def save(self, *args, **kwargs):
        if self.team_id is None:
            self.team = Team.objects.create()
        return super(Student, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # self.user.delete()
        Team.remove_empty()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        return self.user.username


# when removing multiple students or lecturers from the admin site, post_delete signals
# have to be catched and CustomUsers related to those users has to be deleted,
# because 'delete' method of Student/Lecturer isnt called in this case

@receiver(post_delete, sender=Student)
def post_delete_user_after_stud(sender, instance, *args, **kwargs):
    if instance.user is not None:  # just in case user is not specified or already deleted
     #       instance.user.delete()
        pass
    Team.remove_empty()
