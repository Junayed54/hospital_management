from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.generics import RetrieveAPIView
from .models import Doctor, Appointment, DoctorAvailability, WaitingList, Treatment, Prescription, Test
from patients.models import Patient, BPLevel, SugarLevel, HeartRate, CholesterolLevel
from .serializers import DoctorSerializer, AppointmentSerializer, TreatmentSerializer, PrescriptionSerializer, DoctorAvailabilitySerializer
from patients.serializers import PatientSerializer
from tests.serializers import TestCollectionAssignmentSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.viewsets import ModelViewSet
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail  # For email (if needed)
from twilio.rest import Client
from django.core.exceptions import PermissionDenied
from django.conf import settings
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from rest_framework.generics import UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from tests.models import TestCollectionAssignment
from django.db import transaction


from django.contrib.auth import get_user_model
User = get_user_model() 


def index(request):
    return render(request, 'base.html')

def send_sms(self, phone_number, password):
    # Load Twilio credentials from environment variables or Django settings
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    twilio_phone_number = settings.TWILIO_PHONE_NUMBER

    client = Client(account_sid, auth_token)
    
    message = f"Your account has been created. Your login password is: {password}"

    try:
        client.messages.create(
            body=message,
            from_=+17755725026,
            to=phone_number
        )
        print(f"SMS sent successfully to {phone_number}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")



