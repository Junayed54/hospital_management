# serializers.py
from rest_framework import serializers
from .models import Caregiver, CareRequest, CaregiverPayment, CaregiverRating, PatientCaregiverInteraction



class CaregiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caregiver
        fields = '__all__'  # This will include all fields in the model

    def create(self, validated_data):
        # Convert to timezone-aware datetime if it's naive
        available_to_naive = validated_data.get('available_to', None)
        if available_to_naive:
            available_to_aware = timezone.make_aware(available_to_naive, timezone.get_current_timezone())
            validated_data['available_to'] = available_to_aware

        caregiver = super().create(validated_data)
        return caregiver
class CareRequestSerializer(serializers.ModelSerializer):
    # Adding custom fields for patient and caregiver
    patient = serializers.SerializerMethodField()
    caregiver = serializers.SerializerMethodField()

    class Meta:
        model = CareRequest
        fields = '__all__'
        read_only_fields = ['patient']  # Keep patient as read-only

    def get_patient(self, obj):
        # Return serialized data for the patient
        if obj.patient:
            return {
                "id": obj.patient.id,
                "name": obj.patient.patient_profile.name,  # Adjust field names as per your model
            }
        return None

    def get_caregiver(self, obj):
        # Return serialized data for the caregiver
        if obj.caregiver:
            return {
                "id": obj.caregiver.id,
                "name": obj.caregiver.caregiver.full_name,  # Adjust field names as per your model
            }
        return None
    
    
    
class CaregiverPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaregiverPayment
        fields = '__all__'

class CaregiverRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaregiverRating
        fields = '__all__'

class PatientCaregiverInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientCaregiverInteraction
        fields = '__all__'
