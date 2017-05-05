from django.db import models
from django.utils.translation import ugettext_lazy as _

class Course(models.Model):
    name = models.CharField(verbose_name=_('name'),
                            max_length=255,
                            unique=True)
    code = models.CharField(verbose_name=_('code'),
                            default='',
                            max_length=6,
                            blank=False,
                            unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def __str__(self):
        return self.name
