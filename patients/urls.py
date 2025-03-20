from django.urls import path, include
from .views import *
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'report-categories', ReportCategoryViewSet)
router.register(r'test-types', TestTypeViewSet)
router.register(r'patient-reports', PatientReportViewSet, basename='patient-report')
router.register(r'user-prescriptions', PatientPrescriptionViewSet, basename='patient-prescription')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', PatientDashboardAPIView.as_view(), name='patient_dashboard_api'),
    path('api/patient-appointments/', PatientAppointmentsView.as_view(), name='patient-appointments'),
    path('patient/update/', UpdatePatientView.as_view(), name='update_patient'),
    path('api/patient-details/', PatientDetailAPIView.as_view(), name='patient-details'),
]

# Templates
urlpatterns += [
    path('pateient-dashboard/', TemplateView.as_view(template_name='patient_dashboard.html'), name='pateient_dashboard'),
    path('patient-update/', TemplateView.as_view(template_name='update_patient.html'), name='patient-update'),
]
