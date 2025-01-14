from django.db import models
from patients.models import Patient
from django.contrib.auth import get_user_model
User = get_user_model()
class Caregiver(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='caregiver')
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='caregivers/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    certifications = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    available_from = models.DateTimeField()
    available_to = models.DateTimeField()

    def __str__(self):
        return self.full_name


class CareRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='care_requests_patents')
    caregiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='care_requests_caregiver')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)  # Description of the care needed
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Care Request from {self.patient} to {self.caregiver} - {self.status}"



class CareSchedule(models.Model):
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10)  # e.g., Monday, Tuesday, etc.
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.caregiver} - {self.day_of_week}: {self.start_time} to {self.end_time}"



class CaregiverRating(models.Model):
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caregiver_ratings')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_ratings')
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating for {self.caregiver} from {self.patient} - {self.rating} stars"


class CaregiverPayment(models.Model):
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caregiver_payments')
    care_request = models.ForeignKey(CareRequest, on_delete=models.CASCADE, related_name='request_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('pending', 'Pending')])

    def __str__(self):
        return f"Payment of {self.amount} for {self.caregiver} - {self.payment_status}"


class CaregiverAvailability(models.Model):
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability')
    available_date = models.DateField()
    available_start_time = models.TimeField()
    available_end_time = models.TimeField()

    def __str__(self):
        return f"{self.caregiver} available on {self.available_date} from {self.available_start_time} to {self.available_end_time}"



class PatientCaregiverInteraction(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_interactions')
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caregiver_interactions')
    interaction_date = models.DateTimeField(auto_now_add=True)
    interaction_details = models.TextField()

    def __str__(self):
        return f"Interaction between {self.patient} and {self.caregiver} on {self.interaction_date}"
