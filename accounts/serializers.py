from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate


from django.contrib.auth import get_user_model
User = get_user_model() 


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name', 'description']
        


class CustomUserSerializer(serializers.ModelSerializer):
    position = PositionSerializer()

    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'role', 'date_of_birth', 'gender', 
            'address', 'profile_picture', 'is_verified', 'date_joined', 'is_active', 
            'is_staff', 'is_superuser', 'position'
        ]

# User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False)
    position_name = serializers.CharField(required=False)  # CharField without queryset
    position_description = serializers.CharField(required=False, allow_blank=True)  # Optional description

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'password', 'role', 'department', 'position_name', 'position_description']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        department = validated_data.pop('department', None)
        position_name = validated_data.pop('position_name', None)
        position_description = validated_data.pop('position_description', '')

        # Create a new user using the CustomUser manager
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'patient'),  # Default to 'patient' if no role is provided
        )

        # If a position name is provided, create a new position or assign an existing one
        if position_name:
            # Check if the position already exists in the selected department
            position, created = Position.objects.get_or_create(
                department=department,
                name=position_name,
                defaults={'description': position_description}
            )
            user.position = position  # Assign the position to the user
        else:
            user.position = None

        # Assign department if provided
        if department:
            user.department = department

        user.save()
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



class DepartmentSerializer(serializers.ModelSerializer):
    # position = PositionSerializer(many=True)
    users = CustomUserSerializer(many=True, required=False)
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'users']
    