def is_lecturer(user):
    return user.user_type == "L" or user.is_superuser
