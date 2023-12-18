import time

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse

from .forms import RegisterForm, LoginForm
from .services import OTP
from django.contrib import messages
import uuid

User = get_user_model()


def register_page(request):
	form = RegisterForm(request.POST or None)
	context = {
		"form": form,
		"title": "Registration"
	}
	if form.is_valid():
		phone = form.cleaned_data.get("phone")
		User.objects.create_user(phone=phone, password=None)
		return redirect("/login")
	return render(request, template_name="register.html", context=context)


def login_page(request):
	form = LoginForm(request.POST or None)
	context = {
		"form": form,
		"title": "Authorization"
	}
	if form.is_valid():
		phone = form.cleaned_data.get('phone')
		try:
			user = User.objects.get(phone=phone)
			OTP.send_otp(phone)
			temp = uuid.uuid4()
			return redirect(f"/otp/{user.pk}/{temp}")
		except Exception as e:
			messages.error(request, "No such user exists!")

	return render(request, template_name="login.html", context=context)


def generate_otp(request, pk, uuid):
	return render(request, template_name='otp.html')


def check_otp(request):
	otp = request.POST.get("secret")
	phone = request.POST.get("phone")
	context = {
		"title": "OTP checking"
	}
	otp_status = OTP.check_otp(phone, otp)
	if otp_status:
		user = authenticate(request, phone=phone)
		if user is not None:
			login(request, user, backend='user.backends.PasswordlessAuthBackend')
			return redirect(f"/{user.pk}")
		else:
			messages.error(request, "Wrong OTP!")

	print(f"otp via form: {otp}")
	return render(request, "otp.html", context=context)


def profile(request, pk):
	user = get_object_or_404(User, pk=pk)
	context = {
		"title": f"Профиль: {user.phone}",
		"user": user
	}
	return render(request, template_name="profile.html", context=context)
