from django.contrib import admin
from .models import Patient, BPLevel, SugarLevel, HeartRate, CholesterolLevel

# Register your models here.
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'date_of_birth', 'gender', 'blood_type', 'insurance_provider')
    search_fields = ('name', 'blood_type', 'insurance_provider')
    list_filter = ('gender', 'blood_type')
    fieldsets = (
        ('Personal Info', {'fields': ('user', 'name', 'date_of_birth', 'age', 'gender', 'address')}),
        ('Medical Info', {'fields': ('medical_history', 'blood_type', 'insurance_provider', 'insurance_policy_number')}),
        ('Emergency Contact', {'fields': ('emergency_contact',)}),
    )
    
admin.site.register(Patient, PatientAdmin)



@admin.register(BPLevel, SugarLevel, HeartRate, CholesterolLevel)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date')
    list_filter = ('date',)
    search_fields = ('patient__name',)
