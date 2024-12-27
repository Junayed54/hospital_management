from django.urls import path
from .views import UserSignupView, UserLoginView, LogoutView, PasswordUpdateView
from django.views.generic import TemplateView


urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('signin/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-update/', PasswordUpdateView.as_view(), name='password_update'),

]

#Templates urls
urlpatterns += [
    path('register/', TemplateView.as_view(template_name='signup.html'), name='register'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),

    path('appointment/<int:pk>/', TemplateView.as_view(template_name='book_appoinment.html'), name='book_appoinment'),
]
