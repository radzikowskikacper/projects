from django.contrib import admin
from django.contrib.auth.models import *
from django.contrib.auth.admin import UserAdmin
from .models import *


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets =  (
        (None, {'fields': ('user_type',)}),
    ) + UserAdmin.fieldsets



admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course)
admin.site.register(Team)
admin.site.register(Project)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.unregister(Group)

