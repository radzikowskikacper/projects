from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from projects_helper.apps.common.models import Project, Team, Course
from django.core.exceptions import ObjectDoesNotExist


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
    course = get_object_or_404(
        Course, code__iexact=request.session['selectedCourse'])
    proj_pk = request.POST.get('to_pick', False)
    if not request.user.student.team:
        request.user.student.new_team(course)
        request.user.student.save()
    team = request.user.student.team
    if proj_pk:
        try:
            project_picked = Project.objects.get(pk=proj_pk)
        except ObjectDoesNotExist as e:
            print(str(e))
        if not project_picked.lecturer:
            messages.info(request,
                          _("Project " + project_picked.title +
                            " doesn't have any assigned lecturer. " +
                            " You can't pick that project right now."))

        elif project_picked.lecturer.max_students_reached():
            messages.info(request,
                          _("Max number of students who can be assigned " +
                            "to this lecturer has been reached. " +
                            "Choose project from another lecturer."))
        elif project_picked.status() == "free" and not team.is_locked:
            team.select_preference(project_picked)
            team.set_course(course)
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
                           _("You can't pick project: " +
                             "project already assigned"))

    return redirect(reverse('students:project_list',
                            kwargs={'course_code':
                                    request.session['selectedCourse']}))


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
    projects = Project.objects.select_related('lecturer') \
                      .prefetch_related('team_set') \
                      .filter(course=course)
    return render(request,
                  template_name="students/project_list.html",
                  context={"projects": projects,
                           "team": request.user.student.team,
                           "project_picked": request.user.student
                                                    .project_preference,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_student)
def team_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    teams = Team.objects.filter(course=course) \
                .exclude(project_preference__isnull=True) \
                .annotate(num_stud=Count('student')) \
                .order_by('-num_stud')
    return render(request,
                  template_name="students/team_list.html",
                  context={"teams": teams,
                           "student_team": request.user.student.team,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_student)
def filtered_project_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    query = request.GET.get('title')
    filtered_projects = Project.objects \
        .select_related('lecturer') \
        .complex_filter(
            Q(title__icontains=query) |
            Q(lecturer__user__last_name__icontains=query)
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
            messages.info(request,
                          _("Max number of students who can be assigned " +
                            "to this lecturer has been reached. " +
                            "Choose project from another lecturer."))
        else:
            student.leave_team()
            student.join_team(team)
            student.save()
            messages.success(request,
                             _("You have successfully joined selected team "))

    return redirect(reverse('students:team_list',
                            kwargs={'course_code':
                                    request.session['selectedCourse']}))


@login_required
@user_passes_test(is_student)
def new_team(request):
    course = get_object_or_404(
        Course, code__iexact=request.session['selectedCourse'])
    student = request.user.student
    old_team = student.team
    old_preference = None
    if old_team:
        old_preference = old_team.project_preference
    try:
        student.leave_team()
        student.new_team(course)
        student.team.select_preference(old_preference)
        student.team.save()
        student.save()
    except Exception as e:
        print(str(e))
    if request.method == 'POST':
        messages.success(request,
                         _("You have successfully left the team. " +
                           "Your project preference has not changed. " +
                           "If you want to change it, choose another project."))
    return redirect(reverse('students:team_list',
                            kwargs={'course_code':
                                    request.session['selectedCourse']}))
