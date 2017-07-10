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
        self.user = User.objects.create_user('test1', 'test1@test.pl', 'test')
        self.lecturer = Lecturer.objects.create(user=self.user)
        self.client.login(username='test1', password='test')

        #course
        self.code = 'TC'
        self.course = Course.objects.create(name='Test Course', code=self.code)
        self.kwargs = {'course_code' : self.code}

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
        Project.objects.create(pk=2, title='Test Project', description='**sample text**', course=self.course, lecturer=self.lecturer)
        res = self.client.get(reverse('lecturers:project', kwargs={'course_code' : self.code, 'project_pk' : 2}))
        self.assertEqual(res.context['project'].title, 'Test Project')
        self.assertInHTML('<strong>sample text</strong>', str(res.content))

    def test_project_new(self):
        res = self.client.post(reverse('lecturers:project_new', kwargs=self.kwargs), data={'title' : 'TestProject1','description':'123'})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Project.objects.filter(title='TestProject1', description='123').exists())

    def test_modify_project(self):
        Project.objects.create(pk=3, title='TestProject3', description='**sample text**', course=self.course, lecturer=self.lecturer)
        res = self.client.get(reverse('lecturers:modify_project', kwargs={**self.kwargs, 'project_pk': 3}))
        self.assertEqual(res.status_code, 200)
        res = self.client.post(reverse('lecturers:modify_project', kwargs={**self.kwargs, 'project_pk': res.context['project'].pk}), data={'title' : 'abc','description':'111'})
        self.assertTrue(Project.objects.filter(title='abc', description='111').exists())

    def test_duplicate_projects(self):
        self.set_session()
        Project.objects.create(pk=4, title='TestProject4', description='111', course=self.course, lecturer=self.lecturer)
        Project.objects.create(pk=5, title='TestProject5', description='111', course=self.course, lecturer=self.lecturer)
        res = self.client.post(reverse('lecturers:manage_projects'), data={'to_change' : [4, 5], 'duplicate': 0})
        self.assertTrue(Project.objects.filter(title='TestProject4 - copy', description='111').exists())
        self.assertTrue(Project.objects.filter(title='TestProject5 - copy', description='111').exists())

    def test_team_list(self):
        pass

    def test_assign_selected_team(self):
        pass

    def test_assign_team(self):
        pass

    def test_unassign_team(self):
        pass

    def test_project_delete(self):
        self.set_session()
        Project.objects.create(pk=6, title='TestProject6', description='111', course=self.course, lecturer=self.lecturer)
        res = self.client.post(reverse('lecturers:manage_projects'), data={'to_change' : [6], 'delete': 0})
        self.assertFalse(Project.objects.filter(title='TestProject6').exists())

    def test_team_new(self):
        pass

    def test_modify_team(self):
        pass

    def test_team_delete(self):
        pass

    def test_assign_teams_to_projects(self):
        u = User.objects.create_user('test2', 'test2@test.pl', 'test')
        project = Project.objects.create(pk=3, title='Test3', course=self.course, lecturer=self.lecturer)
        team1 = Team.objects.create(course=self.course, project_preference=project)
        team2 = Team.objects.create(course=self.course, project_preference=project)
        s1 = Student.objects.create(user=self.user)
        s2 = Student.objects.create(user=u)
        s1.join_team(team1)
        s2.join_team(team2)
        res = self.client.get(reverse('lecturers:assign_teams_to_projects', kwargs=self.kwargs), follow=True)
        m = list(res.context.get('messages'))[0]
        self.assertTrue('Assigned 1 of 2 teams' in m.message)

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
