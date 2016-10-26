from django.core.urlresolvers import reverse
from django_webtest import WebTest
from model_mommy import mommy

from projects_helper.apps.common.models import CustomUser, Student, Lecturer, Project, Team


class StudentTest(WebTest):
    def create_student(self, name):
        custom_user = CustomUser.objects.create(username=name, user_type='S')
        return Student.objects.create(user=custom_user)

    def create_lecturer(self, name):
        custom_user = CustomUser.objects.create(username=name, user_type='L')
        return Lecturer.objects.create(user=custom_user)

    def setUp(self):
        self.student = self.create_student("Macko")
        self.other_student = self.create_student("Henio")

    def test_pick_project(self):
        project = mommy.make(Project)
        response = self.app.get(reverse('students:project_list'), user="Macko")
        form = response.forms["pick_project_form"]
        form["to_pick"] = project.pk
        form.submit().follow()
        project_preference = Student.objects.get(user__username="Macko").project_preference
        self.assertEqual(project_preference, project)

    def test_join_team(self):
        team = mommy.make(Team)
        student_prev_team = Student.objects.get(user__username="Macko").team
        response = self.app.get(reverse('students:team_list'), user="Macko")
        form = response.forms["join_team_form"]
        form["to_join"] = team.pk
        form.submit().follow()
        student_team = Student.objects.get(user__username="Macko").team
        self.assertEqual(student_team, team)

    def test_new_team(self):
        student_prev_team = Student.objects.get(user__username="Macko").team
        response = self.app.get(reverse('students:team_list'), user="Macko")
        form = response.forms["new_team_form"]
        form.submit()
        student_current_team = Student.objects.get(user__username="Macko").team
        self.assertNotEqual(student_prev_team, student_current_team)

    def test_project(self):
        project = mommy.make(Project)

        response = self.app.get(reverse('students:project',
                                        kwargs={'project_pk': project.pk}),
                                user="Macko")
        self.assertContains(response, project.description)

    def test_filtered_project_list(self):
        project = mommy.make(Project)
        other_project = mommy.make(Project)
        response = self.app.get(reverse('students:project_list'), user="Macko")
        self.assertContains(response, project.title)
        self.assertContains(response, project.title)

        form = response.forms["search_form"]
        form["query"] = project.title
        search_response = form.submit()
        self.assertContains(search_response, project.title)
        self.assertNotContains(search_response, other_project.title)
