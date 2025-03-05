from django.db import models
from patients.models import Patient
from django.contrib.auth import get_user_model
User = get_user_model()

    



    
    
class TestType(models.Model):
    name = models.CharField(max_length=255)  # Name of the test (e.g., Blood Test, Urine Test)
    description = models.TextField(blank=True, null=True)  # Optional description of the test
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price for the test
    
    def __str__(self):
        return self.name


class TestOrder(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('processing', 'Processing'),
        ('sample_collected', 'Sample Collected'),
        ('in_analysis', 'In Analysis'),
        ('completed', 'Completed'),
        ('result_delivered', 'Result Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='requested')
    collection_time = models.DateTimeField(null=True, blank=True)
    result = models.TextField(blank=True, null=True, default="")
    result_sent = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    total_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        """Set total_pay based on test_type price if not already set."""
        if not self.total_pay:
            self.total_pay = self.test_type.price  # Static pricing
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Test Order for {self.user} - {self.test_type}"

    def get_patient_contact_details(self):
        """Fetch contact details from the associated User model via Patient."""
        if self.patient and self.patient.user:
            return {
                "name": self.patient.user.get_full_name(),
                "email": self.patient.user.email,
                "phone_number": self.patient.user.phone_number,
            }
        return {}

class TestCollectionAssignment(models.Model):
    test_order = models.ForeignKey(TestOrder, on_delete=models.CASCADE)
    collector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collections')  # Collector assigned to this order
    status = models.CharField(
        max_length=50, 
        choices=[('Assigned', 'Assigned'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
        default='Assigned'
    )
    collection_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Collection Assignment for Order {self.test_order.id}"

class TestResult(models.Model):
    test_order = models.OneToOneField(TestOrder, on_delete=models.CASCADE)
    result = models.TextField(null=True, blank=True)  # Store the actual test result (blood count, urine level, etc.)
    result_date = models.DateTimeField(auto_now_add=True)  # Date when the result was processed
    result_sent = models.BooleanField(default=False)  # Whether the result has been sent to the patient
    result_file = models.FileField(upload_to='test_results/', blank=True, null=True)
    def __str__(self):
        return f"Result for {self.test_order.user.patient_profile} - {self.test_order.test_type.name}"


