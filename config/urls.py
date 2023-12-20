from django.contrib import admin
from django.urls import path

from user.api.views import RegisterAPIView, LoginAPIView, LogoutAPIView, OTPAPIView
from user.views import register_page, check_otp, login_page, generate_otp, profile_page, enter_invite_code, logout_view

urlpatterns = [
	path('admin/', admin.site.urls),
	path('register/', register_page, name="register"),
	path('check/', check_otp, name="check_otp"),
	path('login/', login_page, name="login"),
	path('', logout_view, name="logout"),
	path('otp/<int:pk>/<uuid>/', generate_otp),
	path('<str:invite_code>/', profile_page, name="profile"),
	path('<str:invite_code>/enter_invite_code/', enter_invite_code, name="enter_invite_code"),

	path('api/register/', RegisterAPIView.as_view(), name="api-register"),
	path('api/login/', LoginAPIView.as_view(), name="api-login"),
	path('api/logout/', LogoutAPIView.as_view(), name="api-logout"),
	path('api/otp/<int:pk>/', OTPAPIView.as_view(), name="api-otp-check"),
]
