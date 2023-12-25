from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from user.api.views import RegisterAPIView, LoginAPIView, LogoutAPIView, OTPAPIView, ProfileAPIView
from user.views import register_page, check_otp, login_page, generate_otp, profile_page, enter_invite_code, logout_view


schema_view = get_schema_view(
	openapi.Info(
		title="PhoneAuthService Documentation",
		default_version='v0.1',
		description="Basic description of the project's API structure",
		terms_of_service="https://www.example.com/policies/terms/",
		contact=openapi.Contact(email="sergey.raskolenko@gmail.com"),
		license=openapi.License(name="BSD License"),
	),
	public=True,
	permission_classes=(permissions.AllowAny,),
	)

urlpatterns = [
	path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
	path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += [
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
	path('api/profile/', ProfileAPIView.as_view(), name="api-profile"),
]
