from django.urls import path
from .views import *
from django.views.generic import TemplateView

urlpatterns = [
    path('api/caregiver/create/', CaregiverCreateView.as_view(), name='caregiver-create'),

    path('api/care-requests/', CareRequestListCreateAPIView.as_view(), name='care_request_list_create'),
    path('api/assign-care-requests/', AssignCaregiverAPIView.as_view(), name='assign_care_request'),
    path('api/update-assignment-collector/<int:pk>/<str:action>/', CareRequestUpdateAPIView.as_view(), name='care_request_update'),
    
    path('care-requests/status/', CareRequestStatusView.as_view(), name='care_requests_status'),

    path('care-requests/<int:pk>/update-status/', UpdateCareRequestStatusView.as_view(), name='update_care_request_status'),
]




urlpatterns += [
    path('create-care-giver/', TemplateView.as_view(template_name='care-giver-create.html'), name='create-care-giver'),
    path('caregiver_request/', TemplateView.as_view(template_name='care-request.html'), name='care-request'),
    path('caregiver-request-list/', TemplateView.as_view(template_name='care-requests-list.html'), name='care-requests-list'),
    path('care-requests-status/', TemplateView.as_view(template_name='care-request-status.html'), name='care-requests-status'),
]
