from django.urls import path
from django.views.generic import TemplateView
from .views import (
    PaymentMethodListCreateView, PaymentMethodDetailView,
    PaymentListCreateView, PaymentDetailView,
    TransactionDetailView, UserPaymentSummaryView
)


urlpatterns = [
    # PaymentMethod URLs
    path('payment-methods/', PaymentMethodListCreateView.as_view(), name='payment-method-list'),
    path('payment-methods/<int:pk>/', PaymentMethodDetailView.as_view(), name='payment-method-detail'),

    # Payment URLs
    path('payments/', PaymentListCreateView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),

    # Transaction URLs
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),

    # Payment Summary
    path('payments/summary/', UserPaymentSummaryView.as_view(), name='user-payment-summary'),
]



urlpatterns += [
    path('payment_methods/', TemplateView.as_view(template_name='payment_methods.html'), name='payment_methods'),
    path('payments/', TemplateView.as_view(template_name='payments.html'), name='payments'), 
]

