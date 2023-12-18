import random

from user.models import User


class OTP:

	@staticmethod
	def send_otp(phone):
		otp = str(random.randint(1000, 9999))
		user = User.objects.get(phone=phone)
		user.otp = otp
		user.save()
		# Some code to send sms
		print(otp)

	@staticmethod
	def check_otp(phone, otp):
		user = User.objects.get(phone=phone)
		if user.otp == otp:
			return True
		return False
