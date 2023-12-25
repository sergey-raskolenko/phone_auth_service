from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from user.manager import UserManager
from django.db import models

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser, PermissionsMixin):
	"""Модель для описания пользователя"""
	objects = UserManager()

	username = None

	phone = PhoneNumberField(max_length=30, verbose_name='phone', unique=True)
	otp = models.CharField(max_length=4, verbose_name='otp', **NULLABLE)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=False)

	USERNAME_FIELD = "phone"
	REQUIRED_FIELDS = []

	class Meta:
		verbose_name = 'user'
		verbose_name_plural = 'users'
		db_table = 'users'
		ordering = ['id']

	def __str__(self):
		return str(self.phone)
