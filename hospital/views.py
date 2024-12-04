from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.generics import RetrieveAPIView
from .models import Doctor, Patient, Appointment, Treatment, Prescription
from .serializers import DoctorSerializer, PatientSerializer, AppointmentSerializer, TreatmentSerializer, PrescriptionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail  # For email (if needed)
from twilio.rest import Client
from django.core.exceptions import PermissionDenied
from django.conf import settings
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
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
            serializer.save(user=user, doctor=doctor)
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
    
    
# prescription views
class PrescriptionListCreateView(generics.ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        if self.request.user.role != 'doctor':
            raise PermissionDenied("Only doctors can create prescriptions.")
        
        appointment_id = self.request.data.get('appointment')
        doctor_id = self.request.data.get('doctor')

        # Retrieve the appointment object
        appointment = get_object_or_404(Appointment, id=appointment_id)
        patient_phone = appointment.phone_number  # Assuming Appointment has a ForeignKey to Patient
        random_password = get_random_string(length=12)
        # Create or get the patient user
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
        patient_profile, profile_created = Patient.objects.get_or_create(
            user=patient_user,
            name=appointment.patient_name,
            address=appointment.address
            # defaults={
            #     'date_of_birth': '2000-01-01',  # Placeholder, customize as needed
            #     'gender': 'Other',
            #     'emergency_contact': patient_phone,
            #     'blood_type': 'O+',  # Placeholder value
            # }
        )

        # Save the prescription with linked doctor, appointment, and patient
        serializer.save(
            doctor=self.request.user.doctor_profile,
            appointment=appointment,
            patient=patient_profile
        )
        self.send_sms(patient_phone, random_password)
        
        
    def send_sms(self, phone_number, password):
        # Load Twilio credentials from environment variables or Django settings
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_number = settings.TWILIO_PHONE_NUMBER

        client = Client(account_sid, auth_token)
        phone_number = f"+88{phone_number}"
        print(phone_number, password)
        message = f"Your account has been created. Your login password is: {password}"
        # print(phone_number, password)
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
        user = self.request.user
        if user.role == 'doctor':
            return Prescription.objects.filter(doctor__user=user)
        elif user.role == 'patient':
            return Prescription.objects.filter(patient__user=user, published=True)
        return Prescription.objects.none()

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
    
    
    

# agura

# from .utils.agora_utils import generate_agora_token

# def get_agora_token(request):
#     channel_name = request.GET.get('channel_name')  # e.g., 'doctor_patient_123'
#     user_id = request.user.id  # Assuming the user is logged in
    
#     if not channel_name:
#         return JsonResponse({'error': 'Channel name is required'}, status=400)
    
#     token = generate_agora_token(channel_name, user_id)
    
#     return JsonResponse({'token': token, 'channel_name': channel_name})
