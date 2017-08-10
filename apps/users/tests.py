from django.test import TestCase
from django.contrib.auth.models import User
from projects_helper.apps.courses.models import Course
from django.core.urlresolvers import reverse
from projects_helper.settings.local import CAS_SERVER_URL

class CASloginTest(TestCase):
    def test_redirect_to_CAS_login_page(self):
        res = self.client.get(reverse('users:cas_ng_login'))
        self.assertTrue(CAS_SERVER_URL in res.url)

class UserTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('test1', 'test1@test.pl', 'test')
        self.client.login(username='test1', password='test')

    def test_home(self):
        res = self.client.get(reverse('users:welcome'))
        self.assertEqual(res.status_code, 200)

    def test_select_course(self):
        res = self.client.get(reverse('users:select_course'))
        self.assertEqual(res.status_code, 200)
        Course.objects.create(name='Test Course1', code='TC1')
        res = self.client.get(reverse('users:select_course'))
        self.assertEqual(res.status_code, 302)
        session = self.client.session
        session['selectedCourse'] = 'TC1'
        session.save()
        Course.objects.create(name='Test Course2', code='TC2')
        res = self.client.post(reverse('users:select_course'),
                                        data={'selection':'TC2'})
        self.assertEqual(self.client.session['selectedCourse'], 'TC2')
