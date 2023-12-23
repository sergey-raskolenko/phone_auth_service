from django.contrib import admin
from user.models.user import User
from user.models.profile import Profile

admin.site.register(User)
admin.site.register(Profile)
