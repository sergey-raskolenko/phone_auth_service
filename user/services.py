import random
from smsaero import SmsAero
from user.models.user import User
from config.settings import SMSAERO_API_KEY, SMSAERO_EMAIL


class OTP:
	"""Класс для работы с одноразовыми паролями"""
	@staticmethod
	def send_sms(phone, message) -> dict:
		"""
		Статический метод для отправки смс сервисом SmsAero
		"""
		api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
		res = api.send(phone, message)
		assert res.get('success'), res.get('message')
		return res.get('data')

	@classmethod
	def send_otp(cls, phone) -> int:
		"""
		Класс-метод для отправки ОТР пользователю
		"""
		otp = str(random.randint(1000, 9999))
		user = User.objects.get(phone=phone)
		user.otp = otp
		user.save()
		# Some code to send sms
		# cls.send_sms(phone=phone, message=otp)
		print(f"OTP:{otp}")
		return otp

	@staticmethod
	def check_otp(phone, otp):
		"""
		Статический метод для проверки ОТР
		"""
		user = User.objects.get(phone=phone)
		if user.otp == otp:
			return True
		return False
