from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import ListView

from projects_helper.apps.common.models import Project, Student, Team
from projects_helper.apps.students import is_student


@login_required
@user_passes_test(is_student)
def profile(request):
    student = Student.objects.get(pk=request.user.pk)
    project_assigned = student.team.project_assigned
    if project_assigned is not None:
        messages.info(request, "You are already assigned to project.")
        messages.info(request, "You can't switch project preference.")
        messages.info(request, "You can't switch or create new team.")
    return render(request,
                  "students/profile.html",
                  {'user': request.user,
                   'student': student})


@login_required
@user_passes_test(is_student)
def pick_project(request):
    student = Student.objects.get(user=request.user)
    team = student.team
    proj_pk = request.POST.get('to_pick', False)
    if proj_pk:
        project_picked = Project.objects.get(pk=proj_pk)
        if project_picked.status() == "free" and not team.is_locked:
            team.select_preference(project_picked)
            team.save()
            messages.success(request,
                             "You have successfully picked project " +
                             project_picked.title)
        elif project_picked.status() != "free":
            messages.error(request,
                           "Project " + project_picked +
                           " is already occupied," +
                           " you can't pick that project")
        elif team.is_locked:
            messages.error(request,
                           "You can't pick project: project already assigned")

    return redirect(reverse('students:project_list'))


@login_required
@user_passes_test(is_student)
def project(request, project_pk):
    proj = Project.objects.get(pk=project_pk)
    return render(request,
                  context={'project': proj},
                  template_name='students/project_detail.html')


class ListProjects(ListView, LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_student(self.request.user)

    model = Project
    template_name = "students/project_list.html"
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super(ListProjects, self).get_context_data(**kwargs)
        student = Student.objects.get(user=self.request.user)
        context["student"] = student
        context['team'] = student.team
        context['project_picked'] = student.project_preference
        return context


class ListTeams(ListView, LoginRequiredMixin, UserPassesTestMixin):
        def test_func(self):
            return is_student(self.request.user)

        model = Team
        template_name = "students/team_list.html"
        context_object_name = 'teams'

        def get_context_data(self, **kwargs):
            context = super(ListTeams, self).get_context_data(**kwargs)
            student = Student.objects.get(user=self.request.user)
            context['student_team'] = student.team
            context['student'] = student
            return context

@login_required
@user_passes_test(is_student)
def filtered_project_list(request):
    query = request.GET.get('query')
    student = Student.objects.get(user=request.user)
    filtered_projects = Project.objects.complex_filter(
        Q(title__contains=query) |
        Q(lecturer__user__username__contains=query) |
        Q(lecturer__user__email__contains=query)
    )

    return render(request,
                  template_name="students/project_list.html",
                  context={"projects": filtered_projects,
                           "student": student,
                           "student_team": student.team})



@login_required
@user_passes_test(is_student)
def join_team(request):
    team_pk = request.POST.get('to_join', False)
    if team_pk:
        team = Team.objects.get(pk=team_pk)
        student = Student.objects.get(user=request.user)
        student.join_team(team)
        student.save()
        Team.remove_empty()


    return redirect(reverse('students:team_list'))


@login_required
@user_passes_test(is_student)
def new_team(request):
    student = Student.objects.get(user=request.user)
    student.new_team()
    student.save()
    Team.remove_empty()
    return redirect(reverse('students:team_list'))