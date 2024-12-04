from django.urls import path
from django.views.generic import TemplateView
from .views import (
    DoctorListCreateView, DoctorDetailView,
    PatientListCreateView, PatientDetailView,
    AppointmentListCreateView, AppointmentDetailView,
    TreatmentListCreateView, TreatmentDetailView,
    AppointmentCreateView, AppointmentListView, PatientAppointmentDetailView,
    DoctorAppointmentListView,
    PrescriptionListCreateView, PrescriptionRetrieveUpdateDestroyView,
    # get_agora_token,
)

urlpatterns = [

    # Doctor URLs
    path('doctors/', DoctorListCreateView.as_view(), name='doctor-list-create'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),

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
    path('api/doctor/<int:doctor_id>/appointments/', DoctorAppointmentListView.as_view(), name='doctor_appointments'),
    
    #prescription urls
    path('prescriptions/', PrescriptionListCreateView.as_view(), name='prescription-list-create'),
    path('prescriptions/<int:pk>/', PrescriptionRetrieveUpdateDestroyView.as_view(), name='prescription-detail'),
    
    # path('api/get-agora-token/', get_agora_token, name='get_agora_token'),


]


templates = [
    path('doctors_list/', TemplateView.as_view(template_name='doctors.html'), name='doctors_list'),
    path('appointment/<int:pk>/', TemplateView.as_view(template_name='book_appoinment.html'), name='book_appoinment'),
    path('doctor_appointments/<int:pk>/', TemplateView.as_view(template_name='doctor_appointments.html'), name='doctor_appointments'),
    path('prescribe/', TemplateView.as_view(template_name='prescription.html'), name='prescription'),
    path('call/<str:pk>', TemplateView.as_view(template_name= 'appoinment_call.html'), name='call'),
    path('appointment_details/<int:id>/', TemplateView.as_view(template_name='appointment_details.html'), name='appointment_details'),

]

urlpatterns = urlpatterns + templates
