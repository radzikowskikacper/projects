from django.test import TestCase
from model_mommy import mommy
from ..models import *

from ..models import Project, Lecturer


def create_student(name):
    custom_user = CustomUser.objects.create(username=name, user_type='S')
    return Student.objects.create(user=custom_user)


class ProjectTest(TestCase):

    def setUp(self):
        custom_user = CustomUser.objects.create(username="Wiktor", user_type='L')
        self.lecturer = Lecturer.objects.create(user=custom_user)
        self.project = Project.objects.create(lecturer=self.lecturer)

    def test_lecturer_creates_project(self):
        lecturer = mommy.make(Lecturer)
        project = Project.objects.create(lecturer=lecturer)
        self.assertEqual(project.lecturer, lecturer)

    def test_status(self):
        instance = mommy.make(Project)
        self.assertEqual(instance.status(), "free")

    def test_assign_random_team(self):
        project = Project.objects.create(lecturer=self.lecturer,title="Project")
        team1 = Team.objects.create(project_preference=project)
        team1.student_set.add(create_student("Stasiek"))
        team1.student_set.add(create_student("Kazik"))

        team2 = Team.objects.create(project_preference=project)
        team2.student_set.add(create_student("Zbyszek"))

        project.assign_random_team()
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.team_assigned, team1)


class TeamTest(TestCase):

    def setUp(self):
        custom_user = CustomUser.objects.create(username="Wiktor", user_type='L')
        self.lecturer = Lecturer.objects.create(user=custom_user)
        self.project = Project.objects.create(lecturer=self.lecturer)

    def test_str(self):
        team1 = Team.objects.create()
        team1.student_set.add(create_student("Stasiek"))
        team1.student_set.add(create_student("Kazik"))

        team2 = Team.objects.create()
        team2.student_set.add(create_student("Zbyszek"))

        self.assertEqual(str(team2), "Zbyszek")
        self.assertEqual(str(team1), "Kazik, Stasiek")



