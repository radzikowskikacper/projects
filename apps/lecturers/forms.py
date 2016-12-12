from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import ModelForm

from projects_helper.apps.common.models import Project
from django.utils.translation import ugettext_lazy as _


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']
        required_css_class = 'required'
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _("%(model_name)s's %(field_labels)s are not unique."),
            }
        }
