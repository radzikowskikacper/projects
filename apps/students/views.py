from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from projects_helper.apps.common.models import Project, Team, Course
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
import logging


## Instantiating module's logger.
logger = logging.getLogger('projects_helper.apps.lecturers.views')


def is_student(user):
    return user.user_type == 'S'


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def profile(request):
    if 'selectedCourse' not in request.session:
        return redirect(reverse('common:select_course'))
    course = get_object_or_404(
        Course, code__iexact=request.session['selectedCourse'])
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        print(request.META.get('HTTP_X_FORWARDED_FOR'))
    return render(request,
                  "students/profile.html",
                  {'selectedCourse': course})


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def pick_project(request):
    if request.method == 'POST':
        course = get_object_or_404(
            Course, code__iexact=request.session['selectedCourse'])
        proj_pk = request.POST.get('to_pick', False)
        if not request.user.student.team:
            try:
                request.user.student.new_team(course)
                request.user.student.save()
            except Exception as e:
                logger.error("Cannot set Student's team. " + str(e))
        team = request.user.student.team
        if proj_pk:
            try:
                project_picked = Project.objects.get(pk=proj_pk)
            except ObjectDoesNotExist as e:
                logger.error('Exception:' + str(e))
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
                try:
                    team.select_preference(project_picked)
                    team.set_course(course)
                    team.save()
                except Exception as e:
                    logger.error("Student cannot pick project. " + str(e))
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
    else:
        logger.error('Bad request: Only POST requests are allowed.')

    return redirect(reverse('students:project_list',
                            kwargs={'course_code':
                                    request.session['selectedCourse']}))


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def project(request, project_pk, course_code=None):
    proj = get_object_or_404(Project, pk=project_pk)
    course = get_object_or_404(Course, code__iexact=course_code)
    return render(request,
                  context={'project': proj,
                           'selectedCourse': course},
                  template_name='students/project_detail.html')


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
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
@ensure_csrf_cookie
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
@ensure_csrf_cookie
def filtered_project_list(request, course_code=None):
    if request.method == 'GET' and 'title' in request.GET:
        course = get_object_or_404(Course, code__iexact=course_code)
        query = request.GET.get('title')
        filtered_projects = Project.objects \
            .select_related('lecturer') \
            .complex_filter(
                Q(title__icontains=query) |
                Q(lecturer__user__last_name__icontains=query)
            )

        context = {
            "projects": filtered_projects,
            "team": request.user.student.team,
            "project_picked": request.user.student.project_preference,
            "selectedCourse": course
        }

        if request.is_ajax():
            return HttpResponse(render_to_string("students/project_table.html",
                                                 context=context))
        else:
            return render(request,
                          template_name="students/project_list.html",
                          context=context)
    else:
        logger.error('Bad request: Only GET requests are allowed. %s' %
                     request.build_absolute_uri())
        raise Http404


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def join_team(request):
    if request.method == 'POST':
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
    else:
        logger.error('Bad request: Only POST requests are allowed.')

    return redirect(reverse('students:team_list',
                            kwargs={'course_code':
                                    request.session['selectedCourse']}))


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
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
        logger.error('Exception: ' + str(e))
    if request.method == 'POST':
        messages.success(request,
                         _("You have successfully left the team. " +
                           "Your project preference has not changed. " +
                           "If you want to change it, choose another project."))
    return redirect(reverse('students:team_list',
                            kwargs={'course_code':
                                    request.session['selectedCourse']}))
