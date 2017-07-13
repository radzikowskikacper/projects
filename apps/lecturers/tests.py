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

    def is_in_messages(self, text, response):
        m = list(response.context.get('messages'))[0]
        return text in m.message

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
        proj = Project.objects.create(pk=9, title='TestProject9', description='111', course=self.course, lecturer=self.lecturer)
        team1 = Team.objects.create(pk=4, course=self.course, project_preference=proj)
        team2 = Team.objects.create(pk=5, course=self.course)
        res = self.client.get(reverse('lecturers:team_list', kwargs=self.kwargs))
        self.assertEqual(res.context['teams'][0], team1)
        self.assertEqual(res.context['teams_with_no_project'][0], team2)

    def test_assign_selected_team(self):
        self.set_session()
        proj = Project.objects.create(pk=10, title='TestProject10', course=self.course, lecturer=self.lecturer)
        team = Team.objects.create(pk=6, course=self.course)
        res = self.client.post(reverse('lecturers:assign_selected_team', args=[10, 6]))
        self.assertTrue(team.project_assigned, proj)

    def test_assign_team(self):
        self.set_session()
        proj = Project.objects.create(pk=11, title='TestProject11', course=self.course, lecturer=self.lecturer)
        team = Team.objects.create(pk=7, course=self.course, project_preference=proj)
        res = self.client.get(reverse('lecturers:assign_team', args=[11]))
        self.assertTrue(team.project_assigned, proj)

    def test_unassign_team(self):
        self.set_session()
        proj = Project.objects.create(pk=12, title='TestProject12', course=self.course, lecturer=self.lecturer)
        team = Team.objects.create(pk=8, course=self.course, project_preference=proj)
        proj.team_assigned = team
        proj.save()
        res = self.client.get(reverse('lecturers:unassign_team', args=[12]))
        self.assertEqual(team.project_assigned, None)

    def test_project_delete(self):
        self.set_session()
        Project.objects.create(pk=6, title='TestProject6', description='111', course=self.course, lecturer=self.lecturer)
        res = self.client.post(reverse('lecturers:manage_projects'), data={'to_change' : [6], 'delete': 0})
        self.assertFalse(Project.objects.filter(title='TestProject6').exists())

    def test_team_new(self):
        pass

    def test_modify_team(self):
        students = []
        for i in range(4):
            user = User.objects.create_user('aaaa'+str(i), 't'+str(i)+'@test.pl', 'test')
            students.append(Student.objects.create(user=user))
        pref_proj = Project.objects.create(pk=7, title='TestProject7', description='111', course=self.course, lecturer=self.lecturer)
        chosen_proj = Project.objects.create(pk=8, title='TestProject8', description='111', course=self.course, lecturer=self.lecturer)
        team1 = Team.objects.create(pk=1, course=self.course, project_preference=pref_proj)
        team2 = Team.objects.create(pk=2, course=self.course, project_preference=pref_proj)
        team3 = Team.objects.create(pk=3, course=self.course, project_preference=pref_proj)
        students[0].join_team(team1)
        students[1].join_team(team1)
        students[2].join_team(team2)
        students[3].join_team(team3)
        chosen_proj.assign_team(team1)
        res = self.client.get(reverse('lecturers:modify_team', kwargs={**self.kwargs, 'team_pk' : 1}))
        self.assertTrue('value=\"TestProject8\"' in str(res.context['form']))

        res = self.client.post(reverse('lecturers:modify_team', kwargs={**self.kwargs, 'team_pk' : 1}),
                                    data={'display_member_1' : '', 'display_member_2' : '',
                                          'change_member_1' : 'on', 'member_1_select' : students[2].pk,
                                          'change_member_2' : 'on', 'member_2_select' : students[3].pk,
                                          'display_project' : 'TestProject8',
                                          'change_project' : 'on', 'project_select' : 7})

        self.assertEqual(Project.objects.get(pk=7).team_assigned, team1)

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
        self.assertTrue(self.is_in_messages('Assigned 1 of 2 teams', res))

    def test_course_manage(self):
        pass

    def test_clean_up(self):
        pass

    def test_export_students_to_file(self):
        pass

    def test_export_teams_to_file(self):
        pass
