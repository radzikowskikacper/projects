from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/$', views.project_list, name="project_list"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/(?P<project_pk>\d+)/$', views.project, name="project"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/assign_all/$', views.assign_teams_to_projects, name="assign_teams_to_projects"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/new/$', views.project_new, name="project_new"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/(?P<project_pk>\d+)/modify/$', views.modify_project, name="modify_project"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/search$', views.filtered_project_list, name="filtered_project_list"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/teams/$', views.team_list, name="team_list"),
    url(r'^projects/(?P<project_pk>\d+)/assign_selected/(?P<team_pk>\d+)$', views.assign_selected_team, name="assign_selected_team"),
    url(r'^projects/(?P<project_pk>\d+)/assign/$', views.assign_team, name="assign_team"),
    url(r'^projects/(?P<project_pk>\d+)/unassign/$', views.unassign_team, name="unassign_team"),
    url(r'^projects/manage_projects/$', views.manage_projects, name="manage_projects"),
    url(r'^teams/del/$', views.team_delete, name="team_delete"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/teams/new/$', views.team_new, name="team_new"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/teams/(?P<team_pk>\d+)/modify/$', views.modify_team, name="modify_team"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/courses_manage/$', views.course_manage, name="course_manage"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/clean_up/$', views.clean_up, name="clean_up"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/export_students/$', views.export_students_to_file, name="export_students"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/export_teams/$', views.export_teams_to_file, name="export_teams"),
]
