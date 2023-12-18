from django.contrib import admin
from user.models import User
from user.profile import Profile

admin.site.register(User)
admin.site.register(Profile)
