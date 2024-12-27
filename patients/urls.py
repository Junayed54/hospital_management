from django.urls import path
from .views import PatientDashboardAPIView, PatientAppointmentsView, UpdatePatientView
from django.views.generic import TemplateView
urlpatterns = [
    path('api/dashboard/', PatientDashboardAPIView.as_view(), name='patient_dashboard_api'),
    path('api/patient-appointments/', PatientAppointmentsView.as_view(), name='patient-appointments'),
    path('patient/update/', UpdatePatientView.as_view(), name='update_patient'),
]

# Templates
urlpatterns += [
    path('pateient-dashboard/', TemplateView.as_view(template_name='patient_dashboard.html'), name='pateient_dashboard'),
    path('patient-update/', TemplateView.as_view(template_name='update_patient.html'), name='patient-update'),
]
