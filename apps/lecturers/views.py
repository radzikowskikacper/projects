from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404

from projects_helper.apps.common.models import Project, Course, Team
from projects_helper.apps.lecturers.forms import ProjectForm


def is_lecturer(user):
    return user.user_type == "L" or user.is_superuser


@login_required
@user_passes_test(is_lecturer)
def profile(request):
    course = get_object_or_404(
        Course, code__iexact=request.session['selectedCourse'])
    return render(request,
                  "lecturers/profile.html",
                  {'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def project_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.filter(
        lecturer=request.user.lecturer).filter(course=course)
    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": projects,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_lecturer)
def filtered_project_list(request, course_code=None):
    title = request.GET.get('title')
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.filter(
        lecturer=request.user.lecturer).filter(course=course)
    filtered_projects = projects.filter(title__icontains=title)

    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": filtered_projects,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_lecturer)
def project(request, project_pk, course_code=None):
    proj = Project.objects.get(pk=project_pk)
    course = get_object_or_404(Course, code__iexact=course_code)
    return render(request, "lecturers/project_detail.html",
                  context={'project': proj,
                           'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def project_delete(request):
    projects_to_delete = Project.objects.filter(
        pk__in=request.POST.getlist('to_delete'))

    for proj in projects_to_delete:
        if proj.lecturer.user == request.user:
            if proj.status() == 'free':
                proj.delete()
            else:
                messages.info(request, _(
                    "Cannot delete occupied project: ") + proj.title)
        else:
            messages.error(request,
                           _("Cannot delete project: " + proj.title + " - access denied"))
    return redirect(reverse('lecturers:project_list',
                            kwargs={'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_lecturer)
def project_new(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    form = ProjectForm(request.POST or None)
    context = {
        'form': form,
        'selectedCourse': course
    }

    if form.is_valid():
        try:
            proj = form.save(commit=False)
            proj.lecturer = request.user.lecturer
            proj.course = course
            proj.save()
        except IntegrityError:
            messages.error(request, _(
                "\n You must provide unique project name"))
            return render(request, "lecturers/project_new.html", context)

        messages.success(request, _(
            "You have succesfully added new project: ") + proj.title)
        return redirect(reverse('lecturers:project_list',
                                kwargs={'course_code': course_code}))

    # GET
    return render(request, "lecturers/project_new.html", context)


@login_required
@user_passes_test(is_lecturer)
def modify_project(request, project_pk, course_code=None):
    proj = get_object_or_404(Project, pk=project_pk)
    form = ProjectForm(request.POST or None, instance=proj)
    course = get_object_or_404(Course, code__iexact=course_code)

    if form.is_valid():
        try:
            form.save()
        except IntegrityError:
            messages.error(request, _(
                "\n You must provide unique project name"))
            return redirect(reverse("lecturers:modify_project",
                                    kwargs={'project_pk': proj.pk,
                                            'course_code': course_code}))

        messages.success(request, _(
            "You have successfully updated project: ") + proj.title)
        return redirect(reverse('lecturers:project_list',
                                kwargs={'course_code': course_code}))

    return render(request, "lecturers/project_modify.html",
                  context={'form': form,
                           'project': proj,
                           'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def project_copy(request, project_pk, course_code=None):
    new_proj = get_object_or_404(Project, pk=project_pk)
    new_proj.pk = None  # autogen a new pk
    new_proj.title = new_proj.title + " - " + str(_("copy"))
    form = ProjectForm(request.POST or None, instance=new_proj)
    course = get_object_or_404(Course, code__iexact=course_code)
    context = {
        'form': form,
        'selectedCourse': course
    }

    if form.is_valid():
        try:
            form.save()
        except IntegrityError:
            messages.error(request, _(
                "\n You must provide unique project name"))
            return render(request, "lecturers/project_new.html", context)

        messages.success(request, _(
            "You have succesfully added new project: ") + new_proj.title)
        return redirect(reverse('lecturers:project_list',
                                kwargs={'course_code': course_code}))

    return render(request, "lecturers/project_new.html", context)


@login_required
@user_passes_test(is_lecturer)
def team_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    teams = Team.objects.filter(project_preference__lecturer=request.user.lecturer).filter(
        course=course).exclude(project_preference__isnull=True)
    return render(request,
                  template_name="lecturers/team_list.html",
                  context={"teams": teams,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_lecturer)
def team_delete(request):
    teams_to_delete = Team.objects.filter(
        pk__in=request.POST.getlist('to_delete'))

    for team in teams_to_delete:
        if team.project_preference.lecturer.user == request.user:
            if team.is_locked == False:
                messages.success(request, _(
                    "You have succesfully deleted team: ") + str(team))
                team.delete()
            else:
                messages.info(request, _(
                    "Cannot delete assigned team: ") + str(team))
        else:
            messages.error(request, _("Cannot delete team: " +
                                      str(team) + " - access denied"))
    return redirect(reverse('lecturers:team_list',
                            kwargs={'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_lecturer)
def assign_team(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    if proj.lecturer.user == request.user:
        if proj.teams_with_preference().count() == 0:
            messages.error(request, _(
                "Cannot assign: No teams waiting for project"))
        else:
            proj.assign_random_team()
            messages.success(request, _(
                "You have successfully assigned team: " +
                str(proj.team_assigned) + " to project: " + str(proj)))
    else:
        messages.error(request, _("Cannot assign: access denied"))

    return redirect(reverse_lazy('lecturers:project',
                                 kwargs={'project_pk': proj.pk,
                                         'course_code': request.session['selectedCourse']}))


@login_required
@user_passes_test(is_lecturer)
def assign_teams_to_projects(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.filter(
        lecturer=request.user.lecturer).filter(course=course)
    if projects:
        for proj in projects:
            proj.assign_random_team()
        messages.success(request, _(
            "You have successfully assigned teams to projects"))
    else:
        messages.info(request, _("You haven't got any projects"))
    return redirect(reverse('lecturers:project_list',
                            kwargs={'course_code': course_code}))


@login_required
@user_passes_test(is_lecturer)
def unassign_team(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    if proj.lecturer.user == request.user:
        proj.team_assigned = None
        proj.save()
        messages.success(request, _(
            "You have successfully unassigned team from project: ") + str(proj))
    return redirect(reverse_lazy('lecturers:project',
                                 kwargs={'project_pk': proj.pk,
                                         'course_code': request.session['selectedCourse']}))
