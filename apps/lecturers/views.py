from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404, HttpResponse
from django.http import Http404, StreamingHttpResponse
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

from django.forms import modelformset_factory
from ..courses.models import Course
from ..teams.models import Team
from ..projects.models import Project
from ..students.models import Student
from ..students.views import is_student
from ..files.models import File
from ..users.forms import ProjectFilterForm
from ..lecturers.forms import ProjectForm, TeamForm, TeamModifyForm, UploadFileForm
from .models import Lecturer

from markdownx.utils import markdownify
from wsgiref.util import FileWrapper
import os, csv, logging

## Instantiating module's logger.
logger = logging.getLogger('projects_helper.apps.lecturers.views')


def is_lecturer(user):
    return hasattr(user, 'lecturer')


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def profile(request):
    if request.method == 'GET':
        if 'selectedCourse' not in request.session:
            return redirect(reverse('users:select_course'))
        course = get_object_or_404(
            Course, code__iexact=request.session['selectedCourse'])
        request.user.max_students = Lecturer.objects.get(user_id = request.user.id).max_students
        return render(request,
                      "lecturers/profile.html",
                      {'selectedCourse': course})
    elif request.method == 'POST':
        l = Lecturer.objects.get(user_id = request.user.id)
        l.max_students = request.POST.get('max_students')
        l.save()
        request.user.max_students = Lecturer.objects.get(user_id = request.user.id).max_students
        course = get_object_or_404(
            Course, code__iexact=request.session['selectedCourse'])

        messages.success(request, _(
            "You have successfully changed preferences"))

        return render(request,
                      "lecturers/profile.html",
                      {'selectedCourse': course})

@login_required
@user_passes_test(is_lecturer)
def project_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.filter(
        lecturer=request.user.lecturer, course=course)
    filter_form = ProjectFilterForm()
    file_upload_form = UploadFileForm()
    return render(request,
                  template_name="lecturers/project_list.html",
                  context={"projects": projects,
                           "filterForm": filter_form,
                           "fileUploadForm" : file_upload_form,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def filtered_project_list(request, course_code=None):
    if (request.method == 'GET') and ('title' in request.GET or 'filter' in request.GET):
        title = request.GET.get('title', None)
        filter_type = request.GET.get('filter', None)
        course = get_object_or_404(Course, code__iexact=course_code)
        projects = Project.objects.filter(
            lecturer=request.user.lecturer, course=course)
        filter_form = ProjectFilterForm(request.GET)

        filtered_projects = projects
        if filter_type:
            if filter_type == 'free':
                filtered_projects = projects.filter(team_assigned__isnull=True)
            elif filter_type == 'occupied':
                filtered_projects = projects.filter(team_assigned__isnull=False)
            elif filter_type == 'has_teams':
                filtered_projects = projects.filter(team__isnull=False)
        if title:
            filtered_projects = filtered_projects.filter(title__icontains=title)

        context = {
            "projects": filtered_projects,
            "filterForm": filter_form,
            "selectedCourse": course,
            "user": request.user
        }

        if request.is_ajax():
            return HttpResponse(render_to_string("lecturers/project_table.html",
                                                 context=context))
        else:
            return render(request,
                          template_name="lecturers/project_list.html",
                          context=context)
    else:
        logger.error('Bad request: Only GET requests are allowed. %s' %
                     request.build_absolute_uri())
        raise Http404


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def project(request, project_pk, course_code=None):
    proj = Project.objects.get(pk=project_pk)
    course = get_object_or_404(Course, code__iexact=course_code)
    proj.description = markdownify(proj.description)
    files = File.objects.filter(project = proj, team = proj.team_assigned) if proj.status() == 'occupied' else []
    return render(request, 'lecturers/project_detail.html',
                  context={'project': proj, 'selectedCourse': course, 'files' : files})

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
                "You must provide unique project name"))
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
def team_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    vacancies = Project.objects.filter(course=course, lecturer=request.user.lecturer).count() * 2

    try:
        my_teams = Team.objects\
            .filter(course=course, project_preference__lecturer=request.user.lecturer)
        teams_with_no_project = Team.objects.filter(course=course, project_preference__isnull=True)
    except Exception as e:
        logger.error(str(e))

    student_count = 0
    for t in my_teams:
        student_count += t.member_count

    return render(request,
                  template_name="lecturers/team_list.html",
                  context={"teams": my_teams,
                           "teams_with_no_project": teams_with_no_project,
                           "vacancies" : vacancies,
                           "students" : student_count,
                           "selectedCourse": course})

