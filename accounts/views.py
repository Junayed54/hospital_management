from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import update_session_auth_hash
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from hospital.models import Appointment 
from rest_framework_simplejwt.tokens import RefreshToken
# User Signup View
class UserSignupView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        request.data['role'] = 'patient'
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        
        # Connect existing appointments with the same phone number
        phone_number = serializer.validated_data.get('phone_number')
        Appointment.objects.filter(phone_number=phone_number, user__isnull=True).update(user=user)
        

        
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )

# User Login View
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        # Validate the incoming data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract the validated user data
        user = serializer.validated_data['user']
        
        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        
        # Return the response with access token, refresh token, and phone_number
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'phone_number': user.phone_number,  # Returning phone_number instead of username
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Blacklist the refresh token
                return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
            return Response({"detail": "No refresh token provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class PasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response({"error": "Both fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(current_password, user.password):
            return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        # Keep the user logged in after password change
        update_session_auth_hash(request, user)

        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)