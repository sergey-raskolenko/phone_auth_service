from django.contrib import admin
from django.urls import path
from user.views import register_page, check_otp, login_page, generate_otp, profile

urlpatterns = [
	path('admin/', admin.site.urls),
	path('register/', register_page, name="register"),
	path('check/', check_otp, name="check_otp"),
	path('login/', login_page, name="login"),
	path('otp/<int:pk>/<uuid>/', generate_otp),
	path('<int:pk>/', profile, name="profile"),
]
