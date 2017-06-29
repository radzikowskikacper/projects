from django.test import TestCase

# def create_student(name):
#     custom_user = CustomUser.objects.create(username=name)
#     return Student.objects.create(user=custom_user)
#
#
# class ProjectTest(TestCase):
#
#     def setUp(self):
#         custom_user = CustomUser.objects.create(username="Wiktor")
#         self.lecturer = Lecturer.objects.create(user=custom_user)
#         self.course = Course.objects.create(name="kurs")
#         self.project = Project.objects.create(lecturer=self.lecturer)
#
#     def test_lecturer_creates_project(self):
#         lecturer = mommy.make(Lecturer)
#         project = Project.objects.create(lecturer=lecturer, course=self.course)
#         self.assertEqual(project.lecturer, lecturer)
#         self.assertEqual(project.course, self.course)
#
#     def test_status(self):
#         instance = mommy.make(Project)
#         self.assertEqual(instance.status(), "free")
#
#     def test_assign_random_team(self):
#         project = Project.objects.create(lecturer=self.lecturer, title="Project", course=self.course)
#         team1 = Team.objects.create(project_preference=project)
#         team1.student_set.add(create_student("Stasiek"))
#         team1.student_set.add(create_student("Kazik"))
#
#         team2 = Team.objects.create(project_preference=project)
#         team2.student_set.add(create_student("Zbyszek"))
#
#         project.assign_random_team()
#         project = Project.objects.get(pk=project.pk)
#         self.assertEqual(project.team_assigned, team1)
