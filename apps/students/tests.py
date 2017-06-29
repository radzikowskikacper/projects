from django.test import TestCase
from ..courses.models import Course
from ..teams.models import Team
from ..lecturers.models import Lecturer
from ..projects.models import Project
from .models import Student
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class StudentTest(TestCase):

    def setUp(self):
        user = User.objects.create_user('test1', 'test1@test.pl', 'test')
        Student.objects.create(user=user)
        self.client.login(username='test1', password='test')

        #course
        self.code = 'TC'
        self.course = Course.objects.create(name='Test Course', code=self.code)
        self.kwargs = {'course_code' : self.code}

        #project
        user = User.objects.create_user('test2', 'test2@test.pl', 'test')
        lecturer = Lecturer.objects.create(user=user)
        self.project = Project.objects.create(pk=1, title='Test Project', course=self.course, lecturer=lecturer)

    def set_session(self):
        session = self.client.session
        session['selectedCourse'] = self.code
        session.save()

    def test_profile1(self):
        res = self.client.get(reverse('students:profile'))
        self.assertEqual(res.status_code, 302)

    def test_profile2(self):
        self.set_session()
        res = self.client.get(reverse('students:profile'))
        self.assertEqual(res.status_code, 200)

    def test_team_list(self):
        Team.objects.create(pk=1, course=self.course)
        res = self.client.get(reverse('students:team_list', kwargs=self.kwargs))
        self.assertEqual([team.pk for team in res.context['teams']], [1])

    def test_project_list(self):
        res = self.client.get(reverse('students:project_list', kwargs=self.kwargs))
        self.assertEqual([project.pk for project in res.context['projects']], [1])

    def test_project(self):
        res = self.client.get(reverse('students:project', kwargs={'course_code' : self.code, 'project_pk' : 1}))
        self.assertEqual(res.context['project'].title, 'Test Project')

    def test_pick_project_with_no_team(self):
        self.set_session()
        res = self.client.post(reverse('students:pick_project'), data='to_pick=1', content_type='application/x-www-form-urlencoded')
        self.assertEqual(res['Location'], reverse('students:project_list', kwargs=self.kwargs))

    def test_filtered_project_list(self):
        res = self.client.get(reverse('students:filtered_project_list', kwargs={'course_code' : 'TC'}), data={'title':'Test Project','filter':'free'})
        self.assertEqual(res.status_code, 200)

    def test_join_team(self):
        self.set_session()
        t = Team.objects.create(pk=2, course=self.course, project_preference=self.project)
        res = self.client.post(reverse('students:join_team'), data='to_join=2', content_type='application/x-www-form-urlencoded')
        self.assertEqual(res.status_code, 302)

    def test_new_team(self):
        self.set_session()
        res = self.client.post(reverse('students:new_team'), content_type='application/x-www-form-urlencoded')
        self.assertEqual(res.status_code, 302)
        
