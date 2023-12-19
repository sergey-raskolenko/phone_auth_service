import random
from smsaero import SmsAero
from user.models import User
from config.settings import SMSAERO_API_KEY, SMSAERO_EMAIL


class OTP:
	@staticmethod
	def send_sms(phone, message) -> dict:
		api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
		res = api.send(phone, message)
		print(res)
		assert res.get('success'), res.get('message')
		return res.get('data')

	@classmethod
	def send_otp(cls, phone):
		otp = str(random.randint(1000, 9999))
		user = User.objects.get(phone=phone)
		user.otp = otp
		user.save()
		# Some code to send sms
		# cls.send_sms(phone=phone, message=otp)
		print(otp)

	@staticmethod
	def check_otp(phone, otp):
		user = User.objects.get(phone=phone)
		if user.otp == otp:
			return True
		return False
