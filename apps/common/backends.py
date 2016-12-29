from django_cas_ng.backends import CASBackend
#from common.models import Student, Lecturer
from django.apps import apps
from django.conf import settings
#from django.core.exceptions import ObjectDoesNotExist


class ExtendedCASBackend(CASBackend):

    def authenticate(self, ticket, service, request):

        user = super(ExtendedCASBackend, self).authenticate(
            ticket, service, request)

        lecturerModel = apps.get_model('lecturers', 'Lecturer')
        studentModel = apps.get_model('students', 'Student')

        if user.user_type == 'N':
            attributes = request.session.get('attributes', None)
            if attributes:
                try:
                    attributes['employeeType']
                except KeyError:
                    # inform about exception. this user will be redirected back
                    # to home page (see: .views.redirect_user)
                    print(
                        "Exception: CAS attribute 'employeeType' not found!" +
                        " (username: " + user.username + ").")
                    return user
                if attributes['employeeType'] == 'S':
                    user.user_type = 'S'
                    studentModel.objects.create(user=user)
                elif attributes['employeeType'] == 'P':
                    user.user_type = 'L'
                    is_admin = (settings.ADMIN_LOGIN == user.username)
                    if is_admin:
                        user.is_staff = True
                        user.is_superuser = True
                        lecturerModel.objects.create(user=user)
                try:
                    user.email = attributes['mail']
                except KeyError:
                    print(
                        "Exception: CAS attribute 'mail' not found!" +
                        " (username: " + user.username + ").")
                    user.email = 'user@mail.com'
                user.save()

                print("New user created:")
                for arg, val in attributes.items():
                    print(arg + ": " + val)

        elif user.user_type == 'S' or user.user_type == 'L':
            print("User logged in: email: " + user.email)

        return user
