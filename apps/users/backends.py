from django_cas_ng.backends import CASBackend
from django.apps import apps
from django.conf import settings
import logging


## Instantiating module's logger.
logger = logging.getLogger('projects_helper.apps.users.backends')


def new_user_created_info(attr):
    info_msg = "New user created:"
    for arg, val in attr.items():
        attr_msg = "\n" + arg + ": " + val
        info_msg += attr_msg
    logger.info(info_msg)


def arg_not_found_info(user, arg_name):
    logger.error("Exception: CAS attribute '%s' not found! (username: %s)." % (arg_name, str(user)))


class ExtendedCASBackend(CASBackend):

    def authenticate(self, ticket, service, request):

        user = super(ExtendedCASBackend, self).authenticate(
            ticket, service, request)

        if not (hasattr(user, 'student') or hasattr(user, 'lecturer')):
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
                    studentModel = apps.get_model('students', 'Student')
                    studentModel.objects.create(user=user)
                elif attributes['employeeType'] == 'P':
                    is_admin = (settings.ADMIN_LOGIN == user.username)
                    if is_admin:
                        user.is_staff = True
                        user.is_superuser = True
                    lecturerModel = apps.get_model('lecturers', 'Lecturer')
                    lecturerModel.objects.create(user=user)
                try:
                    user.email = attributes['mail']
                except KeyError as e:
                    arg_not_found_info(user, str(e))
                    user.email = 'user@mail.com'
                try:
                    # save both first names if both are present and together are
                    # shorter than 30 chars, otherwise save only first first name
                    if len(attributes['givenName']) > 30:
                        user.first_name = attributes['givenName'].split()[0]
                    else:
                        user.first_name = attributes['givenName']
                except KeyError as e:
                    arg_not_found_info(user, str(e))
                    user.first_name = user.username
                try:
                    user.last_name = attributes['sn']
                except KeyError as e:
                    arg_not_found_info(user, str(e))

                user.save()
                new_user_created_info(attributes)
            else:
                logger.error("CAS did not return attributes for user %s" % str(user.username))

        else:
            logger.info("User %s logged in" % str(user.email))

        return user
