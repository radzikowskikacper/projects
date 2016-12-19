from django.conf.urls import url

from projects_helper.apps.students import views

urlpatterns = [
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^teams/$', views.team_list, name="team_list"),
    url(r'^teams/new/$', views.new_team, name="new_team"),
    url(r'^teams/join$', views.join_team, name="join_team"),
    url(r'^projects/$', views.project_list, name="project_list"),
    url(r'^projects/(?P<project_pk>\d+)/$', views.project, name="project"),
    url(r'^projects/pick/$', views.pick_project, name="pick_project"),
    url(r'^projects/search$', views.filtered_project_list, name="filtered_project_list"),
]
