from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

# CustomUser Serializer for retrieving or updating user information
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'role', 'date_of_birth', 'gender', 
            'address', 'profile_picture', 'is_verified', 'date_joined', 'is_active', 
            'is_staff', 'is_superuser'
        ]

# User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create a new user using the CustomUser manager
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'patient'),  # Default to 'patient' if no role is provided
        )
        return user

# User Login Serializer
class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        # Authenticate user using phone number and password
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        print(data['phone_number'], data['password'])
        if not user:
            raise serializers.ValidationError("Incorrect phone number or password")
        return {'user': user}
