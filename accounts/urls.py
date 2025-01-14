from django.urls import path
from .views import *
from django.views.generic import TemplateView


urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('signin/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-update/', PasswordUpdateView.as_view(), name='password_update'),


    path('api/create-department/', CreateDepartmentView.as_view(), name='create-department'),
    path('api/departments/', DepartmentListView.as_view(), name='department_list'),
    path('api/departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    
    path('api/users/care-givers/', CareGiverUsersAPIView.as_view(), name='care_giver_users'),

]

#Templates urls
urlpatterns += [
    path('register/', TemplateView.as_view(template_name='signup.html'), name='register'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),

    path('appointment/<int:pk>/', TemplateView.as_view(template_name='book_appoinment.html'), name='book_appoinment'),
    
    path('create-department/', TemplateView.as_view(template_name='create-department.html'), name='create_department'),
    path('departments/', TemplateView.as_view(template_name='all-departments.html'), name='all-departments'),
    path('departments/<int:pk>/', TemplateView.as_view(template_name='department-details.html'), name='department-details'),
]


