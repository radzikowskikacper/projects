from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from projects_helper.apps.students.models import Student
from django.contrib.auth.models import User

class Lecturer(models.Model):
    user = models.OneToOneField(User,
                                verbose_name=_('user'),
                                primary_key=True)
    max_students = models.IntegerField(verbose_name=_('students limit'),
                                       default=20,
                                       null=True)

    class Meta:
        ordering = ['user__username']
        verbose_name = _('lecturer')
        verbose_name_plural = _('lecturers')

    def __str__(self):
        return self.user.get_full_name()

    def max_students_reached(self):
        assigned_students = Student.objects.filter(
            teams__project_preference__lecturer=self).count()
        return assigned_students >= self.max_students

    def delete(self, *args, **kwargs):
        # self.user.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


# when removing multiple lecturers from the admin site, post_delete signals
# have to be catched and CustomUsers related to those users has to be deleted,
# because 'delete' method of Lecturer isnt called in this case

@receiver(post_delete, sender=Lecturer)
def post_delete_user_after_lect(sender, instance, *args, **kwargs):
    if instance.user is not None:  # just in case user is not specified or already deleted
     #       instance.user.delete()
        pass
