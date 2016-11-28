def is_student(user):
    return user.user_type == 'S' or user.is_superuser
