from rest_framework import serializers
from .models import Doctor, Patient, Appointment, Treatment, Prescription, Medication, Notification, Test
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
        fields = ['id', 'doctor', 'user', 'patient_name', 'phone_number', 'email', 'address', 'appointment_date', 'video_link', 'patient_problem']
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



class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name', 'dosage', 'frequency', 'duration', 'notes']





class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'test_name', 'test_description', 'test_date', 'result', 'status']

class PrescriptionSerializer(serializers.ModelSerializer):
    medications = MedicationSerializer(many=True, required=False)  # Optional
    tests = TestSerializer(many=True, required=False)  # Optional

    class Meta:
        model = Prescription
        fields = [
            'id', 'doctor', 'patient', 'appointment', 'diagnosis',
            'prescription', 'treatment_date', 'follow_up_date',
            'treatment_notes', 'cost', 'published', 'next_appointment_date',
            'treatment_result', 'medications', 'tests'
        ]

    def create(self, validated_data):
        medications_data = validated_data.pop('medications', [])  # Default to empty list if not provided
        tests_data = validated_data.pop('tests', [])  # Default to empty list if not provided
        prescription = Prescription.objects.create(**validated_data)

        # Create medications only if data is provided
        for medication_data in medications_data:
            Medication.objects.create(prescription=prescription, **medication_data)
        
        # Create tests only if data is provided
        for test_data in tests_data:
            Test.objects.create(prescription=prescription, **test_data)
        
        return prescription

    def update(self, instance, validated_data):
        medications_data = validated_data.pop('medications', [])
        tests_data = validated_data.pop('tests', [])
        
        # Update prescription fields
        instance.diagnosis = validated_data.get('diagnosis', instance.diagnosis)
        instance.prescription = validated_data.get('prescription', instance.prescription)
        instance.treatment_date = validated_data.get('treatment_date', instance.treatment_date)
        instance.follow_up_date = validated_data.get('follow_up_date', instance.follow_up_date)
        instance.treatment_notes = validated_data.get('treatment_notes', instance.treatment_notes)
        instance.cost = validated_data.get('cost', instance.cost)
        instance.published = validated_data.get('published', instance.published)
        instance.next_appointment_date = validated_data.get('next_appointment_date', instance.next_appointment_date)
        instance.treatment_result = validated_data.get('treatment_result', instance.treatment_result)
        instance.save()

        # Clear and update medications only if data is provided
        if medications_data:
            instance.medications.all().delete()
            for medication_data in medications_data:
                Medication.objects.create(prescription=instance, **medication_data)
        
        # Clear and update tests only if data is provided
        if tests_data:
            instance.tests.all().delete()
            for test_data in tests_data:
                Test.objects.create(prescription=instance, **test_data)
        
        return instance
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        