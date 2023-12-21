from rest_framework import serializers

from user.profile import Profile


class ProfileSerializer(serializers.ModelSerializer):
	invited_followers = serializers.SerializerMethodField()
	phone = serializers.SerializerMethodField()

	@staticmethod
	def get_phone(instance):
		return str(instance.user.phone)
	@staticmethod
	def get_invited_followers(instance):
		return [str(profile) for profile in instance.profile_set.all()]

	class Meta:
		model = Profile
		fields = ["id", "user", "phone", "invite_code", "invited_by", "invited_followers"]
