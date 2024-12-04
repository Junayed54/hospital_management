from rest_framework import serializers
from .models import Doctor, Patient, Appointment, Treatment, Prescription
from accounts.serializers import CustomUserSerializer
class DoctorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id','full_name', 'user', 'specialty', 'license_number', 'bio', 'experience_years', 'education', 'consultation_fee', 'contact_email', 'contact_phone']

class PatientSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'date_of_birth', 'gender', 'address', 'medical_history', 'emergency_contact', 'blood_type', 'insurance_provider', 'insurance_policy_number']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'user', 'patient_name', 'phone_number', 'email', 'address', 'appointment_date', 'video_link']
        extra_kwargs = {
            'appointment_date': {'required': True},  # Ensure this field is required
        }

    def create(self, validated_data):
        # Validate appointment_date explicitly
        if not validated_data.get('appointment_date'):
            raise serializers.ValidationError({"appointment_date": "This field is required."})
        
        return super().create(validated_data)

    def create(self, validated_data):
        """
        Overriding create to handle linking an appointment with an existing user if available.
        """
        request_user = self.context.get('request').user  # Access user from context
        if request_user.is_authenticated:
            validated_data['user'] = request_user  # Link appointment to authenticated user
        return super().create(validated_data) 
        
        
class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = ['id', 'patient', 'doctor', 'appointment', 'diagnosis', 'prescription', 'treatment_date', 'follow_up_date', 'treatment_notes', 'cost']





class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            'id', 'doctor', 'patient', 'diagnosis', 'prescription',
            'treatment_date', 'follow_up_date', 'treatment_notes',
            'cost', 'published'
        ]
        read_only_fields = ['doctor', 'patient', 'published'] 