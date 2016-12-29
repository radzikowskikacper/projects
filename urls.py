from django.conf.urls import url, include
from django.contrib import admin
from daeauth import AdminSiteWithExternalAuth

admin.site = AdminSiteWithExternalAuth()
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^students/', include('projects_helper.apps.students.urls', namespace='students')),
    url(r'^lecturers/', include('projects_helper.apps.lecturers.urls', namespace='lecturers')),
    url(r'^about/', include('projects_helper.apps.about.urls', namespace='about')),
    url(r'^', include('projects_helper.apps.common.urls', namespace='common')),
]

urlpatterns += [
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
