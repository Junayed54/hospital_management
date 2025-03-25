from rest_framework import serializers
from .models import *

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
        
class ReportCategorySerializer(serializers.ModelSerializer):
    """Serializes report categories (e.g., Blood Test, X-Ray)"""
    class Meta:
        model = ReportCategory
        fields = ['id', 'name']

class PatientReportTypeSerializer(serializers.ModelSerializer):
    """Serializes specific test types (e.g., CBC, Lipid Profile) under categories"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ReportType
        fields = ['id', 'name', 'category', 'category_name']
        extra_kwargs = {'category': {'write_only': True}} 

class PatientReportSerializer(serializers.ModelSerializer):
    """Serializes patient reports with linked test type"""
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Automatically assigns patient
    report_type = PatientReportTypeSerializer()  # Nested serializer for test type details

    class Meta:
        model = PatientReport
        fields = ['id', 'patient', 'patient_username', 'title', 'report_type', 'description', 'report_file', 'uploaded_at']
        read_only_fields = ['patient', 'uploaded_at']

class PatientReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating patient reports, using report_type ID or full object"""
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Hidden field to use current logged-in user
    report_type = serializers.PrimaryKeyRelatedField(
        queryset=ReportType.objects.all(),
        required=True  # Ensures the field is required
    )
    report_type_name = serializers.SerializerMethodField()  

    class Meta:
        model = PatientReport
        fields = ['title', 'report_type', 'report_type_name', 'description', 'report_file', 'patient']

    def create(self, validated_data):
        """Ensures the authenticated user is assigned as the patient"""
        validated_data['patient'] = self.context['request'].user  # This line is redundant now with perform_create
        return super().create(validated_data)
    
    def get_report_type_name(self, obj):
        """Return the name of the related report type"""
        return obj.report_type.name

    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['report_type'].queryset = ReportType.objects.all()

class PatientPrescriptionSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Automatically assign patient

    class Meta:
        model = PatientPrescription
        fields = ['id', 'patient', 'patient_username', 'title', 'doctor_name', 'prescription_date', 'description', 'prescription_file', 'uploaded_at']
        read_only_fields = ['patient', 'uploaded_at']  # Patient is now read-only

    
    def perform_create(self, serializer):
        print(self.request.user)  # Debugging: Check if user is properly authenticated
        serializer.save(patient=self.request.user)