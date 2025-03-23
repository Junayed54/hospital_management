from django.db import models
from accounts.models import CustomUser
from django.conf import settings
from datetime import datetime, timedelta

from .utils import RtcTokenBuilder 
from patients.models import Patient
from django.contrib.auth import get_user_model
User = get_user_model()


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=150, default="")
    nid_number = models.CharField(max_length=20, unique=True, null=True, blank="True")  # New Field
    license_number = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)
    about = models.TextField(blank=True)  # New Field
    experience_years = models.IntegerField(default=0)
    education = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)  # New Field
    profile_picture = models.ImageField(upload_to="doctor_profiles/", blank=True, null=True)  # New Field

    def next_available_slot(self):
        from .models import DoctorAvailability  # Avoid circular imports
        from datetime import datetime
        now = datetime.now()
        next_slot = DoctorAvailability.objects.filter(
            doctor=self, 
            date__gte=now.date(),
            is_booked=False
        ).order_by('date', 'start_time').first()
        return next_slot

    def __str__(self):
        specialties = ", ".join([specialty.name for specialty in self.specialties.all()])
        return f"Dr. {self.full_name} ({specialties})" if specialties else f"Dr. {self.full_name}"


def certification_upload_path(instance, filename):
    """Generate a unique upload path for certification files."""
    return os.path.join('certifications', str(instance.doctor.id), filename)


class Specialty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="specialties", null=True, blank=True)  # One doctor can have multiple specialties
    name = models.CharField(max_length=100)
    services = models.TextField(blank=True, help_text="Comma-separated list of services")
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    about_service = models.TextField(blank=True, help_text="Details about the service provided")

    def __str__(self):
        return f"{self.name} ({self.user})"


class CertificationFile(models.Model):
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
        related_name='certifications'
    )
    file = models.FileField(upload_to=certification_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certification for {self.doctor.full_name}: {os.path.basename(self.file.name)}"



class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()  
    start_time = models.TimeField()  
    session_duration = models.PositiveIntegerField(help_text="Total session duration in minutes")  
    max_patients = models.PositiveIntegerField(default=1, help_text="Maximum number of patients for this session")
    booked_patients = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')

    def calculate_time_per_patient(self):
        """Calculate how much time each patient will receive."""
        return self.session_duration // self.max_patients

    def assign_appointment_time(self):
        """Assign specific times for all accepted appointments."""
        appointments = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date__date=self.date,
            status='accepted'
        ).order_by('created_at')

        time_per_patient = self.calculate_time_per_patient()
        current_time = datetime.combine(self.date, self.start_time)

        for appointment in appointments:
            appointment.appointment_date = current_time
            appointment.save(update_fields=['appointment_date'])
            current_time += timedelta(minutes=time_per_patient)

    def promote_pending_patient(self):
        """Promote the first pending patient to accepted if a slot becomes available."""
        pending_appointment = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date__date=self.date,
            status='pending'
        ).order_by('created_at').first()

        if pending_appointment:
            pending_appointment.status = 'accepted'
            pending_appointment.save(update_fields=['status'])
            self.assign_appointment_time()

    def get_end_time(self):
        """
        Calculate the end time based on the start time and session duration.
        """
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = start_datetime + timedelta(minutes=self.session_duration)
        return end_datetime.time()
    
    
    def __str__(self):
        return f"Availability for {self.doctor} on {self.date} ({self.session_duration} mins, {self.max_patients} patients)"



class WaitingList(models.Model):
    availability = models.ForeignKey(DoctorAvailability, on_delete=models.CASCADE, related_name='waiting_list')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)  # To prioritize by request time

    class Meta:
        unique_together = ('availability', 'patient')

    def __str__(self):
        return f"{self.patient} waiting for {self.availability}"



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
    note = models.TextField(null=True, blank=True)
    class Meta:
        # constraints = [
        #     models.UniqueConstraint(fields=['doctor', 'appointment_date'], name='unique_doctor_date'),
        #     models.UniqueConstraint(fields=['doctor', 'appointment_date', 'phone_number'], name='unique_doctor_appointment')
        # ]
        pass

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new instance

        # Save the instance first
        super().save(*args, **kwargs)

        # Handle video link generation for new appointments
        if is_new and self.appointment_date and not self.video_link:
            try:
                self.generate_agora_link()
                super().save(update_fields=['video_link'])
            except Exception as e:
                # Log the error for debugging purposes
                logger.error(f"Error generating Agora link for Appointment {self.id}: {str(e)}")

        # Assign appointment time for accepted appointments
        if is_new and self.status == 'accepted':
            availability = DoctorAvailability.objects.filter(
                doctor=self.doctor,
                date=self.appointment_date.date()
            ).first()

            if availability:
                try:
                    availability.assign_appointment_time()
                except Exception as e:
                    # Log the error for debugging purposes
                    logger.error(f"Error assigning appointment time for Appointment {self.id}: {str(e)}")

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
        """Cancel an appointment and handle promotion of pending patients."""
        if self.status in ['accepted', 'pending']:
            self.status = 'cancelled'
            self.save(update_fields=['status'])

            # Handle promotion of pending patients
            availability = DoctorAvailability.objects.filter(
                doctor=self.doctor,
                date=self.appointment_date.date()
            ).first()

            if availability:
                availability.promote_pending_patient()
        else:
            raise ValueError("Cannot cancel an appointment that has already been rejected or cancelled.")

        
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


