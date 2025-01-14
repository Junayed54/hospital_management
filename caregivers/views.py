from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import CareRequest, Caregiver
from .serializers import *
from accounts.serializers import *
from accounts.permissions import *




class CaregiverCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if the user is an admin
        if request.user.role != 'admin':  # Assuming 'admin' role is set in your system
            return Response({"error": "You do not have permission to create caregivers."}, status=status.HTTP_403_FORBIDDEN)

        # Step 1: Create the User object first
        user_data = {
            'phone_number': request.data.get('phone_number'),
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            'role': request.data.get('role', 'staff'),  # Default to staff role if not provided
            'department': request.data.get('department'),
            'position': request.data.get('position')
        }
        user_serializer = UserRegistrationSerializer(data=user_data)
        
        if user_serializer.is_valid():
            user = user_serializer.save()  # Create the user object
        else:
            print(user_serializer.errors)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Step 2: Create the Caregiver object
        caregiver_data = {
            'user': user,
            'full_name': request.data.get('full_name'),
            'gender': request.data.get('gender', 'male'),
            'date_of_birth': request.data.get('date_of_birth'),
            'address': request.data.get('address'),
            'phone_number': request.data.get('phone_number'),
            'email': request.data.get('email'),
            'certifications': request.data.get('certifications'),
            'bio': request.data.get('bio'),
            'experience_years': request.data.get('experience_years', 0),
            'available_from': request.data.get('available_from'),
            'available_to': request.data.get('available_to')
        }

        caregiver = Caregiver.objects.create(**caregiver_data)

        return Response({"message": "Caregiver created successfully!"}, status=status.HTTP_201_CREATED)

# List and Create Care Requests
class CareRequestListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if user is a caregiver or patient
        # if hasattr(request.user, 'caregiver'):
        #     care_requests = CareRequest.objects.filter(caregiver=request.user)
        # else:
        #     care_requests = CareRequest.objects.filter(patient=request.user)
        care_requests = CareRequest.objects.all()
        serializer = CareRequestSerializer(care_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if hasattr(request.user, 'caregiver'):
            raise PermissionDenied("Caregivers cannot create care requests.")
        
        serializer = CareRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(patient=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class AssignCaregiverAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        # Extract request_id and caregiver_id from the request data
        request_id = request.data.get('request_id')
        caregiver_id = request.data.get('caregiver_id')
        print(request_id, caregiver_id)
        # Validate inputs
        if not request_id or not caregiver_id:
            return Response({"error": "Both request_id and caregiver_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the care request
            care_request = CareRequest.objects.get(id=request_id)
        except CareRequest.DoesNotExist:
            return Response({"error": "Care Request not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Fetch the caregiver
            caregiver = User.objects.get(id=caregiver_id)
        except User.DoesNotExist:
            return Response({"error": "Caregiver not found."}, status=status.HTTP_404_NOT_FOUND)

        # Assign the caregiver to the care request
        care_request.caregiver = caregiver
        care_request.status = "pending"  # Update status if necessary
        care_request.save()

        # Return a success response
        return Response({
            "message": "Caregiver assigned successfully.",
            "care_request_id": care_request.id,
            "assigned_caregiver": {
                "id": caregiver.id,
                "name": caregiver.caregiver.full_name,  # Adjust according to your User model
            }
        }, status=status.HTTP_200_OK)
        
        
        
        
        
# Update Care Request Status (Accept or Decline)
class CareRequestUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, action):
        
        try:
            care_request = CareRequest.objects.get(id=pk)
            print(care_request)
        except CareRequest.DoesNotExist:
            return Response({"error": "Care Request not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            care_request.status = 'accepted'
            care_request.caregiver = request.user
        elif action == 'decline':
            care_request.status = 'canceled'
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        care_request.save()
        return Response({"message": f"Care request {action}ed successfully."}, status=status.HTTP_200_OK)


class CareRequestStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Query for different statuses
        pending_no_caregiver = CareRequest.objects.filter(status="pending", caregiver__isnull=True)
        pending_with_caregiver = CareRequest.objects.filter(status="pending", caregiver__isnull=False)
        accepted = CareRequest.objects.filter(status="accepted")
        completed = CareRequest.objects.filter(status="completed")
        canceled = CareRequest.objects.filter(status="canceled")

        # Helper function to serialize care requests
        def serialize_care_request(care_request):
            return {
                "id": care_request.id,
                "patient": {
                    "id": care_request.patient.id if care_request.patient else None,
                    "name": care_request.patient.patient_profile.name if care_request.patient else None,  # Ensure `name` exists
                } if care_request.patient else None,
                "caregiver": {
                    "id": care_request.caregiver.id if care_request.caregiver else None,
                    # "name": care_request.caregiver.full_name if care_request.caregiver else None,  # Ensure `name` exists
                } if care_request.caregiver else None,
                "start_date": care_request.start_date.isoformat() if care_request.start_date else None,
                "end_date": care_request.end_date.isoformat() if care_request.end_date else None,
                "description": care_request.description,
                "payment_amount": float(care_request.payment_amount) if care_request.payment_amount else None,
            }

        # Build response data
        data = {
            "pending_no_caregiver": [serialize_care_request(care_request) for care_request in pending_no_caregiver],
            "pending_with_caregiver": [serialize_care_request(care_request) for care_request in pending_with_caregiver],
            "accepted": [serialize_care_request(care_request) for care_request in accepted],
            "completed": [serialize_care_request(care_request) for care_request in completed],
            "canceled": [serialize_care_request(care_request) for care_request in canceled],
        }

        return Response(data)



    
class UpdateCareRequestStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            care_request = CareRequest.objects.get(pk=pk)
            new_status = request.data.get("status")
            care_request.status = new_status
            care_request.save()
            return Response({"message": "Status updated successfully."}, status=status.HTTP_200_OK)
        except CareRequest.DoesNotExist:
            return Response({"error": "Care request not found."}, status=status.HTTP_404_NOT_FOUND)
