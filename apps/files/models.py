from django.db import models
from random import randint
from django.utils.translation import ugettext_lazy as _
from markdownx.models import MarkdownxField

class File(models.Model):
    filedata = models.BinaryField()

    filename = models.CharField(verbose_name=_('filename'), max_length=255)

    project = models.ForeignKey('projects.Project',
                               verbose_name=_('project'),
                               null=True,
                               blank=False)

    team = models.OneToOneField('teams.Team',
                                         verbose_name=_('team'),
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         blank=True)

    class Meta:
        unique_together = ['team', 'project']