from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from registration.backends.simple.views import RegistrationView

from projects_helper.apps import students
from projects_helper.apps import lecturers
from projects_helper.apps.common.forms import CustomRegistrationForm
from .models import *


@sensitive_post_parameters()
@csrf_protect
@never_cache
def user_login(request):
    if request.method == 'GET':
        return auth.views.login(request,
                                template_name="common/login_form.html")
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if students.is_student(user):
                return redirect('students:profile')
            elif lecturers.is_lecturer(user):
                return redirect('lecturers:profile')
            else:
                messages.error(request, "Invalid login details supplied.")
                return redirect('common:login')
        else:
            messages.error(request, "Invalid login details supplied.")
            return redirect('common:login')
    else:
        return render(request, '404.html')


class CustomRegistrationView(RegistrationView):
    template_name = 'common/registration_form.html'

    def get_form_class(self):
        return CustomRegistrationForm

    def register(self, form):
        new_user = super(CustomRegistrationView, self).register(form)
        if students.is_student(new_user):
            Student.objects.create(user=new_user)
        if lecturers.is_lecturer(new_user):
            Lecturer.objects.create(user=new_user)

        return new_user

    def get_success_url(self, new_user):
        if students.is_student(new_user):
            return 'students:profile'
        elif lecturers.is_lecturer(new_user):
            return 'lecturers:profile'



