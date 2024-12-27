from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.generics import RetrieveAPIView
from .models import Doctor, Appointment, Treatment, Prescription, Test
from patients.models import Patient, BPLevel, SugarLevel, HeartRate, CholesterolLevel
from .serializers import DoctorSerializer, AppointmentSerializer, TreatmentSerializer, PrescriptionSerializer
from patients.serializers import PatientSerializer
from rest_framework.exceptions import ValidationError

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
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
        doctor_id = self.request.data.get('doctor')  # Get doctor ID from request data

        if doctor_id:
            try:
                doctor = Doctor.objects.get(id=doctor_id)
            except Doctor.DoesNotExist:
                return Response({"error": "Doctor not found"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(patient=user, doctor=doctor)
        else:
            return Response({"error": "Doctor ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        
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
        appointment_id = self.kwargs.get('pk')  # Capture appointment ID from the URL
        appointment = Appointment.objects.get(id=appointment_id)
        
        if not appointment_id:
            return Prescription.objects.none()  
        obj = Prescription.objects.filter(appointment=appointment)
        print(obj.first())
        return obj

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



class PendingAppointmentsViewSet(ModelViewSet):
    """
    A viewset for managing pending appointments.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        """
        Filter the appointments to show only pending ones for the logged-in doctor.
        """
        user = self.request.user
        
        
        if not user.is_authenticated:
            return Appointment.objects.none()
        return Appointment.objects.filter(doctor__user__phone_number=f"{user}", status="pending")

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """
        Accept an appointment.
        """
        print(pk)
        try:
            appointment = self.get_object()
            print(appointment)
            if appointment.status != "pending":
                return Response(
                    {"error": "Appointment is already processed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            appointment.status = "accepted"
            
            appointment.save()
            print(appointment.status)
            return Response({"message": "Appointment accepted successfully."}, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """
        Reject an appointment.
        """
        try:
            appointment = self.get_object()
            if appointment.status != "pending":
                return Response(
                    {"error": "Appointment is already processed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            appointment.status = "rejected"
            appointment.save()
            return Response({"message": "Appointment rejected successfully."}, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        
class CancelAppointmentView(APIView):
    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(id=pk, phone_number=f"{request.user}")
            if appointment.status in ['pending']:
                appointment.cancel()
                return Response({'message': 'Appointment cancelled successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Appointment cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)