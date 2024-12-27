from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.utils.timezone import now
from hospital.models import Appointment
from hospital.serializers import AppointmentSerializer
from .models import Patient
from .serializers import PatientSerializer
from rest_framework.permissions import IsAuthenticated

class PatientDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get the patient object associated with the authenticated user
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
        patient = f"{request.user}"  # Assumes the authenticated user is the patient

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
            Q(status='accepted') | Q(prescription__isnull=False),  # OR condition
        ).order_by('-appointment_date')

        # Serialize the data
        upcoming_appointments_data = AppointmentSerializer(upcoming_appointments, many=True).data
        joined_appointments_data = AppointmentSerializer(joined_appointments, many=True).data

        return Response({
            "upcoming_appointments": upcoming_appointments_data,
            "joined_appointments": joined_appointments_data,
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