from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model, logout

from .forms import RegisterForm, LoginForm
from .profile import Profile
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
		new_user =User.objects.create_user(phone=phone, password=None)
		new_profile = Profile.objects.create(user=new_user)
		new_profile.set_invite_code()
		new_profile.save()
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
	context = {
		"title": "OTP checking"
	}
	return render(request, template_name='otp.html', context=context)


def check_otp(request):
	otp = request.POST.get("secret")
	phone = request.POST.get("phone")
	otp_status = OTP.check_otp(phone, otp)

	if otp_status:
		user = authenticate(request, phone=phone)

		if user is not None:
			login(request, user, backend='user.backends.PasswordlessAuthBackend')
			user_profile = Profile.objects.get(user=user)
			return redirect(f"/{user_profile.invite_code}")

	else:
		messages.error(request, "Не верный OTP-код!")

	return render(request, "otp.html")


def profile_page(request, invite_code):
	profile = get_object_or_404(Profile, invite_code=invite_code)
	context = {
		"title": f"Профиль: {profile.user.phone}",
		"profile": profile
	}
	return render(request, template_name="profile.html", context=context)


def enter_invite_code(request, invite_code):
	code = request.POST.get("code")
	try:
		invited_by = Profile.objects.get(invite_code=code)
		profile = Profile.objects.get(invite_code=invite_code)

		if profile.invite_code:
			messages.error(request, "Вы не можете ввести новый код!")

		elif code == invite_code:
			messages.error(request, "Вы не можете ввести свой же код!")

		elif invited_by in profile.profile_set.all():
			messages.error(request, "Вы не можете ввести код того, кого вы пригласили!")

		else:
			profile.invited_by = invited_by
			profile.save()

	except Profile.DoesNotExist:
		messages.error(request, "Код не существует!")

	return redirect(f"/{invite_code}")


def logout_view(request):
	logout(request)
	return redirect("login/")
