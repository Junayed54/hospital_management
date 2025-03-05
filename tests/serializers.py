from rest_framework import serializers
from .models import *
from patients.models import Patient  # Import the Patient model
from django.conf import settings


# Serializer for TestType model
class TestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestType
        fields = '__all__'  # Include all fields of the TestType model


# Serializer for TestOrder model
class TestResultSerializer(serializers.ModelSerializer):
    test_order = serializers.PrimaryKeyRelatedField(queryset=TestOrder.objects.all())  # Nested TestOrder serializer for test order details
    result_file= serializers.FileField(required=False)
    result_file_url = serializers.SerializerMethodField()
    # result = serializers.CharField(required=False)
    class Meta:
        model = TestResult
        fields = ['test_order', 'result', 'result_date', 'result_sent', 'result_file', 'result_file_url']

    def create(self, validated_data):
        # Create the TestResult instance and link it to the TestOrder
        test_result = TestResult.objects.create(**validated_data)
        return test_result
    
    def get_result_file_url(self, obj):
        if obj.result_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + obj.result_file.name)
            return settings.MEDIA_URL + obj.result_file.name
        return None

class TestOrderSerializer(serializers.ModelSerializer):
    test_type = serializers.PrimaryKeyRelatedField(queryset=TestType.objects.all())
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_email = serializers.EmailField(source='user.email', read_only=True)
    patient_phone = serializers.CharField(source='user.phone_number', read_only=True)
    test_name = serializers.SerializerMethodField()
    test_result = serializers.SerializerMethodField()
    class Meta:
        model = TestOrder
        fields = [
            'patient_name', 'patient_email', 'patient_phone', 'test_type',
            'order_date', 'status', 'collection_time', 'result', 'result_sent', 'latitude', 'longitude', 'test_name', 'test_result', 'address', 'total_pay'
        ]
        read_only_fields = ['order_date']  # `order_date` is auto-generated

    def create(self, validated_data):
        # Ensure the user is linked to a patient instance
        user = self.context['request'].user
        print(user)
        # patient = getattr(user, 'patient_profile', None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": "User must be authenticated to create a test order."})


        validated_data['user'] = user
        # Create the TestOrder
        # validated_data['patient'] = patient
        return TestOrder.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update the `test_type` field if provided
        test_type = validated_data.pop('test_type')
        if test_type:
            instance.test_type = test_type

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    
    
    
    def get_test_result(self, obj):
        # Retrieve the associated test result
        test_result = TestResult.objects.filter(test_order=obj).first()
        if test_result:
            return TestResultSerializer(test_result).data
        return None

    def get_test_name(self, obj):
        # Retrieve the name of the test from the related TestType model
        return obj.test_type.name


# Serializer for TestCollectionAssignment model
class TestCollectionAssignmentSerializer(serializers.ModelSerializer):
    test_order_id = serializers.IntegerField(source='test_order.id', read_only=True)

    class Meta:
        model = TestCollectionAssignment
        fields = ['id', 'collector', 'test_order', 'status', 'collection_date', 'test_order_id']

# Serializer for TestResult model



