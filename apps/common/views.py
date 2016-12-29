from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from projects_helper.apps.students.views import is_student
from projects_helper.apps.lecturers.views import is_lecturer
from .forms import CourseSelectorForm
from django.urls import reverse


def redirect_user(user, course_code=None):
    if is_student(user):
        return redirect(reverse('students:project_list', kwargs={'course_code': course_code}))
    elif is_lecturer(user):
        return redirect(reverse('lecturers:project_list', kwargs={'course_code': course_code}))

@csrf_protect
@login_required
def course_selection(request):
    if request.method == 'POST':
        form = CourseSelectorForm(request.POST)
        if form.is_valid():
            course_code = request.session['selectedCourse'] = form.cleaned_data.get('selection')
            return redirect_user(request.user, course_code)
    else:
        form = CourseSelectorForm()
        # skip course selection when there is only 1 course
        if len(form.fields['selection'].choices) == 1:
            # retrieve first tuple item (Course code attr) from first (and only) item on the choice list
            course_code = request.session['selectedCourse'] = form.fields['selection'].choices[0][0]
            return redirect_user(request.user, course_code)

    return render(request, 'common/course_selection_form.html', {'form': form})


