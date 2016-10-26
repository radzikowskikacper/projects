from django_webtest import WebTest
from ..common.models import *
from django.core.urlresolvers import reverse


class LecturerTest(WebTest):

    def create_student(self, name):
        custom_user = CustomUser.objects.create(username=name, user_type='S')
        return Student.objects.create(user=custom_user)

    def setUp(self):
        custom_user = CustomUser.objects.create(username="Wiktor", user_type='L')
        self.lecturer = Lecturer.objects.create(user=custom_user)

        custom_user = CustomUser.objects.create(username="Bogdan", user_type='L')
        self.other_lecturer = Lecturer.objects.create(user=custom_user)

    def test_new_project(self):
        response = self.app.get(reverse('lecturers:project_new'), user='Wiktor')
        form = response.form
        form['title'] = "Best_project_ever"
        form['description'] = "Desc"
        form.submit()
        response = self.app.get(reverse('lecturers:project_list'), user='Wiktor')
        self.assertContains(response, "Best_project_ever")

    def test_delete_project(self):
        proj = Project.objects.create(lecturer=self.lecturer,
                                      title="Test_project",
                                      description="Desc")
        response = self.app.get(reverse('lecturers:project_list'), user='Wiktor')
        form = response.forms[1]
        form['to_delete'] = proj.pk
        form.submit()
        self.assertEqual(len(Project.objects.all()), 0)

    def test_list_projects(self):
        Project.objects.create(lecturer=self.lecturer,
                               title="Best_project_ever",
                               description="Desc")
        response = self.app.get(reverse('lecturers:project_list'), user='Wiktor')
        self.assertContains(response, "Best_project_ever")

    def test_project_details(self):
        proj = Project.objects.create(lecturer=self.lecturer,
                                      title="Best_project_ever",
                                      description="Desc")
        response = self.app.get(reverse('lecturers:project',
                                        kwargs={'project_pk': proj.pk}),
                                user='Wiktor')
        self.assertContains(response, "Best_project_ever")

    def test_project_modify(self):
        proj = Project.objects.create(lecturer=self.lecturer,
                                      title="Best_project_ever",
                                      description="Desc")
        response = self.app.get(reverse('lecturers:modify_project',
                                        kwargs={'project_pk': proj.pk}),
                                user='Wiktor')
        form = response.form
        form['title']="Best_modified_title_ever"
        form.submit()
        response = self.app.get(reverse('lecturers:project',
                                        kwargs={'project_pk': proj.pk}),
                                user='Wiktor')
        self.assertContains(response, "Best_modified_title_ever")

    def test_assign_two_person_team(self):

        proj = Project.objects.create(lecturer=self.lecturer,
                                      title="Best_project_ever",
                                      description="Desc")
        team1 = Team.objects.create(project_preference=proj)
        team1.student_set.add(self.create_student("Henryk"))
        team1.student_set.add(self.create_student("Zygmunt"))
        team2 = Team.objects.create(project_preference=proj)
        team2.student_set.add(self.create_student("Bolesław"))

        response = self.app.get(reverse('lecturers:assign_team',
                                        kwargs={'project_pk': proj.pk}),
                                user='Wiktor')
        proj = Project.objects.get(pk=proj.pk)
        self.assertEqual(proj.team_assigned, team1)

    def test_assign_one_person_team(self):
        proj = Project.objects.create(lecturer=self.lecturer,
                                      title="Best_project_ever2",
                                      description="Desc")
        team1 = Team.objects.create()
        team1.student_set.add(self.create_student("Wladyslaw"))

        self.app.get(reverse('lecturers:assign_team',
                                        kwargs={'project_pk': proj.pk}),
                                user='Wiktor')
        proj = Project.objects.get(pk=proj.pk)
        #self.assertEqual(proj.team_assigned, team1)



