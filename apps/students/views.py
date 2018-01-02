from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import Http404, StreamingHttpResponse
from django.utils.translation import ugettext_lazy as _
from ..courses.models import Course
from ..teams.models import Team
from ..projects.models import Project
from ..lecturers.models import Lecturer
from ..files.models import File
from .models import Student
from .forms import MyDescriptionForm
from projects_helper.apps.users.forms import ProjectFilterForm
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from markdownx.utils import markdownify
from wsgiref.util import FileWrapper
import logging, os


## Instantiating module's logger.
logger = logging.getLogger('projects_helper.apps.lecturers.views')

def is_student(user):
    return hasattr(user, 'student')


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def profile(request):
    if 'selectedCourse' not in request.session:
        return redirect(reverse('users:select_course'))
    course = get_object_or_404(
        Course, code__iexact=request.session['selectedCourse'])
    stud = Student.objects.get(pk=request.user.student.pk)
    proj_preference = stud.project_preference(course)
    proj_assigned = stud.project_assigned(course)
    team = stud.team(course)
    return render(request,
                  "students/profile.html",
                  {'selectedCourse': course,
                   'team': team,
                   'project_preference': proj_preference,
                   'project_assigned': proj_assigned,
                   'description' : request.user.student.description})

@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def profile_edit(request):
    if 'selectedCourse' not in request.session:
        return redirect(reverse('users:select_course'))
    course = get_object_or_404(
        Course, code__iexact=request.session['selectedCourse'])

    if request.method == 'POST':
        form = MyDescriptionForm(request.POST)
        if form.is_valid():
            student = Student.objects.get(pk=request.user.student.pk)
            student.description = form.cleaned_data['description']
            student.save()
            return redirect(reverse('students:profile'))
    else:
        form = MyDescriptionForm()
    return render(request, "students/profile_edit.html", {'description_form': form,
                                                          'selectedCourse' : course })

@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def pick_project(request):
    if request.method == 'POST':
        course = get_object_or_404(
            Course, code__iexact=request.session['selectedCourse'])
        proj_pk = request.POST.get('to_pick', False)
        team = request.user.student.team(course)
        if not team:
            try:
                team = request.user.student.new_team(course)
                request.user.student.save()
            except Exception as e:
                logger.error("Cannot set Student's team. " + str(e))

        if team and proj_pk:
            try:
                project_picked = Project.objects.get(pk=proj_pk)
            except ObjectDoesNotExist as e:
                logger.error('Exception:' + str(e))
            if not project_picked.lecturer:
                messages.info(request,
                              _("Project " + project_picked.title +
                                " doesn't have any assigned lecturer. " +
                                " You can't pick that project right now."))

            elif project_picked.status() == "free" and not team.is_locked:
                try:
                    team.select_preference(project_picked)
                    team.set_course(course)
                    team.save()
                except Exception as e:
                    logger.error("Student cannot pick project. " + str(e))

                if project_picked.lecturer.max_students_reached():
                    messages.info(request, _("Max number of students who can be assigned " +
                                            "to this lecturer has been reached. " +
                                            "Choose project from another lecturer."))
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
    project = get_object_or_404(Project, pk=project_pk)
    course = get_object_or_404(Course, code__iexact=course_code)
    project.description = markdownify(project.description)
    return render(request,
                  context={'project': project,
                           'selectedCourse': course},
                  template_name='students/project.html')

@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def project_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    projects = Project.objects.select_related('lecturer') \
                      .prefetch_related('team_set') \
                      .filter(course=course)
    lecturers = Lecturer.objects.filter(project__in=projects).distinct()

    lecturer_info = []
    for lecturer in lecturers:
        vacancies = projects.filter(lecturer=lecturer).count() * 2
        teams = Team.objects.filter(course=course, project_preference__lecturer=lecturer)

        student_count = 0
        for t in teams:
            student_count += t.member_count
        lecturer_info.append((lecturer, student_count, vacancies))

    for p in projects:
        p.description = markdownify(p.description)
        if p.status() == 'occupied' and p.team_assigned == request.user.student.team(course):
            p.files = File.objects.filter(project = p, team = p.team_assigned)

    filter_form = ProjectFilterForm()
    proj_preference = request.user.student.project_preference(course)
    return render(request,
                  template_name="students/project_list.html",
                  context={"projects": projects,
                           "lecturer_info": lecturer_info,
                           "filterForm": filter_form,
                           "team": request.user.student.team(course),
                           "project_picked": proj_preference,
                           "selectedCourse": course})


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def team_list(request, course_code=None):
    course = get_object_or_404(Course, code__iexact=course_code)
    teams = Team.objects.filter(course=course) \
                .annotate(num_stud=Count('student')) \
                .order_by('-num_stud')

    return render(request,
                  template_name="students/team_list.html",
                  context={"teams": teams,
                           "student_team": request.user.student.team(course),
                           "selectedCourse": course})


