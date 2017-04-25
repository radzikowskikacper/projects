from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from projects_helper.apps.students.views import is_student
from projects_helper.apps.lecturers.views import is_lecturer
from projects_helper.apps.common.forms import CourseSelectorForm
from projects_helper.apps.common.models import Course
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
import logging


## Instantiating module's logger.
logger = logging.getLogger('projects_helper.apps.common.views')


def generate_context(request):
    context = {
        'basetemplate': "common/base.html",
        'selectedCourse': None
    }
    if (request.user.is_authenticated()) and ('selectedCourse' in request.session):
        if is_student(request.user):
            context['basetemplate'] = "students/base.html"
        elif is_lecturer(request.user):
            context['basetemplate'] = "lecturers/base.html"

        context['selectedCourse'] = get_object_or_404(
            Course, code__iexact=request.session['selectedCourse'])
    return context


def check_for_cookie(request):
    if request.user.is_authenticated():
        # redirect when user logged in but hasn't choosed course yet
        if 'selectedCourse' not in request.session:
            redirect(reverse('common:select_course'))


@ensure_csrf_cookie
def home(request, course_code=None):
    check_for_cookie(request)
    return render(request, 'common/welcome.html', context=generate_context(request))


@ensure_csrf_cookie
def redirect_user(request, user, course_code=None):
    if is_student(user):
        return redirect(reverse('students:project_list', kwargs={'course_code': course_code}))
    elif is_lecturer(user):
        return redirect(reverse('lecturers:project_list', kwargs={'course_code': course_code}))

    # when user was recognized by the CAS server,
    # BUT his account could not be created in backends.py
    else:
        messages.error(request,
            _('Error: Your account type cannot be recognized by the service. Please contact administrator.'))
        return redirect(reverse('common:welcome'))


@csrf_protect
@login_required
def course_selection(request):
    context = generate_context(request)
    if request.method == 'POST':
        form = CourseSelectorForm(request.POST)
        if form.is_valid():
            course_code = request.session['selectedCourse'] = form.cleaned_data.get('selection')
            return redirect_user(request, request.user, course_code)
    else:
        form = CourseSelectorForm()
        # skip course selection when there is only 1 course
        if len(form.fields['selection'].choices) == 1:
            # retrieve first tuple item (Course code attr) from first (and only) item on the choice list
            course_code = request.session['selectedCourse'] = form.fields['selection'].choices[0][0]
            return redirect_user(request, request.user, course_code)

    context['form'] = form
    return render(request, 'common/course_selection_form.html', context=context)
