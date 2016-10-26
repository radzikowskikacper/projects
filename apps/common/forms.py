from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from registration.forms import RegistrationForm
from django.forms.fields import *  # NOQA

from projects_helper.apps.common.models import CustomUser


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
