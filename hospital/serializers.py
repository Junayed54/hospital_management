from rest_framework import serializers
from django.db import transaction
from .models import *
from accounts.serializers import CustomUserSerializer
from patients.serializers import PatientSerializer
from datetime import datetime, timedelta


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DoctorAvailability
        fields = [
            'id',
            'doctor',
            'date',
            'start_time',
            'session_duration',
            'max_patients',
            'booked_patients',
        ]
        read_only_fields = ['booked_patients']

    def validate(self, data):
        """
        Validate session_duration and max_patients to ensure logical values.
        """
        if data.get('max_patients', 1) <= 0:
            raise serializers.ValidationError({"max_patients": "The maximum number of patients must be at least 1."})
        if data.get('session_duration', 0) <= 0:
            raise serializers.ValidationError({"session_duration": "Session duration must be greater than 0 minutes."})

        # Ensure no other availability exists for the same doctor at the same date and time
        doctor = data.get('doctor')
        date = data.get('date')
        start_time = data.get('start_time')

        # Check if an availability exists for this doctor at the same time
        if DoctorAvailability.objects.filter(doctor=doctor, date=date, start_time=start_time).exists():
            raise serializers.ValidationError("This doctor already has availability at this date and time.")

        return data

    def create(self, validated_data):
        """
        Ensure unique availability per doctor, date, and start time.
        """
        availability = super().create(validated_data)
        return availability

    def update(self, instance, validated_data):
        """
        Allow updating of availability details while ensuring data integrity.
        """
        # Check for uniqueness again when updating
        doctor = validated_data.get('doctor', instance.doctor)
        date = validated_data.get('date', instance.date)
        start_time = validated_data.get('start_time', instance.start_time)

        # Ensure no other availability exists for the same doctor at the same date and time
        if DoctorAvailability.objects.filter(doctor=doctor, date=date, start_time=start_time).exclude(id=instance.id).exists():
            raise serializers.ValidationError("This doctor already has availability at this date and time.")

        return super().update(instance, validated_data)

class CertificationFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationFile
        fields = ['id', 'file']

class DoctorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    availability = DoctorAvailabilitySerializer(many=True, read_only=True)
    certifications = CertificationFileSerializer(many=True, read_only=True)  # Nested certifications

    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'user', 'specialty', 'license_number', 'bio', 'experience_years', 
                  'education', 'consultation_fee', 'contact_email', 'contact_phone', 'availability', 'certifications']
    # def create(self, validated_data):
    #     # Extract user data
    #     user_data = validated_data.pop('user')
    #     user = User.objects.create_user(**user_data)

    #     # Create doctor
    #     doctor = Doctor.objects.create(user=user, **validated_data)
    #     return doctor
    
    
# class PatientSerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer(read_only=True)

