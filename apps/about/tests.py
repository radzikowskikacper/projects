from django.test import TestCase, Client
from .apps import AboutConfig

class AboutTestCase(TestCase):

    def test_page(self):
        res = self.client.get('/about/')
        self.assertEqual(res.status_code, 200)

    def english_title(self):
        res = self.client.get('/about/', HTTP_ACCEPT_LANGUAGE='en')
        assertInHTML(b'How to use Project Helper app',res.content)

    def polish_title(self):
        res = self.client.get('/about/', HTTP_ACCEPT_LANGUAGE='pl')
        assertInHTML(b'Spos\xc3\xb3b u\xc5\xbcycia aplikacji do zapis\xc3\xb3w', res.content)
