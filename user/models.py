from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from user.manager import UserManager
from django.db import models
from django.contrib.auth.models import PermissionsMixin

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser, PermissionsMixin):
	objects = UserManager()

	phone = PhoneNumberField(max_length=30, verbose_name='phone', unique=True)
	username = None

	USERNAME_FIELD = "phone"
	REQUIRED_FIELDS = []

	class Meta:
		verbose_name = 'user'
		verbose_name_plural = 'users'
		db_table = 'users'
		ordering = ['id']

	def __str__(self):
		return str(self.phone)
