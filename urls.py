from django.conf.urls import url, include
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^students/', include('projects_helper.apps.students.urls', namespace='students')),
    url(r'^lecturers/', include('projects_helper.apps.lecturers.urls', namespace='lecturers')),
    url(r'^common/', include('projects_helper.apps.common.urls', namespace='common')),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('common:login')), name='redirect_login'),
    # url(r'$', RedirectView.as_view(url='common/login')),

]