@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def assign_selected_team(request, project_pk, team_pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_pk, lecturer=request.user.lecturer)
        team = get_object_or_404(Team, pk=team_pk)

        project.assign_team(team)
        project.save()
        messages.success(request, _(
            "You have successfully assigned team: " +
            str(team) + " to project: " + str(project)))

    return redirect('lecturers:project',
                    project_pk=project.pk,
                    course_code=request.session['selectedCourse'])


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def assign_team(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, lecturer=request.user.lecturer)

    if project.teams_with_preference().count() == 0:
        messages.error(request, _(
            "Cannot assign: No teams waiting for project"))
    else:
        project.assign_random_team()
        messages.success(request, _(
            "You have successfully assigned team: " +
            str(project.team_assigned) + " to project: " + str(project)))

    return redirect('lecturers:project',
                    project_pk=project.pk,
                    course_code=request.session['selectedCourse'])


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def unassign_team(request, project_pk):
    proj = get_object_or_404(Project, pk=project_pk, lecturer=request.user.lecturer)
    proj.team_assigned = None
    proj.save()
    messages.success(request, _(
        "You have successfully unassigned team from project: ") + str(proj))
    return redirect('lecturers:project',
                    project_pk=proj.pk,
                    course_code=request.session['selectedCourse'])

@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def manage_projects(request):
    if request.method == 'POST':
        chosen_projects = get_list_or_404(Project,
                                          pk__in=request.POST.getlist('to_change'),
                                          lecturer=request.user.lecturer)
        if 'duplicate' in request.POST:
            for proj in chosen_projects:
                if proj.lecturer.user == request.user:
                    proj.title += ' - copy'
                    proj.pk = None
                    proj.team_assigned = None
                    if not Project.objects.filter(title=proj.title).exists():
                        proj.save()
                    else:
                        messages.error(request, 'Project ' + proj.title + ' already exists')

        elif 'delete' in request.POST:
            for proj in chosen_projects:
                if proj.status() == 'free':
                    proj.delete()
                else:
                    messages.info(request, _(
                        "Cannot delete occupied project: ") + proj.title)

        return redirect('lecturers:project_list',
                        course_code=request.session['selectedCourse'])
    else:
        raise Http404

