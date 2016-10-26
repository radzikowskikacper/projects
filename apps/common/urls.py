from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from projects_helper.apps.common.views import CustomRegistrationView, user_login

urlpatterns = [
    url(r'^login/$',
        user_login,
        name="login"),
    url(r'^register/$',
        CustomRegistrationView.as_view(),
        name="register"),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': "common/logout.html"},
        name="logout")

]
