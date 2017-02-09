from django.forms import Form, RadioSelect
from django.forms.fields import *  # NOQA
from projects_helper.apps.common.models import Course


# this callable will be necessary to avoid executing queries
# at the time this models.py is imported
def get_course_set():
    return Course.objects.all()


class CourseSelectorForm(Form):
    selection = ChoiceField(
        choices=[],
        label='',
        widget=RadioSelect(attrs={'onclick': 'form.submit()'})
    )

    def __init__(self, *args, **kwargs):
        super(CourseSelectorForm, self).__init__(*args, **kwargs)
        self.fields['selection'].choices = \
            [(c.code, '[' + c.code + '] ' + c.name) for c in get_course_set()]
