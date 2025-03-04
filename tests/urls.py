from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView

from .views import *

router = DefaultRouter()
router.register(r'test-types', TestTypeViewSet)
router.register(r'test-orders', TestOrderViewSet)
router.register(r'test-collection-assignments', TestCollectionAssignmentViewSet)
router.register(r'test-results', TestResultViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  # Include all the router-generated URLs
    path('api/test-type/create/', TestTypeCreateView.as_view(), name='test-type-create'),
    
    path('api/update-assignment-status/<int:pk>/', UpdateAssignmentStatusAPIView.as_view(), name='update_assignment_status_api'),
    path('api/update-assignment-collector/<int:id>/', UpdateAssignmentCollectorAPIView.as_view(), name='update_assignment_collector'),
    path('api/upload-result/<int:id>/', UploadTestResultView.as_view(), name='upload_test_result'),
    path('api/test-assignments/', TestAssignments.as_view(), name='staff_dashboard_api'),
    path('api/test-result/delete/', TestResultDeleteView.as_view(), name='test-result-delete'),
]


# Template urls

urlpatterns += [
    path('all_tests/', TemplateView.as_view(template_name='all_tests.html'), name="all_tests"),
    path('test-assignments/', TemplateView.as_view(template_name='test-assignments.html'), name='staff_dashboard'),
]
