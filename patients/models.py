from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from datetime import date, timedelta

class Patient(models.Model):
    name = models.CharField(max_length=150, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile', null=True, blank=True)  # Allow user to be optional
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)  # Add age as a field
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    
    # Address-related fields
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Latitude
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Longitude
    location = models.JSONField(blank=True, null=True)  # JSON field to store Google Maps response (address components, country, city, etc.)

    medical_history = models.TextField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)
    blood_type = models.CharField(max_length=5, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')])
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        # If age is provided but date_of_birth is not, calculate date_of_birth
        if self.age is not None and self.date_of_birth is None:
            today = date.today()
            self.date_of_birth = today - timedelta(days=self.age * 365)  # Approximation
        elif self.date_of_birth is not None:
            # If date_of_birth is provided, calculate age
            today = date.today()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        super().save(*args, **kwargs)

    @property
    def calculated_age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return self.age

    def set_location(self, address, latitude, longitude, location_data):
        """Method to set location data, including Google Maps response."""
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.location = location_data

    def update_location_from_google(self, google_location_data):
        """Method to update location details from Google Maps response."""
        if google_location_data:
            self.latitude = google_location_data.get('lat')
            self.longitude = google_location_data.get('lng')
            self.location = google_location_data
            self.save()
            
            
            
class BPLevel(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bp_levels')
    systolic = models.PositiveIntegerField()  # Upper value
    diastolic = models.PositiveIntegerField()  # Lower value
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"BP {self.systolic}/{self.diastolic} for {self.patient.name} on {self.date}"

class SugarLevel(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sugar_levels')
    level = models.FloatField()  # Measured in mg/dL or mmol/L
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"Sugar {self.level} for {self.patient.name} on {self.date}"

class HeartRate(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='heart_rates')
    rate = models.PositiveIntegerField()  # Measured in beats per minute (BPM)
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"Heart Rate {self.rate} BPM for {self.patient.name} on {self.date}"

class CholesterolLevel(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='cholesterol_levels')
    level = models.FloatField()  # Measured in mg/dL
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"Cholesterol {self.level} for {self.patient.name} on {self.date}"