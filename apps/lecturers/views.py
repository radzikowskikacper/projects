from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404

from projects_helper.apps.common.models import Project, Course, Team
from projects_helper.apps.lecturers import is_lecturer
from projects_helper.apps.lecturers.forms import ProjectForm


@login_required
@user_passes_test(is_lecturer)
def profile(request):
    return render(request,
                  "lecturers/profile.html",
                  {'selectedCourse': request.session['selectedCourse']})

@login_required
@user_passes_test(is_lecturer)
def project_list(request):
    course = Course.objects.get(name=request.session['selectedCourse'])
    projects = Project.objects.filter(lecturer=request.user.lecturer).filter(course=course)
    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": projects,
                           "selectedCourse": course})

@login_required
@user_passes_test(is_lecturer)
def filtered_project_list(request):
    title = request.GET.get('title')
    course = Course.objects.get(name=request.session['selectedCourse'])
    projects = Project.objects.filter(lecturer=request.user.lecturer).filter(course=course)

    filtered_projects = projects.filter(
        title__icontains=title
    )
    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": filtered_projects,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_lecturer)
def project(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    course = Course.objects.get(name=request.session['selectedCourse'])
    return render(request, "lecturers/project_detail.html",
                  context={'project': proj,
                           'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def project_delete(request):
    projects_to_delete = Project.objects.filter(pk__in=request.POST.getlist('to_delete'))

    for proj in projects_to_delete:
        if proj.lecturer.user == request.user:
            if proj.status() == 'free':
                proj.delete()
            else:
                messages.error(request, _("Cannot delete occupied project: ") + proj.title)
        else:
            messages.error(request, _("Cannot delete project: " + proj.title + " - access denied"))
    return redirect(reverse('lecturers:project_list'))


@login_required
@user_passes_test(is_lecturer)
def project_new(request):
    course = Course.objects.get(name=request.session['selectedCourse'])
    if request.method == 'POST':
        form = ProjectForm(request.POST)
    else:
        form = ProjectForm()
    if form.is_valid():
        try:
            proj = form.save(commit=False)
            proj.lecturer = request.user.lecturer
            proj.course = Course.objects.get(name=request.session['selectedCourse'])
            proj.save()
        except IntegrityError:
            messages.error(request, _("\n You must provide unique project name"))
            return render(request, "lecturers/project_new.html",
                          context={'form': form,
                                    'selectedCourse': course})

        messages.info(request, _("You have succesfully added new project: ") + proj.title)
        return redirect(reverse('lecturers:project_list'))
    return render(request, "lecturers/project_new.html",
                  context={'form': form,
                            'selectedCourse': course})

@login_required
@user_passes_test(is_lecturer)
def team_list(request):
    course = Course.objects.get(name=request.session['selectedCourse'])
    teams = Team.objects.filter(project_preference__lecturer=request.user.lecturer).filter(course=course).exclude(project_preference__isnull=True)
    return render(request,
                  template_name="lecturers/team_list.html",
                  context={"teams": teams,
                           "selectedCourse": course})

@login_required
@user_passes_test(is_lecturer)
def team_delete(request):
    teams_to_delete = Team.objects.filter(pk__in=request.POST.getlist('to_delete'))

    for team in teams_to_delete:
        if team.project_preference.lecturer.user == request.user:
            if team.is_locked == False:
                team.delete()
            else:
                messages.error(request, _("Cannot delete assigned team: ") + str(team))
        else:
            messages.error(request, _("Cannot delete team: " + str(team) + " - access denied"))
    return redirect(reverse('lecturers:team_list'))

@login_required
@user_passes_test(is_lecturer)
def assign_team(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    if proj.lecturer.user == request.user:
        if proj.teams_with_preference().count() == 0:
            messages.error(request, _("Cannot assign: No teams waiting for project"))
        else:
            proj.assign_random_team()
    else:
        messages.error(request, _("Cannot assign: access denied"))

    return redirect(reverse_lazy('lecturers:project', kwargs={'project_pk': proj.pk}))


@login_required
@user_passes_test(is_lecturer)
def modify_project(request, project_pk):
    proj = get_object_or_404(Project, pk=project_pk)
    form = ProjectForm(request.POST or None, instance=proj)
    course = Course.objects.get(name=request.session['selectedCourse'])
    if form.is_valid():
        if proj.lecturer == request.user.lecturer:
            form.save()
            messages.info(request, _("You have successfully updated project:") + proj.title)
        else:
            messages.error(request, _("Access denied"))
        return redirect(reverse("lecturers:modify_project", kwargs={'project_pk': proj.pk}))
    return render(request, "lecturers/project_modify.html",
                  context={'form': form,
                           'project': proj,
                           'selectedCourse': course})
