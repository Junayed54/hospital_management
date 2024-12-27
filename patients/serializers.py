from rest_framework import serializers
from .models import Patient, BPLevel, SugarLevel, HeartRate, CholesterolLevel

class BPLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BPLevel
        fields = ['date', 'systolic', 'diastolic']

class SugarLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SugarLevel
        fields = ['date', 'level']

class HeartRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartRate
        fields = ['date', 'rate']

class CholesterolLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CholesterolLevel
        fields = ['date', 'level']

class PatientSerializer(serializers.ModelSerializer):
    bp_levels = BPLevelSerializer(many=True, read_only=True)
    sugar_levels = SugarLevelSerializer(many=True, read_only=True)
    heart_rates = HeartRateSerializer(many=True, read_only=True)
    cholesterol_levels = CholesterolLevelSerializer(many=True, read_only=True)
    consulting_doctor = serializers.CharField(source='doctor.name', read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'age', 'gender', 'blood_type', 'consulting_doctor',
            'bp_levels', 'sugar_levels', 'heart_rates', 'cholesterol_levels'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'age': {'required': False, 'allow_null': True},
            'gender': {'required': False},
            'blood_type': {'required': False},
        }