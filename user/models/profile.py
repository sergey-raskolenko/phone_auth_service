import random
import string

from django.db import models
from django.conf import settings

from user.models.user import NULLABLE


class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
	invite_code = models.CharField(max_length=6, verbose_name='invite code', **NULLABLE)
	invited_by = models.ForeignKey(
		to="self", on_delete=models.CASCADE, verbose_name='invited by', null=True, blank=True
	)

	class Meta:
		verbose_name = 'profile'
		verbose_name_plural = 'profiles'
		db_table = 'profiles'
		ordering = ['id']

	def __str__(self):
		return f"{self.user}({self.invite_code})"

	def set_invite_code(self):
		if not self.invite_code:
			while True:
				invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
				if not Profile.objects.filter(invite_code=invite_code).exists():
					self.invite_code = invite_code
					break
