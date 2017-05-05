from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django_cas_ng import views as cas_views
from projects_helper.apps.users.views import course_selection, home

urlpatterns = [
    url(r'^$', home, name='welcome'),
    url(r'^login/$', cas_views.login, {'next_page': "/select_course"}, name='cas_ng_login'),
    url(r'^logged_out/$', auth_views.logout, {'template_name': "users/logout.html"}, name="logged_out"),
    url(r'^logout/$', cas_views.logout, {'next_page': "/logged_out"}, name='cas_ng_logout'),
    url(r'^select_course/$', course_selection, name="select_course")
]
