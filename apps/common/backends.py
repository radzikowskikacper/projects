from django_cas_ng.backends import CASBackend
#from common.models import Student, Lecturer
from django.apps import apps
from django.conf import settings
#from django.core.exceptions import ObjectDoesNotExist


def new_user_created_info(attr):
    print("New user created:")
    for arg, val in attr.items():
        print(arg + ": " + val)

def arg_not_found_info(user, arg_name):
    print("Exception: CAS attribute '" + arg_name + "' not found!" +
    " (username: " + user.username + ").")

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
                except KeyError as e:
                    # inform about exception. this user will be redirected back
                    # to home page (see: .views.redirect_user)
                    arg_not_found_info(user, str(e))
                    new_user_created_info(attributes)
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
                except KeyError as e:
                    arg_not_found_info(user, str(e))
                    user.email = 'user@mail.com'
                try:
                    user.first_name = attributes['givenName'].split()[0]
                except KeyError as e:
                    arg_not_found_info(user, str(e))
                    user.first_name = user.username
                try:
                    user.last_name = attributes['sn']
                except KeyError as e:
                    arg_not_found_info(user, str(e))

                user.save()
                new_user_created_info(attributes)

        elif user.user_type == 'S' or user.user_type == 'L':
            print("User logged in: email: " + user.email)

        return user