@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def filtered_project_list(request, course_code=None):
    if (request.method == 'GET') and ('title' in request.GET or 'filter' in request.GET):
        query = request.GET.get('title', None)
        filter_type = request.GET.get('filter', None)
        course = get_object_or_404(Course, code__iexact=course_code)
        projects = Project.objects.filter(course=course)
        filter_form = ProjectFilterForm(request.GET)

        filtered_projects = projects
        if filter_type:
            if filter_type == 'free':
                filtered_projects = projects.filter(team_assigned__isnull=True)
            elif filter_type == 'occupied':
                filtered_projects = projects.filter(team_assigned__isnull=False)
            elif filter_type == 'has_teams':
                filtered_projects = projects.filter(team__isnull=False)
        if query:
          filtered_projects = Project.objects \
              .select_related('lecturer') \
              .filter(course=course) \
              .complex_filter(
                  Q(title__icontains=query) |
                  Q(lecturer__user__last_name__icontains=query)
              )

        context = {
            "projects": filtered_projects,
            "filterForm": filter_form,
            "team": request.user.student.team(course),
            "project_picked": request.user.student.project_preference(course),
            "selectedCourse": course,
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

            course = get_object_or_404(
                Course, code__iexact=request.session['selectedCourse'])
            student.leave_team(student.team(course))
            student.join_team(team)
            student.save()

            if team.project_preference.lecturer.max_students_reached():
                messages.info(request,
                              _("Max number of students who can be assigned " +
                                "to this lecturer has been reached. " +
                                "Choose project from another lecturer."))
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
    old_team = student.team(course)
    old_preference = None
    if old_team:
        old_preference = old_team.project_preference
    try:
        student.leave_team(old_team)
        new_team = student.new_team(course)
        new_team.select_preference(old_preference)
        new_team.save()
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

@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def files(request, course_code, project_pk, file_id = None):
    if request.method == 'GET':
        with open('test', 'w') as tt:
            tt.write('a')
            file = File.objects.get(id=file_id,
                                    team = request.user.student.team(Course.objects.get(code = course_code)))
            tt.write('b')
            file_name = '{}_{}'.format(project_pk, file_id)
            tt.write('c')

            with open(file_name, 'wb') as retfile:
                retfile.write(bytearray(file.filedata))
            tt.write('d')

            wrapper = FileWrapper(open(file_name))
            tt.write('e')
            response = StreamingHttpResponse(wrapper, content_type='application/force-download')
            tt.write('f')
            response['Content-Length'] = os.path.getsize(file_name)
            tt.write('g')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(file.filename)
            tt.write('h')

            os.remove(file_name)
            tt.write('i')
            return response

    elif request.method == 'POST':
        if file_id is None:
            File.objects.create(team = request.user.student.team(Course.objects.get(code = course_code)),
                                filename = 'a.txt', filedata = request.FILES['fileToUpload'].read(),
                                project = Project.objects.get(id = project_pk))
            return HttpResponse(status=200)

    elif request.method == 'DELETE':
        file = File.objects.get(id=file_id,
                                team = request.user.student.team(Course.objects.get(code = course_code)))

        file.delete()
        return HttpResponse(status=200)

@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def upload_file(request):
    project_id = 0
    team_id = 0

    filedata = request.FILES['image_path'].read()
    filename = ''
    File.objects.create(filedata = filedata, filename = filename, project = project_id, team = team_id)

@login_required
@user_passes_test(is_student)
@ensure_csrf_cookie
def delete_file(request):
    file_id = 0
    File.objets.get(id = file_id).delete()