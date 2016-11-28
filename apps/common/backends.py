from django_cas_ng.backends import CASBackend
#from common.models import Student, Lecturer
from django.apps import apps
from django.conf import settings
#from django.core.exceptions import ObjectDoesNotExist


class ExtendedCASBackend(CASBackend):

    def authenticate(self, ticket, service, request):

        user = super(ExtendedCASBackend, self).authenticate(
            ticket, service, request)

        attributes = request.session.get('attributes', None)
        lecturerModel = apps.get_model('common', 'Lecturer')
        studentModel = apps.get_model('common', 'Student')

        if attributes is not None:
            if attributes['employeeType'] == 'S':
                try:
                    student = studentModel.objects.get(user=user)
                    return user
                except studentModel.DoesNotExist:
                	# logged in for the first time, create student user
                    user.user_type = 'S'
                    user.email = attributes['mail']

                    user.save()
                    studentModel.objects.create(user=user)
            elif attributes['employeeType'] == 'P':
                try:
                    lecturer = lecturerModel.objects.get(user=user)
                    return user
                except lecturerModel.DoesNotExist:
                    # logged in for the first time, create lecturer user
                    is_admin = (settings.ADMIN_LOGIN == user.username)
                    if is_admin:
                        user.is_staff = True
                        user.is_superuser = True

                    user.user_type = 'L'
                    user.email = attributes['mail']
                    user.save()
                    lecturerModel.objects.create(user=user)

        return user

