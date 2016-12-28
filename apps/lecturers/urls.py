from django.conf.urls import url
from projects_helper.apps.lecturers import views

urlpatterns = [
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^projects/$', views.project_list, name="project_list"),
    url(r'^projects/(?P<project_pk>\d+)/$', views.project, name="project"),
    url(r'^projects/del/$', views.project_delete, name="project_delete"),
    url(r'^projects/assign_all/$', views.assign_teams_to_projects, name="assign_teams_to_projects"),
    url(r'^projects/(?P<project_pk>\d+)/assign/$', views.assign_team, name="assign_team"),
    url(r'^projects/(?P<project_pk>\d+)/unassign/$', views.unassign_team, name="unassign_team"),
    url(r'^projects/new/$', views.project_new, name="project_new"),
    url(r'^projects/(?P<project_pk>\d+)/modify/$', views.modify_project, name="modify_project"),
    url(r'^projects/(?P<project_pk>\d+)/copy/$', views.project_copy, name="project_copy"),
    url(r'^projects/search$', views.filtered_project_list, name="filtered_project_list"),
    url(r'^teams/$', views.team_list, name="team_list"),
    url(r'^teams/del/$', views.team_delete, name="team_delete"),
]
