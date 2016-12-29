from django.conf.urls import url
from projects_helper.apps.about import views


urlpatterns = [
    url(r'^$', views.info, name="info"),
]
