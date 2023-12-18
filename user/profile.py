import random
import string

from django.db import models
from django.conf import settings


class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
	invite_code = models.CharField(max_length=6, default=None, verbose_name='invite code')
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

	def save(self, *args, **kwargs):
		if not self.invite_code:
			while True:
				invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
				if not Profile.objects.filter(invite_code=invite_code).exists():
					self.invite_code = invite_code
					break
		super().save(*args, **kwargs)
