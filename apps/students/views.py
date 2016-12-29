from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from projects_helper.apps.common.models import Project, Team, Course


def is_student(user):
    return user.user_type == 'S'


@login_required
@user_passes_test(is_student)
def profile(request):
    course = get_object_or_404(
        Course, code__iexact=request.session['selectedCourse'])
    return render(request,
                  "students/profile.html",
                  {'selectedCourse': course})


@login_required
@user_passes_test(is_student)
def pick_project(request):
    team = request.user.student.team
    proj_pk = request.POST.get('to_pick', False)
    if proj_pk:
        project_picked = Project.objects.get(pk=proj_pk)
        if not project_picked.lecturer:
            messages.error(request,
                           _("Project " + project_picked.title +
                             " doesn't have any assigned lecturer. " +
                             " You can't pick that project right now."))

        elif project_picked.lecturer.max_students_reached():
            messages.error(request,
                           _("Max number of students who can be assigned " +
                             "to this lecturer has been reached. " +
                             "Choose project from another lecturer."))
        elif project_picked.status() == "free" and not team.is_locked:
            team.select_preference(project_picked)
            team.set_course(Course.objects.get(
                name=request.session['selectedCourse']))
            team.save()
            messages.success(request,
                             _("You have successfully picked project ") +
                             project_picked.title)
        elif project_picked.status() != "free":
            messages.error(request,
                           _("Project " + project_picked +
                             " is already occupied," +
                             " you can't pick that project"))
        elif team.is_locked:
            messages.error(request,
                           _("You can't pick project: project already assigned"))

    return redirect(reverse('students:project_list',
                            kwargs={'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_student)
def project(request, project_pk, course_code=None):
    proj = Project.objects.get(pk=project_pk)
    course = get_object_or_404(Course, code__iexact=course_code)
    return render(request,
                  context={'project': proj,
                           'selectedCourse': course},
                  template_name='students/project_detail.html')


@login_required
@user_passes_test(is_student)
def project_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.select_related('lecturer').filter(course=course)
    return render(request,
                  template_name="students/project_list.html",
                  context={"projects": projects,
                           "team": request.user.student.team,
                           "project_picked": request.user.student.project_preference,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_student)
def team_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    teams = Team.objects.filter(course=course).exclude(
        project_preference__isnull=True)
    return render(request,
                  template_name="students/team_list.html",
                  context={"teams": teams,
                           "student_team": request.user.student.team,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_student)
def filtered_project_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    query = request.GET.get('query')
    filtered_projects = Project.objects.select_related('lecturer').complex_filter(
        Q(title__icontains=query) |
        Q(lecturer__user__username__contains=query) |
        Q(lecturer__user__email__contains=query)
    )

    return render(request,
                  template_name="students/project_list.html",
                  context={"projects": filtered_projects,
                           "student_team": request.user.student.team,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_student)
def join_team(request):
    team_pk = request.POST.get('to_join', False)
    if team_pk:
        team = Team.objects.get(pk=team_pk)
        student = request.user.student
        if team.project_preference.lecturer.max_students_reached():
            messages.error(request,
                           _("Max number of students who can be assigned " +
                             "to this lecturer has been reached. " +
                             "Choose project from another lecturer."))
        else:
            student.join_team(team)
            student.save()
            Team.remove_empty()
            messages.success(request,
                             _("You have successfully joined selected team "))

    return redirect(reverse('students:team_list',
                            kwargs={'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_student)
def new_team(request):
    student = request.user.student
    was_empty_team = student.team.project_preference is None
    student.new_team(request.session['selectedCourse'])
    student.save()
    Team.remove_empty()
    if request.method == 'POST' and not was_empty_team:
        messages.success(request,
                         _("You have successfully left the team "))
    return redirect(reverse('students:team_list',
                            kwargs={'course_code': request.session['selectedCourse']}))
