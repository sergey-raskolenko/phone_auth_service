from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import User
from user.models.profile import Profile


class UserBaseTestCase(APITestCase):
	"""Тест-кейс для регистрации/авторизации пользователя"""
	def setUp(self):
		self.user = User.objects.create_user(phone="+79999999999")

	def test_register(self):
		"""Тест для регистрации нового пользователя"""
		data = {
			"phone": "+79999999998"
		}
		response = self.client.post(reverse('api-register'), data=data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(User.objects.get(phone=data['phone']))

	def test_register_error(self):
		"""Тест для проверки ошибки регистрации с неверным номером"""
		data = {"phone": "+71111111111"}
		response = self.client.post(reverse('api-register'), data=data)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_login(self):
		"""Тест авторизации пользователя"""
		data = {
			"phone": self.user.phone
		}
		response = self.client.post(reverse('api-login'), data=data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_login_error(self):
		"""Тест для проверки ошибки авторизации несуществующего пользователя"""
		data = {
			"phone": "+79999999998"
		}
		response = self.client.post(reverse('api-login'), data=data)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserOTPAuthTestCase(APITestCase):
	"""Тест-кейс по работе с ОТР"""
	def setUp(self):
		self.data = {
			"phone": "+79999999999"
		}
		self.user = User.objects.create_user(phone=self.data.get("phone"))
		self.profile = Profile.objects.create(user=self.user)
		self.profile.set_invite_code()
		self.profile.save()

		self.client.post(reverse('api-login'), data=self.data)
		self.user.refresh_from_db()

	def test_otp_check(self):
		"""Тест для проверки введенного ОТР и входа пользователя в систему"""
		self.data["otp"] = self.user.otp
		response = self.client.post(reverse('api-otp-check', kwargs={'pk': self.user.pk}), data=self.data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(self.user.is_authenticated)

	def test_otp_check_empty(self):
		"""Тест для проверки пустого поля ОТР"""
		response = self.client.post(reverse('api-otp-check', kwargs={'pk': self.user.pk}), data=self.data)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_otp_check_wrong(self):
		"""Тест для проверки неверно введенного ОТР"""
		self.data["otp"] = "xxxx"
		response = self.client.post(reverse('api-otp-check', kwargs={'pk': self.user.pk}), data=self.data)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileLogoutTestCase(APITestCase):
	"""Тест-кейс выхода из профиля"""
	def setUp(self):
		self.data = {
			"phone": "+79999999999"
		}
		self.user = User.objects.create_user(phone=self.data.get("phone"))
		self.profile = Profile.objects.create(user=self.user)
		self.profile.set_invite_code()
		self.profile.save()

		self.client.post(reverse('api-login'), data=self.data)
		self.user.refresh_from_db()

		self.data["otp"] = self.user.otp
		self.client.post(reverse('api-otp-check', kwargs={'pk': self.user.pk}), data=self.data)
		self.user.refresh_from_db()

	def test_logout(self):
		"""Тест выхода из системы пользователем"""
		response = self.client.get(reverse('api-logout'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data.get("user"), "AnonymousUser")

	def test_user_profile(self):
		"""Тест получения информации о профиле пользователя"""
		response = self.client.get(reverse('api-profile'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserProfileInviteCodeTestCase(APITestCase):
	"""Тест-кейс для добавления инвайт-кода пользователю"""
	def setUp(self):
		self.data = {
			"phone": "+79999999999"
		}
		self.user = User.objects.create_user(phone=self.data.get("phone"))
		self.profile = Profile.objects.create(user=self.user)
		self.profile.set_invite_code()
		self.profile.save()

		self.client.post(reverse('api-login'), data=self.data)
		self.user.refresh_from_db()

		self.data["otp"] = self.user.otp
		self.client.post(reverse('api-otp-check', kwargs={'pk': self.user.pk}), data=self.data)
		self.user.refresh_from_db()

		self.user_test = User.objects.create_user(phone="+79999999998")
		self.profile_test = Profile.objects.create(user=self.user_test)
		self.profile_test.set_invite_code()
		self.profile_test.save()

	def test_user_profile_invite_code_adding(self):
		"""Тест добавления инвайт-кода"""
		data = {
			"invite_code": self.profile_test.invite_code
		}
		response = self.client.post(reverse('api-profile'), data=data)
		self.profile.refresh_from_db()
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.profile.invited_by, self.profile_test)

	def test_user_profile_invite_own_code_adding(self):
		"""Тест для проверки ошибки ввода собственного инвайт-кода"""
		data = {
			"invite_code": self.profile.invite_code
		}
		response = self.client.post(reverse('api-profile'), data=data)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_user_profile_invite_wrong_code_adding(self):
		"""Тест для проверки ошибки ввода несуществующего инвайт-кода"""
		data = {
			"invite_code": ""
		}
		response = self.client.post(reverse('api-profile'), data=data)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