@login_required
@user_passes_test(is_lecturer)
def team_new(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    if request.method == 'POST':
        form = TeamForm(request.POST, course=course, lecturer=request.user.lecturer)

        if form.is_valid():
            stud_1 = form.cleaned_data['member_1']
            next_stud = form.cleaned_data['next_stud_check']
            stud_2 = form.cleaned_data['member_2']
            project_check = form.cleaned_data['project_check']
            proj = form.cleaned_data['project']
            try:
                with transaction.atomic():
                    new_team = Team.objects.create(course=course)
                    if project_check and proj:
                        new_team.select_preference(proj)
                        new_team.save()
                        proj.assign_team(new_team)
                        proj.save()
                    # Student's method 'leave_team' not used below
                    # because project assignment override is possible
                    stud_1_team = stud_1.team(course)
                    if stud_1_team and (stud_1_team.team_members.count() == 1):
                        stud_1_team.delete()
                    stud_1.teams.add(new_team)
                    stud_1.save()
                    if next_stud and stud_2:
                        stud_2_team = stud_2.team(course)
                        if stud_2_team and (stud_2_team.team_members.count() == 1):
                            stud_2_team.delete()
                        stud_2.teams.add(new_team)
                        stud_2.save()

            except Exception as e:
                messages.error(request, _(
                    "Something went wrong. Try again."))
                return render(request, "lecturers/team_new.html", context)

            messages.success(request, _(
                "You have succesfully added new team: ") + str(new_team))
            return redirect('lecturers:team_list',
                            course_code=course_code)

    # GET
    else:
        form = TeamForm(course=course, lecturer=request.user.lecturer)

    return render(request, "lecturers/team_new.html",
                           {'form': form,
                           'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
def modify_team(request, team_pk, course_code=None):
    team = get_object_or_404(Team, pk=team_pk)
    course = get_object_or_404(Course, code__iexact=course_code)

    if request.method == 'POST':
        form = TeamModifyForm(request.POST,
                              course=course,
                              lecturer=request.user.lecturer,
                              team=team)
    else:
        form = TeamModifyForm(course=course,
                              lecturer=request.user.lecturer,
                              team=team)

    if form.is_valid():
        stud_1 = form.cleaned_data['member_1_select']
        stud_2 = form.cleaned_data['member_2_select']
        proj = form.cleaned_data['project_select']
        change_member_1 = form.cleaned_data['change_member_1']
        change_member_2 = form.cleaned_data['change_member_2']
        change_project = form.cleaned_data['change_project']
        members = team.team_members
        try:
            deleted_count = 0
            with transaction.atomic():
                if not team.course:
                    team.course = course
                    team.save()
                if change_member_1:
                    if members and (stud_1 not in members):
                        team.student_set.remove(members[0])
                        if stud_1:
                            stud_1_team = stud_1.team(course)
                            if stud_1_team and (stud_1_team.team_members.count() == 1):
                                stud_1_team.delete()
                            team.student_set.add(stud_1)
                        else:
                            members[0].new_team(course)
                            deleted_count += 1
                if change_member_2:
                    if stud_2 not in members:
                        if len(members) > 1:
                            team.student_set.remove(members[1])
                        if stud_2:
                            stud_2_team = stud_2.team(course)
                            if stud_2_team and (stud_2_team.team_members.count() == 1):
                                stud_2_team.delete()
                            team.student_set.add(stud_2)
                        else:
                            members[1].new_team(course)
                            deleted_count += 1
                if len(members) <= deleted_count:
                    if deleted_count == 2:
                        messages.success(request, 'You have successfully deleted team: ' + str(team))
                    team.delete()
                    return redirect('lecturers:team_list',
                                    course_code=course_code)

                if change_project:
                    if team.project_assigned != proj:
                        if team.project_assigned:
                            project_to_unassign = team.project_assigned
                            project_to_unassign.assign_team(None)
                        if proj:
                            proj.assign_team(team)

        except Exception as e:
            logger.error("Exception: " + str(e))
            messages.error(request, _(
                "Something went wrong. Try again."))
            return redirect('lecturers:team_list',
                            course_code=course_code)

        messages.success(request, 'You have successfully updated team: ' + str(team))
        return redirect('lecturers:team_list',
                        course_code=course_code)

    return render(request, 'lecturers/team_modify.html',
                  context={'form': form,
                           'team': team,
                           'selectedCourse': course})


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def team_delete(request):
    if request.method == 'POST':
        teams_to_delete = Team.objects.filter(
            pk__in=request.POST.getlist('to_delete'))

        for team in teams_to_delete:
            if team.project_preference is None \
                    or (team.project_preference.lecturer.user == request.user):
                messages.success(request, _(
                    "You have succesfully deleted team: ") + str(team))
                team.delete()
            else:
                messages.error(request, _("Cannot delete team: " + str(team) +
                                                             " - access denied"))
        return redirect('lecturers:team_list',
                        course_code=request.session['selectedCourse'])
    else:
        logger.error('Bad request: Only POST requests are allowed.')
        raise Http404

@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def assign_teams_to_projects(request, course_code):
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.filter(
        lecturer=request.user.lecturer, course=course)
    team_count = len([t for t in Team.objects.filter(course=course) if t.project_assigned==None])

    if projects:
        count = 0
        for proj in projects:
            if proj.assign_random_team():
                count += 1
            else:
                break

        messages.success(request, _(
            "Assigned {} of {} teams".format(count ,team_count)))
    else:
        messages.info(request, _("You don't have any projects"))
    return redirect('lecturers:project_list',
                    course_code=course_code)

@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def assign_all_teams(request, project_pk):
    project = Project.objects.get(
        lecturer=request.user.lecturer, id = project_pk)
    project.assign_all_teams()
    messages.success(request, _(
            "Assigned all teams"))
    return redirect('lecturers:project_list')

@login_required
@user_passes_test(is_lecturer)
def course_manage(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    CourseFormSet = modelformset_factory(Course,
                                         fields=('name', 'code',),
                                         extra=1,
                                         can_delete=True)
    formset = CourseFormSet(request.POST or None,)
                            #queryset=Course.objects.all())
    context = {
        'formset': formset,
        'selectedCourse': course
    }

    if request.method == 'POST':
        if formset.is_valid():
            try:
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.save()
                del_count = 0
                for instance in formset.deleted_objects:
                    if request.user.is_superuser \
                        or ((instance.project_set.all().count() == 0)
                            and (instance.team_set.all().count() == 0)):
                        instance.delete()
                        del_count += 1
            except IntegrityError as e:
                logger.error("Cannot save Course. " + str(e))
                messages.error(request, _(
                    "You must provide unique course name and course code"))
                return render(request, "lecturers/course_manage.html", context)

            ch_count = len(formset.changed_objects)
            new_count = len(formset.new_objects)
            if del_count > 0:
                messages.success(request, _(
                    "You have succesfully deleted {} courses")
                    .format(str(del_count)))
            if ch_count > 0:
                messages.success(request, _(
                    "You have succesfully modified {} courses")
                    .format(str(del_count + ch_count)))
            if new_count > 0:
                messages.success(request, _(
                    "You have succesfully added new course."))
            if del_count != len(formset.deleted_objects):
                messages.info(request, _(
                    "You don't have permission to delete course which" +
                    " has related projects/teams: ") + course.name)

        # if current course's code has been modified
        # or whole course has been deleted, remove course from cookie
        try:
            Course.objects.get(code__iexact=request.session['selectedCourse'])
        except ObjectDoesNotExist:
            request.session.pop('selectedCourse')

        return redirect('lecturers:profile')

    return render(request, "lecturers/course_manage.html", context)


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def clean_up(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    try:
        for team in course.team_set.filter(project_preference__lecturer=request.user.lecturer):
            team.delete()
    except Exception as e:
        logger.error("Exception: " + str(e))

    messages.success(request, _(
        "You have succesfully performed clean-up for current course."))

    return redirect('lecturers:profile')


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def export_students_to_file(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    file_name = 'studenci_{}.csv'.format(course.code)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-LIGHTTPD-send-file'] = smart_str(file_name)

    try:
        writer = csv.writer(response)
        course_info = [course.code, course.name]
        writer.writerow(course_info)
        writer.writerow([])
        headers = ['L.p.', 'Nazwisko', 'Imiona', 'Adres e-mail',
                   'Tytuł przypisanego projektu', 'Prowadzący']
        writer.writerow(headers)
        students = Student.objects \
            .filter(teams__course=course) \
            .order_by('user__last_name', 'user__first_name')

        for i, s in enumerate(students):
            stud_team = None
            proj_title = lect_name = ""
            stud_teams = s.teams.filter(course=course)
            if len(stud_teams) > 0:
                stud_team = stud_teams[0]
                if stud_team.project_assigned:
                    proj_title = stud_team.project_assigned.title
                    lect_name = str(stud_team.project_assigned.lecturer)
            row = [i + 1, s.user.last_name, s.user.first_name, s.user.email, proj_title, lect_name]
            writer.writerow(row)
    except Exception as e:
        logger.error("Exception: " + str(e))
        messages.error(request, _("There was an error while generating csv file."))
        return redirect('lecturers:profile')

    return response


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def export_teams_to_file(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    file_name = 'zespoly_{}.csv'.format(course.code)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-LIGHTTPD-send-file'] = smart_str(file_name)

    try:
        writer = csv.writer(response)
        course_info = [course.code, course.name]
        writer.writerow(course_info)
        writer.writerow([])
        headers = ['L.p.', 'Temat projektu', 'Prowadzący', 'Przypisany zespół']
        writer.writerow(headers)
        projects = Project.objects \
            .filter(course=course) \
            .order_by('lecturer__user__last_name', 'title')

        for i, p in enumerate(projects):
            stud_names = ''
            if p.team_assigned:
                team = p.team_assigned
                stud_names = ', '.join(['{} {} ({})'
                        .format(s.user.last_name, s.user.first_name, s.user.email) for s in team.team_members])
            row = [i + 1, p.title, p.lecturer.user.get_full_name(), stud_names]
            writer.writerow(row)
    except Exception as e:
        logger.error("Exception: " + str(e))
        messages.error(request, _("There was an error while generating csv file."))
        return redirect('lecturers:profile')

    return response

@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def save_projects_to_file(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    response = HttpResponse(content_type='text/utf-8')
    response['Content-Disposition'] = 'attachment; filename="{}_{}.txt"' \
                                        .format(request.user.last_name, course_code)

    for p in Project.objects.filter(lecturer=request.user.lecturer, course=course):
        response.write('{' + p.title + '}\n{' + p.description + '}\n')

    return response


@login_required
@user_passes_test(is_lecturer)
@ensure_csrf_cookie
def load_projects_from_file(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = iter((str(x, 'utf-8') for x in request.FILES['file'].readlines()))
            added_projects = 0
            for line in uploaded_file:
                title, description = '', ''
                if line.startswith('{') and line.endswith('}\n'):
                    title = line
                else:
                    messages.error(request, 'Error reading file - uncorrect format.')
                    break
                line = next(uploaded_file)
                if line.startswith('{'):
                    while not line.endswith('}\n'):
                        description += line
                        line = next(uploaded_file)
                    description += line
                else:
                    messages.error(request, 'Error reading file - uncorrect format.')
                    break

                if not Project.objects.filter(title=title[1:-2], course=course):
                    Project.objects.create(title=title[1:-2], description=description[1:-2],
                                       course=course, lecturer=request.user.lecturer)
                    added_projects += 1

            messages.success(request, 'Added ' + str(added_projects) + ' projects')

    return redirect('lecturers:project_list', course_code=course_code)

@login_required
@user_passes_test(lambda x: is_lecturer(x) or is_student(x))
@ensure_csrf_cookie
def handle_file(request, course_code, project_pk, file_id):
    file = File.objects.get(id = file_id,
                            project = Project.objects.get(id = project_pk, lecturer = request.user.lecturer))

    if request.method == 'GET':
        file_name = '{}_{}'.format(project_pk, file_id)

        with open(file_name, 'wb') as retfile:
            retfile.write(file.filedata)

        wrapper = FileWrapper(open(file_name, 'rb'))
        response = StreamingHttpResponse(wrapper, content_type='application/force-download')
        response['Content-Length'] = os.path.getsize(file_name)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(file.filename)
        os.remove(file_name)
        return response