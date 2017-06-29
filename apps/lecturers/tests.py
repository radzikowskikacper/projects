from django.test import TestCase
from ..courses.models import Course
from ..teams.models import Team
from ..students.models import Student
from ..projects.models import Project
from .models import Lecturer
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class LecturerTest(TestCase):

    def setUp(self):
        user = User.objects.create_user('test1', 'test1@test.pl', 'test')
        lecturer = Lecturer.objects.create(user=user)
        self.client.login(username='test1', password='test')

        #course
        self.code = 'TC'
        self.course = Course.objects.create(name='Test Course', code=self.code)
        self.kwargs = {'course_code' : self.code}

        #project
        self.project = Project.objects.create(pk=2, title='Test Project', course=self.course, lecturer=lecturer)

    def set_session(self):
        session = self.client.session
        session['selectedCourse'] = self.code
        session.save()

    def test_profile1(self):
        res = self.client.get(reverse('lecturers:profile'))
        self.assertEqual(res.status_code, 302)

    def test_profile2(self):
        self.set_session()
        res = self.client.get(reverse('lecturers:profile'))
        self.assertEqual(res.status_code, 200)

    def test_filtered_project_list(self):
        res = self.client.get(reverse('lecturers:filtered_project_list', kwargs={'course_code' : 'TC'}), data={'title':'Test Project','filter':'free'})
        self.assertEqual(res.status_code, 200)

    def test_project(self):
        res = self.client.get(reverse('lecturers:project', kwargs={'course_code' : self.code, 'project_pk' : 2}))
        self.assertEqual(res.context['project'].title, 'Test Project')

    def test_project_new(self):
        pass

    def test_modify_project(self):
        pass

    def test_project_copy(self):
        pass

    def test_team_list(self):
        pass
        
    def test_assign_selected_team(self):
        pass

    def test_assign_team(self):
        pass

    def test_unassign_team(self):
        pass

    def test_project_delete(self):
        pass

    def test_team_new(self):
        pass

    def test_modify_team(self):
        pass

    def test_team_delete(self):
        pass

    def test_assign_teams_to_projects(self):
        pass

    def test_course_manage(self):
        pass

    def test_clean_up(self):
        pass

    def test_export_students_to_file(self):
        pass

    def test_export_teams_to_file(self):
        pass

# from django_webtest import WebTest
# from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
# from projects_helper.apps.lecturers.models import Lecturer

#
#
# class LecturerTest(WebTest):
#
#     def create_student(self, name):
#         user = User.objects.create(username=name)
#         return Student.objects.create(user=user)
#
#     def setUp(self):
#         user = User.objects.create(username="TestUser1")
#         self.lecturer = Lecturer.objects.create(user=user)
#
#         user = User.objects.create(username="TestUser2")
#         self.other_lecturer = Lecturer.objects.create(user=user)
#
#     def test_new_project(self):
#         response = self.app.get(reverse('lecturers:project_new'), user='TestUser1')
#         form = response.form
#         form['title'] = "Best_project_ever"
#         form['description'] = "Desc"
#         form.submit()
#         response = self.app.get(reverse('lecturers:project_list'), user='TestUser1')
#         self.assertContains(response, "Best_project_ever")
#
#     def test_delete_project(self):
#         proj = Project.objects.create(lecturer=self.lecturer,
#                                       title="Test_project",
#                                       description="Desc")
#         response = self.app.get(reverse('lecturers:project_list'), user='TestUser1')
#         form = response.forms[1]
#         form['to_delete'] = proj.pk
#         form.submit()
#         self.assertEqual(len(Project.objects.all()), 0)
#
#     def test_list_projects(self):
#         Project.objects.create(lecturer=self.lecturer,
#                                title="Best_project_ever",
#                                description="Desc")
#         response = self.app.get(reverse('lecturers:project_list'), user='TestUser1')
#         self.assertContains(response, "Best_project_ever")
#
#     def test_project_details(self):
#         proj = Project.objects.create(lecturer=self.lecturer,
#                                       title="Best_project_ever",
#                                       description="Desc")
#         response = self.app.get(reverse('lecturers:project',
#                                         kwargs={'project_pk': proj.pk}),
#                                 user='TestUser1')
#         self.assertContains(response, "Best_project_ever")
#
#     def test_project_modify(self):
#         proj = Project.objects.create(lecturer=self.lecturer,
#                                       title="Best_project_ever",
#                                       description="Desc")
#         response = self.app.get(reverse('lecturers:modify_project',
#                                         kwargs={'project_pk': proj.pk}),
#                                 user='TestUser1')
#         form = response.form
#         form['title']="Best_modified_title_ever"
#         form.submit()
#         response = self.app.get(reverse('lecturers:project',
#                                         kwargs={'project_pk': proj.pk}),
#                                 user='TestUser1')
#         self.assertContains(response, "Best_modified_title_ever")
#
#     def test_assign_two_person_team(self):
#
#         proj = Project.objects.create(lecturer=self.lecturer,
#                                       title="Best_project_ever",
#                                       description="Desc")
#         team1 = Team.objects.create(project_preference=proj)
#         team1.student_set.add(self.create_student("Henryk"))
#         team1.student_set.add(self.create_student("Zygmunt"))
#         team2 = Team.objects.create(project_preference=proj)
#         team2.student_set.add(self.create_student("Bolesław"))
#
#         response = self.app.get(reverse('lecturers:assign_team',
#                                         kwargs={'project_pk': proj.pk}),
#                                         user='TestUser1')
#         proj = Project.objects.get(pk=proj.pk)
#         self.assertEqual(proj.team_assigned, team1)
#
#     def test_assign_one_person_team(self):
#         proj = Project.objects.create(lecturer=self.lecturer,
#                                       title="Best_project_ever2",
#                                       description="Desc")
#         team1 = Team.objects.create()
#         team1.student_set.add(self.create_student("Wladyslaw"))
#
#         self.app.get(reverse('lecturers:assign_team',
#                                         kwargs={'project_pk': proj.pk}),
#                                         user='TestUser1')
#         proj = Project.objects.get(pk=proj.pk)
#         #self.assertEqual(proj.team_assigned, team1)
