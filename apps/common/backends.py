from django_cas_ng.backends import CASBackend
#from common.models import Student, Lecturer
from django.apps import apps
#from django.core.exceptions import ObjectDoesNotExist


class ExtendedCASBackend(CASBackend):

    def authenticate(self, ticket, service, request):

        user = super(ExtendedCASBackend, self).authenticate(
            ticket, service, request)

        attributes = request.session.get('attributes', None)
        lecturer_Model = apps.get_model('common', 'Lecturer')
        studentModel = apps.get_model('common', 'Student')

        if attributes is not None:
        	if attributes['employeeType'] == 'S':
        		try:
        			student = studentModel.objects.get(user=user)
        			return user
        		except studentModel.DoesNotExist:
					# first login, create student user
	        		user.user_type = 'S'
	        		user.save()
	        		studentModel.objects.create(user=user)
        	elif attributes['employeeType'] == 'L':		#TODO check what is proper employeeType for lecturer
        		try:
        			student = studentModel.objects.get(user=user)
        			return user
        		except studentModel.DoesNotExist:
					# first login, create lecturer user
	        		user.user_type = 'L'
	        		user.save()
	        		lecturerModel.objects.create(user=user)

        return user

