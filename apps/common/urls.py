from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django_cas_ng import views as cas_views

from projects_helper.apps.common.views import course_selection

urlpatterns = [
    url(r'^welcome/$', auth_views.logout, {'template_name': "common/welcome.html"}, name='welcome'),
    url(r'^login/$', cas_views.login, {'next_page': "/common/select_course"}, name='cas_ng_login'),
    # url(r'^register/$',
    #     CustomRegistrationView.as_view(),
    #     name="register"),
    url(r'^logged_out/$', auth_views.logout, {'template_name': "common/logout.html"}, name="logged_out"),
    url(r'^logout/$', cas_views.logout, {'next_page': "/common/logged_out"}, name='cas_ng_logout'),
    url(r'^select_course/$', course_selection, name="select_course")

]
