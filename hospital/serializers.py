from rest_framework import serializers
from django.db import transaction
from .models import Doctor, Appointment, Treatment, Prescription, Medication, Notification, Test
from accounts.serializers import CustomUserSerializer
from patients.serializers import PatientSerializer
class DoctorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id','full_name', 'user', 'specialty', 'license_number', 'bio', 'experience_years', 'education', 'consultation_fee', 'contact_email', 'contact_phone']

# class PatientSerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer(read_only=True)

#     class Meta:
#         model = Patient
#         fields = ['id', 'user', 'date_of_birth', 'gender', 'address', 'medical_history', 'emergency_contact', 'blood_type', 'insurance_provider', 'insurance_policy_number']

class AppointmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'patient_name', 'phone_number', 'email', 'address', 'appointment_date', 'video_link', 'patient_problem', 'status']
        extra_kwargs = {
            'appointment_date': {'required': True},  # Ensure this field is required
        }

    def create(self, validated_data):
        """
        Overriding create to validate the appointment_date and link an appointment 
        with the authenticated user if available.
        """
        # Validate appointment_date explicitly
        if not validated_data.get('appointment_date'):
            raise serializers.ValidationError({"appointment_date": "This field is required."})

        # Access user from context and link to the appointment
        request_user = self.context.get('request').user
        if request_user and request_user.is_authenticated:
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
    medications = MedicationSerializer(many=True, required=False)
    tests = TestSerializer(many=True, required=False)
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'doctor', 'patient', 'appointment', 'diagnosis',
            'prescription', 'treatment_date', 'follow_up_date',
            'treatment_notes', 'cost', 'published', 'next_appointment_date',
            'treatment_result', 'medications', 'tests'
        ]

    def create(self, validated_data):
        medications_data = validated_data.pop('medications', [])
        tests_data = validated_data.pop('tests', [])

        with transaction.atomic():
            prescription = Prescription.objects.create(**validated_data)

            # Bulk create medications
            Medication.objects.bulk_create([
                Medication(prescription=prescription, **medication_data)
                for medication_data in medications_data
            ])

            # Bulk create tests
            Test.objects.bulk_create([
                Test(prescription=prescription, **test_data)
                for test_data in tests_data
            ])

        return prescription

    def update(self, instance, validated_data):
        medications_data = validated_data.pop('medications', [])
        tests_data = validated_data.pop('tests', [])

        # Update prescription fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        with transaction.atomic():
            # Update medications
            self._update_or_create_related_objects(
                instance, medications_data, Medication, 'medications'
            )

            # Update tests
            self._update_or_create_related_objects(
                instance, tests_data, Test, 'tests'
            )

        return instance

    def _update_or_create_related_objects(self, instance, related_data, model_class, related_field_name):
        """
        Helper method to update or create related objects.
        """
        related_manager = getattr(instance, related_field_name)
        existing_objects = {obj.id: obj for obj in related_manager.all()}

        # Track IDs to retain
        retain_ids = []

        for data in related_data:
            obj_id = data.get('id')
            if obj_id and obj_id in existing_objects:
                # Update existing object
                obj = existing_objects[obj_id]
                for attr, value in data.items():
                    setattr(obj, attr, value)
                obj.save()
                retain_ids.append(obj_id)
            else:
                # Create new object
                model_class.objects.create(**data, prescription=instance)

        # Delete objects not included in the update
        to_delete_ids = set(existing_objects.keys()) - set(retain_ids)
        model_class.objects.filter(id__in=to_delete_ids).delete()


        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        