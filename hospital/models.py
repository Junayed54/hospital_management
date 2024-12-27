from django.db import models
from accounts.models import CustomUser
from django.conf import settings
from django.contrib.auth import get_user_model
from .utils import RtcTokenBuilder 
from patients.models import Patient
User = get_user_model()


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=150, default="")
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    education = models.CharField(max_length=200, blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)

    
    def next_available_slot(self):
        from .models import DoctorAvailability  # Avoid circular imports
        now = datetime.now()
        next_slot = DoctorAvailability.objects.filter(
            doctor=self, 
            date__gte=now.date(),
            is_booked=False
        ).order_by('date', 'start_time').first()
        return next_slot
    
    
    def __str__(self):
        return f"Dr. {self.full_name} ({self.specialty})"

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()  # Specific date for availability
    start_time = models.TimeField()  # Start time of availability
    end_time = models.TimeField()  # End time of availability
    max_patients = models.PositiveIntegerField(default=1)  # Maximum number of patients allowed
    booked_patients = models.PositiveIntegerField(default=0)  # Number of patients already booked

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')

    def is_available(self):
        """Check if there is still room for more patients."""
        return self.booked_patients < self.max_patients

    def __str__(self):
        return f"Availability for {self.doctor} on {self.date} from {self.start_time} to {self.end_time} (Booked: {self.booked_patients}/{self.max_patients})"



class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    patient_name = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    appointment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    video_link = models.CharField(max_length=500, null=True, blank=True)
    patient_problem = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'appointment_date'], name='unique_doctor_date'),
            models.UniqueConstraint(fields=['doctor', 'appointment_date', 'phone_number'], name='unique_doctor_appointment')
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs)
        if self.appointment_date and not self.video_link:
            try:
                self.generate_agora_link()
                super().save(update_fields=['video_link'])
            except Exception as e:
                # Handle or log the error
                pass
        else:
            super().save(*args, **kwargs)

    def generate_agora_link(self):
        app_id = settings.AGORA_APP_ID
        app_certificate = settings.AGORA_APP_CERTIFICATE
        channel_name = f"appointment_{self.id}_{int(self.appointment_date.timestamp())}"
        expiration_time = int(self.appointment_date.timestamp()) + 7200  # Token valid for 2 hours
        token = RtcTokenBuilder.buildTokenWithUid(
            app_id, app_certificate, channel_name, 0, expiration_time, expiration_time
        )
        self.video_link = f"http://127.0.0.1:8000/call/{channel_name}?token={token}"

    
    def cancel(self):
        if self.status not in ['accepted', 'rejected']:
            self.status = 'cancelled'
            self.save(update_fields=['status'])
        else:
            raise ValueError("Cannot cancel an appointment that has already been accepted or rejected.")
        
        
    def __str__(self):
        return f"{self.patient_name} - {self.doctor}"

class Treatment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    diagnosis = models.CharField(max_length=255)
    prescription = models.TextField()
    treatment_date = models.DateField()
    follow_up_date = models.DateField(blank=True, null=True)
    treatment_notes = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Treatment for {self.patient.name} on {self.treatment_date}"




class Prescription(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="prescription")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescription", null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="prescription")
    diagnosis = models.CharField(max_length=255)
    prescription = models.TextField()
    treatment_date = models.DateField()
    follow_up_date = models.DateField(blank=True, null=True)
    treatment_notes = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    published = models.BooleanField(default=False)  # New field
    next_appointment_date = models.DateField(blank=True, null=True)
    treatment_result = models.TextField(blank=True, null=True)  # New field for storing results
    created_at = models.DateField(blank=True, null=True, auto_now_add=True) #
    def __str__(self):
        return f"Prescription for {self.patient} on {self.treatment_date}"


class Test(models.Model):
    prescription = models.ForeignKey(
        'Prescription',
        on_delete=models.CASCADE,
        related_name='tests'
    )
    test_name = models.CharField(max_length=100)  # e.g., "Blood Test", "X-ray"
    test_description = models.TextField(blank=True, null=True)  # Additional details or instructions
    test_date = models.DateField(blank=True, null=True)  # Scheduled test date
    result = models.TextField(blank=True, null=True)  # Result of the test after completion
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('completed', 'Completed')], 
        default='pending'
    )

    def __str__(self):
        return f"{self.test_name} for {self.prescription.patient}"

class Medication(models.Model):
    prescription = models.ForeignKey ( 'Prescription', on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=100) 
    dosage = models.CharField(max_length=50) # e.g., "500 mg"
    frequency = models.CharField(max_length=50) # e.g., "Twice a day"
    duration = models.CharField(max_length=50) # e.g., "7 days"
    notes = models.TextField(blank=True, null=True) # Additional instructions
    
    def __str__(self): 
        return f"{self.name} - {self.dosage}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications") 
    message = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True) 
    read = models.BooleanField(default=False) 
    scheduled_time = models.DateTimeField() # When the notification should be sent 
    def __str__(self): 
        return f"Notification for {self.user.username} at {self.scheduled_time}"
