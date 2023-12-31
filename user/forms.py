from django import forms

from user.models.user import User


class RegisterForm(forms.Form):
	phone = forms.CharField(label="Телефон", widget=forms.TextInput(attrs={'placeholder': 'Введите номер'}))

	def clean_phone(self):
		phone = self.cleaned_data.get('phone')
		user = User.objects.filter(phone=phone)
		if user.exists():
			raise forms.ValidationError("Пользователь с таким номером уже существует!")
		return phone


class LoginForm(forms.Form):
	phone = forms.CharField(label="Телефон", widget=forms.TextInput(attrs={'placeholder': 'Введите номер'}))

	def clean_phone(self):
		phone = self.cleaned_data.get('phone')
		user = User.objects.filter(phone=phone)
		if not user.exists():
			raise forms.ValidationError("Нет пользователя с таким номером. Попробуйте зарегистрироваться")
		return phone
