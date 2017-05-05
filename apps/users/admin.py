from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('name', 'user_type', 'is_superuser')

    def name(self,obj):
        return obj.first_name + ' ' + obj.last_name

    def user_type(self, obj):
        if hasattr(obj, 'student'):
            return "Student"
        else:
            return "Lecturer"


admin.site.register(User, UserAdmin)
