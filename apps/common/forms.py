from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from registration.forms import RegistrationForm
from django.forms import Form, RadioSelect
from django.forms.fields import *  # NOQA

from projects_helper.apps.common.models import Course


class CustomRegistrationForm(RegistrationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()

    user_type = ChoiceField(
        choices=(
            ('S', 'Student'),
            ('L', 'Lecturer'),
        ),
        label='User type',
    )

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user

# this callable will be necessary to avoid executing queries
# at the time this models.py is imported
def get_course_set():
    return Course.objects.all()

class CourseSelectorForm(Form):
    selection = ChoiceField(
        choices=[(c.code, c.name) for c in get_course_set()],
        label='',
        widget=RadioSelect(attrs={'onclick': 'form.submit()'})
        )
