from django.db import models
from accounts.models import CustomUser
from django.conf import settings
from django.contrib.auth import get_user_model
from .utils import RtcTokenBuilder 

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

    def __str__(self):
        return f"Dr. {self.full_name} ({self.specialty})"

class Patient(models.Model):
    name = models.CharField(max_length=150, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.CharField(max_length=255, blank=True)
    medical_history = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15)
    blood_type = models.CharField(max_length=5, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B-'), ('O+', 'O-'), ('O-', 'O-'), ('AB+', 'AB-')])
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name}"

class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Optional link to User model
    patient_name = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    appointment_date = models.DateTimeField(null=True, blank=True)
    video_link = models.CharField(max_length=500, null=True, blank=True) 
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'appointment_date'], name='unique_doctor_appointment')
        ]
        
    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
        # Generate video link only if it doesn't already exist
        if self.appointment_date and not self.video_link:
            self.generate_agora_link()
            super().save(update_fields=['video_link'])
    
    def generate_agora_link(self):
        app_id = settings.AGORA_APP_ID
        app_certificate = settings.AGORA_APP_CERTIFICATE
        
        # Generate Agora video link with a unique channel name
        channel_name = f"appointment_{self.id}_{int(self.appointment_date.timestamp())}"
        expiration_time = int(self.appointment_date.timestamp()) + 7200  # Token valid for 2 hours
        
        # Generate token using RtcTokenBuilder
        token = RtcTokenBuilder.buildTokenWithUid(
            app_id, app_certificate, channel_name, 0,  # UID 0 for guests
            expiration_time, expiration_time
        )
        
        # Construct the video link
        self.video_link = f"http://127.0.0.1:8000/call/{channel_name}?token={token}"


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

    def __str__(self):
        return f"Prescription for {self.patient} - {self.treatment_date}"