# Doctor Views
class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    
class DoctorUpdateView(UpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Ensure that the logged-in user can only update their own doctor profile.
        """
        try:
            doctor = Doctor.objects.get(user=self.request.user)
            return doctor
        except Doctor.DoesNotExist:
            raise PermissionDenied("You do not have permission to edit this profile.")

# Patient Views
class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

# Appointment Views
class AppointmentListCreateView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

# Treatment Views
class TreatmentListCreateView(generics.ListCreateAPIView):
    queryset = Treatment.objects.all()
    serializer_class = TreatmentSerializer

class TreatmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Treatment.objects.all()
    serializer_class = TreatmentSerializer






# appoinments 

# class AppointmentCreateView(APIView):
#     def post(self, request):
#         data = request.data.copy()  # Create a mutable copy of the request data
#         # data['doctor'] = doctor_id

#         if request.user.is_authenticated:
#             # Use logged-in user's information
#             data['user'] = request.user.id
#             data['patient_name'] = request.user.username  # Set patient's name to user's name

#         serializer = AppointmentSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AppointmentCreateView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        print(user)
        serializer.save(patient=user)

    # def perform_create(self, serializer):
    #     user = self.request.user if self.request.user.is_authenticated else None
    #     doctor_id = self.request.data.get('doctor')  # Doctor ID from request
    #     availability_id = self.request.data.get('slot_id')  # Availability ID from request

    #     if not doctor_id or not availability_id:
    #         raise serializers.ValidationError({"error": "Doctor ID and Availability ID are required."})

    #     try:
    #         doctor = Doctor.objects.get(id=doctor_id)
    #     except Doctor.DoesNotExist:
    #         raise serializers.ValidationError({"error": "Doctor not found."})

    #     try:
    #         availability = DoctorAvailability.objects.get(id=availability_id, doctor=doctor)
    #     except DoctorAvailability.DoesNotExist:
    #         raise serializers.ValidationError({"error": "No availability found for the selected doctor."})

    #     # Check if there are free slots
    #     if availability.booked_patients >= availability.max_patients:
    #         raise serializers.ValidationError({"error": "All slots are booked for this availability."})

    #     # Calculate time per patient
    #     time_per_patient = availability.calculate_time_per_patient()
    #     current_time = datetime.combine(availability.date, availability.start_time)

    #     # Determine the next available time slot
    #     existing_appointments = Appointment.objects.filter(
    #         doctor=doctor,
    #         appointment_date__date=availability.date,
    #         status='accepted'
    #     ).order_by('appointment_date')

    #     if existing_appointments.exists():
    #         last_appointment_time = existing_appointments.last().appointment_date
    #         appointment_time = last_appointment_time + timedelta(minutes=time_per_patient)
    #     else:
    #         appointment_time = current_time

    #     # Validate that the appointment_time does not exceed the doctor's working hours
    #     if appointment_time.time() >= availability.end_time:
    #         raise serializers.ValidationError({"error": "The doctor does not have any available slots within working hours."})

    #     # Update booked patients count
    #     availability.booked_patients += 1
    #     availability.save()

    #     # Save the appointment
    #     serializer.save(
    #         patient=user,
    #         doctor=doctor,
    #         appointment_date=appointment_time
    #     )

        
# List Appointments View
class AppointmentListView(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer


class PatientAppointmentDetailView(RetrieveAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    authentication_classes = [JWTAuthentication]

    # Custom method to restrict access to the patient's own appointments
    # def get_queryset(self):
    #     user = self.request.user
    #     return Appointment.objects.filter(user=user)


class DoctorAppointmentListView(APIView):
    # permission_classes = [IsAuthenticated]  # Optional: Restrict access to logged-in users

    def get(self, request, doctor_id):
        appointments = Appointment.objects.filter(doctor_id=doctor_id).order_by('-appointment_date')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class DoctorAppointmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Ensure the logged-in user is a doctor
        if not hasattr(request.user, 'doctor'):
            return Response(
                {"error": "You are not authorized to view this resource."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        doctor = request.user.doctor  # Assuming OneToOne relation between User and Doctor
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
        serializer = AppointmentSerializer(appointments, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# prescription views
class PrescriptionListCreateView(generics.ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        
        if self.request.user.role != 'doctor':
            raise PermissionDenied("Only doctors can create prescriptions.")
        try:
            # Retrieve appointment and doctor
            appointment_id = self.request.data.get('appointment')
            
            appointment = get_object_or_404(Appointment, id=appointment_id)
            patient_phone = appointment.phone_number
            
            # Generate a random password for a new patient
            random_password = get_random_string(length=12)

            # Get or create the patient user
            patient_user, created = User.objects.get_or_create(
                phone_number=patient_phone,
                defaults={
                    'role': 'patient',
                    'phone_number': patient_phone,
                }
            )
            
            if created:
                patient_user.set_password(random_password)
                patient_user.save()
            
            # Ensure the Patient profile exists
            patient_profile, _ = Patient.objects.get_or_create(
                user=patient_user,
                defaults={
                    'name': appointment.patient_name,
                    'address': appointment.address
                }
            )
            
            

            # Extract and validate health metrics
            health_metrics = {
                'bp_systolic': self.request.data.get('vital_measurements').get('bp_systolic'),
                'bp_diastolic': self.request.data.get('vital_measurements').get('bp_diastolic'),
                'sugar_level': self.request.data.get('vital_measurements').get('sugar_level'),
                'heart_rate': self.request.data.get('vital_measurements').get('heart_rate'),
                'cholesterol_level': self.request.data.get('vital_measurements').get('cholesterol_level'),
            }
            print(health_metrics)

            missing_metrics = [key for key, value in health_metrics.items() if not value]
            if missing_metrics:
                raise ValidationError(
                    f"Missing health metrics: {', '.join(missing_metrics)}"
                )

            # Save the prescription
            prescription = serializer.save(
                doctor=self.request.user.doctor_profile,
                appointment=appointment,
                patient=patient_profile,
            )

            # Create health metric records
            BPLevel.objects.create(
                patient=patient_profile,
                systolic=health_metrics['bp_systolic'],
                diastolic=health_metrics['bp_diastolic'],
            )
            SugarLevel.objects.create(
                patient=patient_profile,
                level=health_metrics['sugar_level'],
            )
            HeartRate.objects.create(
                patient=patient_profile,
                rate=health_metrics['heart_rate'],
            )
            CholesterolLevel.objects.create(
                patient=patient_profile,
                level=health_metrics['cholesterol_level'],
            )

            # Send SMS if a new user was created
            if created:
                self.send_sms(patient_phone, random_password)

        except ValidationError as ve:
            raise ve
        except Exception as e:
            print(f"Error during prescription creation: {e}")
            raise ValidationError("An error occurred during prescription creation.")

    
    def send_sms(self, phone_number, password):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_number = settings.TWILIO_PHONE_NUMBER

        client = Client(account_sid, auth_token)
        phone_number = f"+88{phone_number}"
        message = f"Your account has been created. Your login password is: {password}"
        try:
            client.messages.create(
                body=message,
                from_=twilio_phone_number,
                to=phone_number
            )
            print(f"SMS sent successfully to {phone_number}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")




class PrescriptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        appointment_id = self.kwargs.get('pk')
    
        if not appointment_id:
            return Prescription.objects.none()

        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            raise Http404("Appointment not found")

        return Prescription.objects.filter(appointment=appointment)


    def perform_update(self, serializer):
        # Ensure only the doctor can update and publish prescriptions
        if self.request.user.role != 'doctor':
            raise PermissionError("Only doctors can update prescriptions.")
        serializer.save()
    
    # Custom action for publishing a prescription
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        prescription = self.get_object()
        if request.user.role != 'doctor':
            return Response({"detail": "Only doctors can publish prescriptions."}, status=status.HTTP_403_FORBIDDEN)
        
        prescription.published = True
        prescription.save()
        return Response({"detail": "Prescription published successfully!"}, status=status.HTTP_200_OK)
    
class PatientPrescriptionView(RetrieveAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    def get_object(self):
        appointment_id = self.kwargs['id']
        appointment = Appointment.objects.get(id=appointment_id)
        return get_object_or_404(Prescription, appointment=appointment)
    

class PrescriptionDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        prescription_id = request.data.get("prescription_id")  # Get ID from request body

        if not prescription_id:
            return Response({"error": "Prescription ID is required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the doctor's profile linked to the user
        doctor = getattr(request.user, 'doctor_profile', None)

        if not doctor:
            return Response({"error": "You are not authorized to delete prescriptions."}, 
                            status=status.HTTP_403_FORBIDDEN)

        # Get the prescription
        prescription = get_object_or_404(Prescription, pk=prescription_id)

        # Ensure the logged-in doctor created this prescription
        if prescription.doctor != doctor:
            return Response({"error": "You can only delete your own prescriptions."}, 
                            status=status.HTTP_403_FORBIDDEN)

        prescription.delete()
        return Response({"message": "Prescription deleted successfully."}, 
                        status=status.HTTP_204_NO_CONTENT)



class AppointmentPagination(PageNumberPagination):
    page_size = 10  # Set the number of appointments per page

class PatientAppointmentsListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination  # Add pagination
    
    def get_queryset(self):
        return Appointment.objects.filter(phone_number=self.request.user.phone_number).order_by('-appointment_date')






class DoctorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure the current user is a doctor
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response({"error": "You are not authorized to access this dashboard."}, status=403)

        # Get the current day
        today = timezone.now().date()

        # Today's Appointments
        total_appointments = Appointment.objects.filter(
            doctor=doctor,
            status='accepted',
            appointment_date__date=today
        ).count()

        # Upcoming Appointments
        upcoming_appointments = Appointment.objects.filter(
            doctor=doctor,
            status='accepted',
            appointment_date__gte=timezone.now()
        ).order_by('appointment_date')[:5]

        # Total Patients (Based on Prescriptions)
        total_patients = Prescription.objects.filter(doctor=doctor).values('patient').distinct().count()

        # Today's Patients
        todays_patients = Prescription.objects.filter(
            doctor=doctor,
            created_at=today  # Ensure `created_at` is a DateTimeField and correctly filtered by date
        ).count()

        # Serialize Data
        doctor_serializer = DoctorSerializer(doctor)
        upcoming_appointments_serializer = AppointmentSerializer(upcoming_appointments, many=True)

        # Response Data
        data = {
            "doctor_profile": doctor_serializer.data,
            "today_appointments": total_appointments,
            "upcoming_appointments": upcoming_appointments_serializer.data,
            "total_patients": total_patients,
            "todays_patients": todays_patients,
        }

        return Response(data, status=200)



class PendingAppointmentsViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing pending appointments.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_accepted_appointments(self, doctor):
        """
        Fetch all accepted appointments for the given doctor, ordered by date.
        """
        accepted_appointments = Appointment.objects.filter(doctor=doctor, status="accepted").order_by("date")
        return AppointmentSerializer(accepted_appointments, many=True).data

    @action(detail=False, methods=["post"])
    def accept(self, request):
        """
        Accept an appointment using the ID from request body.
        """
        appointment_id = request.data.get("appointment_id")
        if not appointment_id:
            return Response({"error": "Appointment ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.status != "pending":
            return Response({"error": "Appointment is already processed."}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = "accepted"
        appointment.save()

        # Extract the doctor from the appointment
        doctor = appointment.doctor

        # Fetch accepted appointments for this doctor
        accepted_appointments = self.get_accepted_appointments(doctor)

        return Response({
            "message": "Appointment accepted successfully.",
            "accepted_appointments": accepted_appointments
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def reject(self, request):
        """
        Reject an appointment using the ID from request body and set a rejection note.
        """
        appointment_id = request.data.get("appointment_id")
        note = request.data.get("note", "")

        if not appointment_id:
            return Response({"error": "Appointment ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.status != "pending":
            return Response({"error": "Appointment is already processed."}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = "rejected"
        appointment.note = note
        appointment.save()

        # Extract the doctor from the appointment
        doctor = appointment.doctor

        # Fetch accepted appointments for this doctor
        accepted_appointments = self.get_accepted_appointments(doctor)

        return Response({
            "message": "Appointment rejected successfully.",
            "accepted_appointments": accepted_appointments
        }, status=status.HTTP_200_OK)
        
class CancelAppointmentView(APIView):
    def post(self, request):
        appointment_id = request.data.get('appointment_id')  # Fetch id from the body of the request
        
        if not appointment_id:
            return Response({'error': 'Appointment ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the appointment by id and the phone_number linked to the user
            appointment = Appointment.objects.get(id=appointment_id, phone_number=str(request.user))

            # Check if the appointment is in 'pending' status
            if appointment.status == 'pending':
                appointment.cancel()  # Assuming `cancel()` is a method on the Appointment model
                return Response({'message': 'Appointment cancelled successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Appointment cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
        
# Availabilities
class DoctorAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get(self, request, *args, **kwargs):
        """
        Retrieve all availability slots for the authenticated doctor.
        """
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "You do not have a doctor profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        availability = DoctorAvailability.objects.filter(doctor=doctor)
        serializer = DoctorAvailabilitySerializer(availability, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a new availability slot for the authenticated doctor.
        """
        if request.user.role != 'doctor':
            return Response(
                {"error": "Permission denied. Only doctors can access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "You do not have a doctor profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        data['doctor'] = doctor.id  # Associate with the authenticated doctor

        serializer = DoctorAvailabilitySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, availability_id, *args, **kwargs):
        """
        Update an existing availability slot for the authenticated doctor.
        """
        if request.user.role != 'doctor':
            return Response(
                {"error": "Permission denied. Only doctors can access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response(
                {"error": "You do not have a doctor profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        availability = get_object_or_404(DoctorAvailability, id=availability_id, doctor=doctor)

        serializer = DoctorAvailabilitySerializer(availability, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
    def delete(self, request, *args, **kwargs):
        """
        Delete an availability slot for the authenticated doctor.
        The availability ID is taken from the request body.
        """
        # Ensure only doctors can delete availability slots
        if not hasattr(request.user, 'doctor_profile'):
            return Response(
                {"error": "Permission denied. Only doctors can access this resource."},
                status=status.HTTP_403_FORBIDDEN
            )

        doctor = request.user.doctor_profile  # Get the doctor profile linked to the user

        # Get availability ID from request body
        availability_id = request.data.get("availability_id")

        if not availability_id:
            return Response(
                {"error": "Availability ID is required in the request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the availability instance and ensure the doctor owns it
        availability = get_object_or_404(DoctorAvailability, id=availability_id, doctor=doctor)

        # Delete the availability slot
        availability.delete()
        return Response(
            {"message": "Availability slot deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

# Staff Dashboard View



# Admin views
from accounts.serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
class CreateDoctorView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # To handle file uploads

    def post(self, request):
        # Extract user-related data
        user_data = {
            'phone_number': request.data.get('phone_number'),
            'email': request.data.get('email', ''),
            'password': request.data.get('password'),
            'role': 'doctor',  # Explicitly set the role for a doctor
        }

        # Extract doctor-related data
        doctor_data = {
            'full_name': request.data.get('full_name', ''),
            'specialty': request.data.get('specialty', ''),
            'license_number': request.data.get('license_number', ''),
            'bio': request.data.get('bio', ''),
            'experience_years': request.data.get('experience_years', 0),
            'education': request.data.get('education', ''),
            'consultation_fee': request.data.get('consultation_fee', 0.00),
            'contact_email': request.data.get('contact_email', ''),
            'contact_phone': request.data.get('contact_phone', ''),
        }

        # Get certifications (if any)
        certification_files = request.FILES.getlist('certifications')  # Expecting a list of files

        try:
            with transaction.atomic():
                # Create the user
                user_serializer = UserRegistrationSerializer(data=user_data)
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()

                # Pass the `user` instance when creating the doctor
                doctor_serializer = DoctorSerializer(data=doctor_data)
                doctor_serializer.is_valid(raise_exception=True)
                doctor = doctor_serializer.save(user=user)  # Provide `user` to the save method

                # Save certifications (if provided)
                for cert_file in certification_files:
                    CertificationFile.objects.create(doctor=doctor, file=cert_file)

                # Prepare the response
                user_response_data = CustomUserSerializer(user).data
                doctor_response_data = doctor_serializer.data

                return Response({
                    'user': user_response_data,
                    'doctor': doctor_response_data,
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)