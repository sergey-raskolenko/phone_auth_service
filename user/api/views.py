from django.contrib.auth import authenticate, login, logout

from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from user.forms import RegisterForm, LoginForm
from user.models import User
from user.profile import Profile
from user.services import OTP


class RegisterAPIView(CreateAPIView):

	def post(self, request, *args, **kwargs):
		form = RegisterForm(request.data)

		if form.is_valid():
			phone = form.cleaned_data.get("phone")
			try:
				validate_international_phonenumber(phone)
				User.objects.create_user(phone=phone, password=None)
				content = {
					'phone': phone
				}
				return Response(content, status=status.HTTP_200_OK)
			except Exception as e:
				content = {
					'error': e
				}
				return Response(content, status=status.HTTP_400_BAD_REQUEST)

		content = {
			'error': form.errors
		}
		return Response(content, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(CreateAPIView):

	def post(self, request, *args, **kwargs):

		form = LoginForm(request.data)

		if form.is_valid():
			phone = form.cleaned_data.get("phone")
			try:
				user = User.objects.get(phone=phone)
				otp = OTP.send_otp(phone)
				content = {
					'phone': str(user.phone),
					'otp': otp,
					'link_for_auth': f"/api/otp/{user.pk}/"
				}
				return Response(content, status=status.HTTP_200_OK)
			except Exception as e:
				content = {
					'error': f'User not found ({e})'
				}
				return Response(content, status=status.HTTP_404_NOT_FOUND)
		content = {
			'error': form.errors
		}
		return Response(content, status=status.HTTP_400_BAD_REQUEST)


class OTPAPIView(CreateAPIView):

	def post(self, request, *args, **kwargs):
		phone = request.data.get("phone")
		otp = request.data.get("otp")
		otp_status = OTP.check_otp(phone, otp)
		if otp_status:
			user = authenticate(request, phone=phone)
			if user is not None:
				login(request, user, backend='user.backends.PasswordlessAuthBackend')
				user_profile = Profile.objects.get(user=user)
				content = {
					'is_auth_user': request.user.is_authenticated,
					'user': str(request.user),
					'auth': str(request.auth),
					'user_profile_url': f'/{user_profile.invite_code}/',
					'last_login': request.user.last_login
				}
				return Response(content, status=status.HTTP_200_OK)
		else:
			content = {
				'error': "Не верный OTP-код!"
			}
			return Response(content, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(ListAPIView):

	def get(self, request, *args, **kwargs):
		logout(request)
		content = {
			'is_auth_user': request.user.is_authenticated,
			'user': str(request.user),
			'auth': str(request.auth),
			'login_url': '/api/login/'
		}
		return Response(content, status=status.HTTP_200_OK)
