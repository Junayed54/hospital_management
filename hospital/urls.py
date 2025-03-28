from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .views import *

router = DefaultRouter()
router.register(r'pending-appointments', PendingAppointmentsViewSet, basename='pending-appointments')


urlpatterns = [
    path('api/', include(router.urls)),
    # Doctor URLs
    path('doctors/', DoctorListCreateView.as_view(), name='doctor-list-create'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('doctor/update/', DoctorUpdateView.as_view(), name='doctor-update'),
    
    
    # Patient URLs
    path('patients/', PatientListCreateView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),

    # Appointment URLs
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
   
    # Treatment URLs
    path('treatments/', TreatmentListCreateView.as_view(), name='treatment-list-create'),
    path('treatments/<int:pk>/', TreatmentDetailView.as_view(), name='treatment-detail'),
    
    #Appointment
    path('api/appointments/', AppointmentCreateView.as_view(), name='create_appointment'),
    path('api/appointments/list/', AppointmentListView.as_view(), name='list_appointments'),
    path('api/appointment/<int:pk>/', PatientAppointmentDetailView.as_view(), name='patient_appointment_detail'),
    path('patient-appointment/', PatientAppointmentsListView.as_view(), name='patient-appointments'),
    path('api/doctor/<int:doctor_id>/appointments/', DoctorAppointmentListView.as_view(), name='doctor_appointments'),
    path('api/appointments/cancel/', CancelAppointmentView.as_view(), name='cancel_appointment'),
    #prescription urls
    path('prescriptions/', PrescriptionListCreateView.as_view(), name='prescription-list-create'),
    path('prescriptions/<int:pk>/', PrescriptionRetrieveUpdateDestroyView.as_view(), name='prescription-detail'),
    
    path('patient-prescription/<int:id>/', PatientPrescriptionView.as_view(), name='patient-prescription'),
    path('prescription/delete/', PrescriptionDeleteAPIView.as_view(), name='prescription-delete'),
    # path('api/get-agora-token/', get_agora_token, name='get_agora_token'),

    path('api/doctor/dashboard/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    
    
    #Availabilit
    path('doctor/availability/', DoctorAvailabilityView.as_view(), name='create_availability'),  # For creating availability
    path('doctor/availability/<int:availability_id>/', DoctorAvailabilityView.as_view(), name='update_availability'),  # For updating availability
    
    
    
    path('api/create-doctor/', CreateDoctorView.as_view(), name='doctor_create'),
    
    path('specialties/create/', SpecialtyCreateView.as_view(), name='create-specialty'),
    path('specialties/update/<int:pk>/', SpecialtyUpdateView.as_view(), name='update-specialty'),
    path('specialties/delete/<int:pk>/', SpecialtyDeleteView.as_view(), name='delete-specialty'),
]


templates = [
    path('doctors_list/', TemplateView.as_view(template_name='doctors.html'), name='doctors_list'),
    path('appointment/<int:pk>/<int:id>/', TemplateView.as_view(template_name='book_appoinment.html'), name='book_appoinment'),
    path('doctor_appointments/<int:pk>/', TemplateView.as_view(template_name='doctor_appointments.html'), name='doctor_appointments'),
    path('prescribe/', TemplateView.as_view(template_name='prescription.html'), name='prescription'),
    path('call/<str:pk>', TemplateView.as_view(template_name= 'appoinment_call.html'), name='call'),
    path('appointment_details/<int:id>/', TemplateView.as_view(template_name='appointment_details.html'), name='appointment_details'),
    path('patient_appointment/', TemplateView.as_view(template_name='patient_appointment.html'), name='patient_appointment'),
    path('patient_prescription/<int:id>/', TemplateView.as_view(template_name='patient_prescription.html'), name='patient_prescription'),
    
    path('doctor/dashboard/', TemplateView.as_view(template_name='doctor_dashboard.html'), name='doctor_dashboard'),
    path('update_doctor/', TemplateView.as_view(template_name='update_doctor.html'), name='update_doctor'),

    
    
    path('doctor-availability/update/', TemplateView.as_view(template_name='doctor_availability.html'), name='doctor_availability'),
    
    
    path('admin-dashboard/', TemplateView.as_view(template_name='admin_dashboard.html'), name='admin_dashboard'),
    path('create-doctor/', TemplateView.as_view(template_name='doctor_create.html'), name='create_doctor'),
    
]

urlpatterns = urlpatterns + templates
