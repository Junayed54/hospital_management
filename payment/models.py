from django.db import models
from django.conf import settings


# PaymentMethod Model
class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Name of the payment method (e.g., bKash, Nagad, Credit Card)")
    description = models.TextField(blank=True, null=True, help_text="Optional description of the payment method")
    is_active = models.BooleanField(default=True, help_text="Indicates if this payment method is currently active")
    requires_mobile_number = models.BooleanField(default=False, null=True, blank=True, help_text="Does this method require a mobile number? (e.g., bKash, Nagad)")
    requires_transaction_id = models.BooleanField(default=True, null=True, blank=True, help_text="Does this method require a transaction ID?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'


# Payment Model
class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="The payment amount")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending', help_text="Current status of the payment")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction ID provided by the payment gateway")
    mobile_number = models.CharField(max_length=15, blank=True, null=True, help_text="Mobile number used for payment, if applicable")
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.amount} by {self.user}"

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']


# Transaction Model
class Transaction(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="transaction")
    gateway_response = models.JSONField(blank=True, null=True, help_text="Response from the payment gateway")
    success = models.BooleanField(default=False, help_text="Whether the transaction was successful")

    def __str__(self):
        return f"Transaction for Payment {self.payment.id} - Success: {self.success}"

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
