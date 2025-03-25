from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Department, Position
from .serializers import *
from .permissions import *
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
        print(user)
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response({"error": "current and new password required."}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(current_password, user.password):
            return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        # Keep the user logged in after password change
        update_session_auth_hash(request, user)

        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
    
    
    
    
class CreateDepartmentView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def post(self, request):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract department data
        department_data = {
            'name': request.data.get('name'),
            'description': request.data.get('description', ''),
        }
        

        try:
            # Create the department using the serializer
            department_serializer = DepartmentSerializer(data=department_data)
            department_serializer.is_valid(raise_exception=True)
            
            department = department_serializer.save()

            # Return success response
            return Response({
                'department': department_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DepartmentListView(APIView):
    permission_classes = [IsStaffOrAdminUser]

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
    
class DepartmentDetailView(APIView):
    permission_classes = [IsStaffUserAndDepartmentMatch]

    def get(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        users_data = []

        self.check_object_permissions(request, department)
        # Get all users belonging to the department
        department_users = department.users.all()

        for user in department_users:
            users_data.append({
                "id": user.id,
                "phone_number": user.phone_number,
                "email": user.email,
                "position": user.position.name if user.position else None,  # Get the position name if available
                "role": user.role,
                "gender": user.gender,
            })

        return Response({
            "department": {
                "id": department.id,
                "name": department.name,
                "description": department.description,
            },
            "users": users_data
        })
        
        
class CareGiverUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Retrieve the "Care-Giver" department
            care_giver_department = Department.objects.get(name="Care-giver")

            # Filter users belonging to the "Care-Giver" department
            care_giver_users = User.objects.filter(department=care_giver_department)

            # Serialize user data along with caregiver's full name
            data = []
            for user in care_giver_users:
                caregiver = getattr(user, 'caregiver', None)  # Check if a related caregiver exists
                data.append({
                    "id": user.id,
                    "username": user.caregiver.full_name,
                    "email": user.email,
                    "caregiver_name": caregiver.full_name if caregiver else None,
                })

            
            return Response(data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response(
                {"error": "Care-Giver department not found."},
                status=status.HTTP_404_NOT_FOUND
            )