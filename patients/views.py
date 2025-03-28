from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db.models import Q
from django.utils.timezone import now
from hospital.models import Appointment
from hospital.serializers import AppointmentSerializer
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class PatientDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        try:
            # Get the patient object linked to the logged-in user
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            raise NotFound("Patient profile not found for the current user.")

        serializer = PatientSerializer(patient)
        return Response(serializer.data)

class PatientDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request, *args, **kwargs):
       
        try:
            # Get the patient object associated with the authenticated user
            # print(request.user)
            patient = Patient.objects.prefetch_related(
                'bp_levels', 'sugar_levels', 'heart_rates', 'cholesterol_levels'
            ).get(user=request.user)
            
            serializer = PatientSerializer(patient)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({'error': 'User is not a patient'}, status=status.HTTP_403_FORBIDDEN)





class PatientAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        patient = request.user.phone_number  # Assumes the authenticated user is the patient
        print(patient)
        # Filter upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            Q(phone_number=patient),
            Q(appointment_date__gt=now()),
            ~Q(status='cancelled'),
            ~Q(status='rejected')
        ).order_by('appointment_date')

        # Filter joined appointments with either status accepted or with a prescription
        joined_appointments = Appointment.objects.filter(
            Q(phone_number=patient),
            Q(appointment_date__lte=now()),
            Q(status='accepted') | Q(prescription__isnull=False)  # OR condition
        ).order_by('-appointment_date')

        # Filter pending appointments
        pending_appointments = Appointment.objects.filter(
            Q(phone_number=patient),
            Q(status='pending')
        ).order_by('appointment_date')

        # Serialize the data
        upcoming_appointments_data = AppointmentSerializer(upcoming_appointments, many=True).data
        joined_appointments_data = AppointmentSerializer(joined_appointments, many=True).data
        pending_appointments_data = AppointmentSerializer(pending_appointments, many=True).data

        return Response({
            "upcoming_appointments": upcoming_appointments_data,
            "joined_appointments": joined_appointments_data,
            "pending_appointments": pending_appointments_data,  # ✅ Added pending appointments
        })


class UpdatePatientView(APIView):
    permission_classes = [IsAuthenticated]

    def get_patient(self, user):
        try:
            return Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            return None

    def patch(self, request, *args, **kwargs):
        patient = self.get_patient(request.user)
        if not patient:
            return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(patient, data=request.data, partial=True)  # Partial updates allowed
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        patient = self.get_patient(request.user)
        if not patient:
            return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(patient, data=request.data, partial=True)  # Partial updates also supported here
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report categories."""
    queryset = ReportCategory.objects.all()
    serializer_class = ReportCategorySerializer
    permission_classes = [IsAuthenticated]


class PatientReportTypeViewSet(viewsets.ModelViewSet):
    queryset = ReportType.objects.all()
    serializer_class = PatientReportTypeSerializer
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        if isinstance(response.data, dict) and 'detail' in response.data:
            # Keep default behavior for error messages
            return super().finalize_response(request, response, *args, **kwargs)

        if response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]:
            if not response.data:  # Ensure a response even if DRF sends an empty response
                if request.method == "DELETE":
                    response.data = {"message": "Deleted successfully"}
                else:
                    instance = self.get_object() if "pk" in kwargs else self.get_queryset()
                    response.data = self.get_serializer(instance, many=not "pk" in kwargs).data
        return super().finalize_response(request, response, *args, **kwargs)

    
class PatientReportViewSet(viewsets.ModelViewSet):
    queryset = PatientReport.objects.all().order_by('-uploaded_at')
    serializer_class = PatientReportCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def get_queryset(self):
        return PatientReport.objects.filter(patient=self.request.user)  # Patients can only see their own reports


class PatientPrescriptionViewSet(viewsets.ModelViewSet):
    queryset = PatientPrescription.objects.all().order_by('-uploaded_at')
    serializer_class = PatientPrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)  # Automatically assign the logged-in user as the patient

    def get_queryset(self):
        return PatientPrescription.objects.filter(patient=self.request.user)  