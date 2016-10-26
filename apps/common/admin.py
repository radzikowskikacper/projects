from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Team)
admin.site.register(Project)
admin.site.register(Student)
admin.site.register(Lecturer)
