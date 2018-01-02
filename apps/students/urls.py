from django.conf.urls import url

from projects_helper.apps.students import views

urlpatterns = [
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^profile_edit/$', views.profile_edit, name="profile_edit"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/teams/$', views.team_list, name="team_list"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/$', views.project_list, name="project_list"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/(?P<project_pk>\d+)/$', views.project, name="project"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/(?P<project_pk>\d+)/file/$', views.files, name="file_handler"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/(?P<project_pk>\d+)/file/(?P<file_id>\d+)/$', views.files, name="file_handler"),
    url(r'^(?P<course_code>[a-zA-Z0-9]+)/projects/search$', views.filtered_project_list, name="filtered_project_list"),
    url(r'^teams/new/$', views.new_team, name="new_team"),
    url(r'^teams/join$', views.join_team, name="join_team"),
    url(r'^projects/pick/$', views.pick_project, name="pick_project"),
]
