from django.contrib.auth import authenticate, login, logout

from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response

from user.api.serializers import ProfileSerializer
from user.forms import RegisterForm, LoginForm
from user.models.user import User
from user.models.profile import Profile
from user.services import OTP


class RegisterAPIView(CreateAPIView):

	def post(self, request, *args, **kwargs):
		form = RegisterForm(request.data)

		if form.is_valid():
			phone = form.cleaned_data.get("phone")

			try:
				validate_international_phonenumber(phone)
				new_user = User.objects.create_user(phone=phone, password=None)
				new_profile = Profile.objects.create(user=new_user)
				new_profile.set_invite_code()
				new_profile.save()
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
					'user_profile_url': f'/api/profile/',
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


class ProfileAPIView(ListCreateAPIView):
	def get(self, request, *args, **kwargs):
		user_id = request.session.get('_auth_user_id')

		if user_id:
			profile = User.objects.get(id=user_id).profile
			content = ProfileSerializer(profile).data
			return Response(content, status=status.HTTP_200_OK)

		else:
			content = {
				'error': "Вы не авторизованы!",
			}
			return Response(content, status=status.HTTP_404_NOT_FOUND)

	def post(self, request, *args, **kwargs):
		invite_code = request.data.get("invite_code")
		user_id = request.session.get('_auth_user_id')

		if user_id:
			profile = User.objects.get(id=user_id).profile

			try:
				invited_by = Profile.objects.get(invite_code=invite_code)

				if profile.invited_by:
					content = {
						'error': "Вы не можете ввести новый код!",
					}
					return Response(content, status=status.HTTP_400_BAD_REQUEST)

				elif profile.invite_code == invite_code:
					content = {
						'error': "Вы не можете ввести свой же код!",
					}
					return Response(content, status=status.HTTP_400_BAD_REQUEST)

				elif invited_by in profile.profile_set.all():
					content = {
						'error': "Вы не можете ввести код того, кого вы пригласили!",
					}
					return Response(content, status=status.HTTP_400_BAD_REQUEST)

				else:
					profile.invited_by = invited_by
					profile.save()
					content = ProfileSerializer(profile).data
					return Response(content, status=status.HTTP_200_OK)

			except Profile.DoesNotExist:
				content = {
					'error': "Код не существует!",
				}
				return Response(content, status=status.HTTP_400_BAD_REQUEST)

		else:
			content = {
				'error': "Вы не авторизованы!",
			}
			return Response(content, status=status.HTTP_404_NOT_FOUND)
