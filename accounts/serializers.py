from rest_framework import serializers
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["anrede", "geburtsdatum", "telefon", "strasse", "plz", "stadt", "bundesland", "preferred_language"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_staff"]
        read_only_fields = ["id", "email", "is_staff"]


class AdminUserListSerializer(serializers.ModelSerializer):
    subscription_plan = serializers.CharField(source="profile.subscription_plan", default="free")
    document_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "is_active", "is_staff", "is_email_verified",
            "date_joined", "last_login",
            "subscription_plan", "document_count",
        ]


class AdminUserDetailSerializer(serializers.ModelSerializer):
    subscription_plan = serializers.CharField(source="profile.subscription_plan", default="free")
    document_count = serializers.IntegerField(read_only=True)
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "is_active", "is_staff", "is_email_verified",
            "date_joined", "last_login",
            "subscription_plan", "document_count", "profile",
        ]


class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Ein Benutzer mit dieser E-Mail-Adresse existiert bereits."
            )
        return value

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Passwörter stimmen nicht überein."})

        # Run Django's configured password validators (min length, common, numeric, etc.)
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(data["password1"])
        except Exception as e:
            raise serializers.ValidationError({"password1": list(e.messages)})

        return data

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "password1": self.validated_data.get("password1", ""),
        }

    def save(self, request):
        from allauth.account.adapter import get_adapter
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.save()
        return user
