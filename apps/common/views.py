from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from projects_helper.apps import students, lecturers
from .forms import CourseSelectorForm


@csrf_protect
@login_required
def course_selection(request):
    if request.method == 'POST':
        form = CourseSelectorForm(request.POST)
        if form.is_valid():
            request.session['selectedCourse'] = form.cleaned_data.get('selection')
            user = request.user
            if students.is_student(user):
                return redirect('/students/projects')
            elif lecturers.is_lecturer(user):
                return redirect('/lecturers/projects')
    else:
        form = CourseSelectorForm()

    return render(request, 'common/course_selection_form.html', {'form': form})