#     class Meta:
#         model = Patient
#         fields = ['id', 'user', 'date_of_birth', 'gender', 'address', 'medical_history', 'emergency_contact', 'blood_type', 'insurance_provider', 'insurance_policy_number']


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    doctor_speciality = serializers.SerializerMethodField()
    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor',  # Derived from doctor_id
            'doctor_name',
            'doctor_speciality',
            'patient',  # Derived internally for authenticated users or anonymous creation
            'patient_name',
            'phone_number',
            'email',
            'address',
            'appointment_date',
            'video_link',
            'patient_problem',
            'status',
            'note'
        ]
        extra_kwargs = {
            'appointment_date': {'read_only': True},  # Derived dynamically
            'doctor': {'read_only': True},  # Derived from doctor_id
            'patient': {'read_only': True},  # Managed internally
        }
        
    def get_doctor_name(self, obj):
        return obj.doctor.full_name if obj.doctor else None

    def get_doctor_speciality(self, obj):
        return obj.doctor.specialty if obj.doctor else None
    
    
    def create(self, validated_data):
        """
        Automatically assigns an appointment time based on slot availability.
        """
        # Get IDs from the request
        request = self.context['request']
        doctor_id = request.data.get('doctor_id')
        availability_id = request.data.get('slot_id')
        # patient = validated_data.get('patient')
        if not doctor_id:
            raise serializers.ValidationError({"doctor_id": "This field is required."})
        if not availability_id:
            raise serializers.ValidationError({"slot_id": "This field is required."})

        # Resolve doctor and availability (slot)
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError({"doctor_id": "Invalid doctor ID."})

        try:
            availability = DoctorAvailability.objects.get(id=availability_id, doctor=doctor)
        except DoctorAvailability.DoesNotExist:
            raise serializers.ValidationError({"slot_id": "Invalid slot ID for the specified doctor."})

        # Check for slot availability
        if availability.booked_patients >= availability.max_patients:
            # Handle waiting list addition
            patient_name = validated_data.get('patient_name')
            phone_number = validated_data.get('phone_number')
            email = validated_data.get('email')

            # Check if the patient exists or create an anonymous patient
            patient, created = Patient.objects.get_or_create(
                name=patient_name,
                # defaults={'phone_number': phone_number, 'email': email},
            )

            # Add to the waiting list
            WaitingList.objects.create(
                availability=availability,
                patient=patient
            )
            raise serializers.ValidationError({"slot_id": "No slots available. Added to the waiting list."})

        # Calculate appointment time
        time_per_patient = availability.calculate_time_per_patient()
        current_time = datetime.combine(availability.date, availability.start_time)
        existing_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__date=availability.date,
            status='accepted'
        ).order_by('appointment_date')

        if existing_appointments.exists():
            last_appointment_time = existing_appointments.last().appointment_date
            appointment_time = last_appointment_time + timedelta(minutes=time_per_patient)
        else:
            appointment_time = current_time

        # Validate appointment time
        if appointment_time.time() >= availability.get_end_time():
            raise serializers.ValidationError({"slot_id": "No available slots within working hours."})

        # Update availability and save appointment
        availability.booked_patients += 1
        availability.save()

        # Populate the appointment instance
        validated_data['doctor'] = doctor
        validated_data['appointment_date'] = appointment_time
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Override update to handle status changes, particularly cancellations.
        """
        # If status is being updated to 'cancelled', update doctor availability
        if validated_data.get('status') == 'cancelled' and instance.status != 'cancelled':
            availability = DoctorAvailability.objects.filter(
                doctor=instance.doctor,
                date=instance.appointment_date.date()
            ).first()

            if availability:
                availability.booked_patients = max(0, availability.booked_patients - 1)
                availability.save()

        return super().update(instance, validated_data)

class WaitingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingList
        fields = [
            'id',
            'availability',
            'patient',
            'requested_at',
        ]
        read_only_fields = ['requested_at']

    def validate(self, data):
        """
        Ensure that the patient is not already on the waiting list for the same availability.
        """
        if WaitingList.objects.filter(
            availability=data.get('availability'),
            patient=data.get('patient')
        ).exists():
            raise serializers.ValidationError("This patient is already on the waiting list for this availability.")
        return data

    def create(self, validated_data):
        """
        Add a patient to the waiting list.
        """
        waiting_entry = super().create(validated_data)
        return waiting_entry
    
    

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
    doctor_name = serializers.SerializerMethodField()
    doctor_speciality = serializers.SerializerMethodField()
    doctor = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Prescription
        fields = [
            'id', 'doctor', 'doctor_name', 'doctor_speciality', 'patient', 'appointment', 'diagnosis',
            'prescription', 'treatment_date', 'follow_up_date',
            'treatment_notes', 'cost', 'published', 'next_appointment_date',
            'treatment_result', 'medications', 'tests'
        ]
        
        
    def get_doctor_name(self, obj):
        """Fetches the full name of the doctor"""
        return obj.doctor.full_name if obj.doctor else None

    def get_doctor_speciality(self, obj):
        """Fetches the specialty of the doctor"""
        return obj.doctor.specialty if obj.doctor and hasattr(obj.doctor, 'speciality') else None

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
        