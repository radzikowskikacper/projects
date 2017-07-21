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
        res = self.client.get(reverse('lecturers:team_new', args=['TC']))
        self.assertEqual(res.status_code, 200)
        proj = Project.objects.create(pk=13, title='TestProject13', description='111', course=self.course, lecturer=self.lecturer)
        user1 = User.objects.create_user('bbb1', 'bbb1@test.pl', 'test')
        user2 = User.objects.create_user('bbb2', 'bbb2@test.pl', 'test')
        student1 = Student.objects.create(user=user1)
        student2 = Student.objects.create(user=user2)
        team1 = Team.objects.create(pk=9, course=self.course, project_preference=proj)
        team2 = Team.objects.create(pk=10, course=self.course, project_preference=proj)
        student1.join_team(team1)
        student2.join_team(team2)
        res = self.client.post(reverse('lecturers:team_new', args=['TC']),
                               data= {'member_1': student1.pk,
                                      'next_stud_check': 'on',
                                      'member_2': student2.pk,
                                      'project_check': 'on',
                                      'project': proj.pk})
        self.assertTrue(student1.teams, student2.teams)

    def test_modify_team(self):
        students = []
        for i in range(4):
            user = User.objects.create_user('aaaa'+str(i), 't'+str(i)+'@test.pl', 'test')
            students.append(Student.objects.create(user=user))
        pref_proj = Project.objects.create(pk=7, title='TestProject7', description='111', course=self.course, lecturer=self.lecturer)
        chosen_proj = Project.objects.create(pk=8, title='TestProject8', description='111', course=self.course, lecturer=self.lecturer)
        team1 = Team.objects.create(pk=1, project_preference=pref_proj)
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
        res = self.client.post(reverse('lecturers:modify_team', kwargs={**self.kwargs, 'team_pk' : 1}),
                                    data={'display_member_1' : '', 'display_member_2' : '',
                                          'change_member_1' : 'on', 'member_1_select' : '',
                                          'change_member_2' : 'on', 'member_2_select' : '',
                                          'display_project' : 'TestProject7', 'project_select' : ''},
                                          follow=True)
        self.assertFalse(Team.objects.filter(pk=1).exists())

    def test_team_delete(self):
        self.set_session()
        res = self.client.get(reverse('lecturers:team_delete'))
        self.assertEqual(res.status_code, 404)
        team = Team.objects.create(pk=11, course=self.course)
        res = self.client.post(reverse('lecturers:team_delete'), data={'to_delete':[11]})
        self.assertFalse(Team.objects.filter(pk=11).exists())

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
        self.assertTrue(self.is_in_messages('Assigned 1 of 2 teams', res))

    def test_course_manage(self):
        self.set_session()
        res = self.client.get(reverse('lecturers:course_manage', args=[self.code]))
        self.assertTrue(res.status_code, 200)
        Course.objects.create(pk=2, name='Test Course2', code='TC2')
        Course.objects.create(pk=3, name='Test Course3', code='TC3')

        res = self.client.post(reverse('lecturers:course_manage', args=[self.code]),
                    data={'form-0-name':'Test Course2', 'form-0-code':'TC2', 'form-0-id':2, 'form-0-DELETE':'on',
                          'form-1-name':'Modified Course', 'form-1-code':'MC', 'form-1-id':3,
                          'form-2-name':'New Course', 'form-2-code':'NC', 'form-2-id':'',
                          'form-TOTAL_FORMS':3, 'form-INITIAL_FORMS':2, 'form-MIN_NUM_FORMS':0, 'form-MAX_NUM_FORMS':10})
        self.assertFalse(Course.objects.filter(name='Test Course2').exists())
        self.assertTrue(Course.objects.filter(name='Modified Course').exists())
        self.assertTrue(Course.objects.filter(name='New Course').exists())

    def test_clean_up(self):
        proj = Project.objects.create(pk=14, lecturer=self.lecturer)
        Team.objects.create(pk=15, course=self.course, project_preference=proj)
        Team.objects.create(pk=16, course=self.course)
        res = self.client.get(reverse('lecturers:clean_up', args=[self.code]))
        self.assertFalse(Team.objects.filter(pk=15).exists())
        self.assertTrue(Team.objects.filter(pk=16).exists())

    def test_save_projects_to_file(self):
        Project.objects.create(pk=15, title='ĄĆĘŁŻŹŃ', course=self.course, description='ąęćóń', lecturer=self.lecturer)
        res = self.client.get(reverse('lecturers:save_projects_to_file', args=[self.code]))
        self.assertEqual(str(res.content, "utf-8"), '{ĄĆĘŁŻŹŃ}\n{ąęćóń}\n')

    def test_load_projects_from_file(self):
        import os
        from django.core.files.uploadedfile import SimpleUploadedFile
        with open('testfile', 'w+', encoding='utf-8') as file_to_test:
            file_to_test.write('{ĄĆĘŁłńó}\n{dęszkąpśn}\n')
            file_to_test.seek(0)
            res = self.client.post(reverse('lecturers:load_projects_from_file', args=[self.code]),
                                            data={'name': 'file_to_test',
                                                  'file': file_to_test})
        self.assertTrue(Project.objects.filter(title='ĄĆĘŁłńó', description='dęszkąpśn').exists())
        os.remove('testfile')

    def test_export_teams_to_file(self):
        Project.objects.create(pk=16, title='ĄĆ', course=self.course, description='ąęćź', lecturer=self.lecturer)
        res = self.client.get(reverse('lecturers:export_teams', args=[self.code]))
        self.assertEqual(str(res.content, 'utf-8'), 'TC,Test Course\r\n\r\nL.p.,Temat projektu,Prowadzący,Przypisany zespół\r\n1,ĄĆ,,\r\n')

    def test_export_students_to_file(self):
        user = User.objects.create_user('test4', 'test4@test.pl', 'test')
        student = Student.objects.create(user=self.user)
        team1 = Team.objects.create(course=self.course)
        student.join_team(team1)
        res = self.client.get(reverse('lecturers:export_students', args=[self.code]))
        self.assertEqual(str(res.content, 'utf-8'), 'TC,Test Course\r\n\r\nL.p.,Nazwisko,Imiona,Adres e-mail,Tytuł przypisanego projektu,Prowadzący\r\n1,,,test1@test.pl,,\r\n')
