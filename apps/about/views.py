from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from projects_helper.apps.students.views import is_student
from projects_helper.apps.lecturers.views import is_lecturer
from projects_helper.apps.common.models import Course


def info(request):
    context = {
        "basetemplate" : "common/base.html",
        "selectedCourse" : None
    }

    if request.user.is_authenticated():
        # redirect when user logged in but hasn't choosed course yet
        if 'selectedCourse' not in request.session:
            return redirect(reverse('common:select_course'))

        if is_student(request.user):
            context["basetemplate"] = "students/base.html"
        elif is_lecturer(request.user):
            context["basetemplate"] = "lecturers/base.html"

        course = get_object_or_404(
            Course, code__iexact=request.session['selectedCourse'])
        context["selectedCourse"] = course

    return render(request, 'about.html', context=context)
