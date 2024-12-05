from django.contrib import admin
from .models import Doctor, Patient, Appointment, Treatment, Prescription, Notification, Medication, Test

# Custom admin configuration for Doctor
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'specialty', 'license_number', 'experience_years', 'consultation_fee')
    search_fields = ('full_name', 'specialty', 'license_number')
    list_filter = ('specialty', 'experience_years')
    fieldsets = (
        ('Personal Info', {'fields': ('user','full_name', 'specialty', 'license_number', 'bio')}),
        ('Professional Info', {'fields': ('experience_years', 'education', 'consultation_fee')}),
        ('Contact Info', {'fields': ('contact_email', 'contact_phone')}),
    )

# Custom admin configuration for Patient
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'date_of_birth', 'gender', 'blood_type', 'insurance_provider')
    search_fields = ('name', 'blood_type', 'insurance_provider')
    list_filter = ('gender', 'blood_type')
    fieldsets = (
        ('Personal Info', {'fields': ('user', 'name', 'date_of_birth', 'gender', 'address')}),
        ('Medical Info', {'fields': ('medical_history', 'blood_type', 'insurance_provider', 'insurance_policy_number')}),
        ('Emergency Contact', {'fields': ('emergency_contact',)}),
    )

# Custom admin configuration for Appointment
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor', 'phone_number', 'email', 'appointment_date', 'user')
    search_fields = ('patient_name', 'doctor__user__username', 'phone_number', 'email')
    list_filter = ('doctor', 'appointment_date')
    ordering = ('-appointment_date',)
    readonly_fields = ('appointment_date',)

    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_name', 'phone_number', 'email', 'address', 'user', 'video_link')
        }),
        ('Appointment Details', {
            'fields': ('doctor', 'appointment_date')
        }),
    )

    # Optional: Adding custom actions or methods (e.g., exporting data)
    actions = ['export_appointments']

    def export_appointments(self, request, queryset):
        # Example function to export data (can be expanded as needed)
        pass
    export_appointments.short_description = 'Export selected appointments'
    
    
# Custom admin configuration for Treatment
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'treatment_date', 'cost')
    search_fields = ('patient__user__username', 'doctor__user__username', 'diagnosis')
    list_filter = ('treatment_date',)
    fieldsets = (
        ('Treatment Details', {'fields': ('patient', 'doctor', 'diagnosis', 'prescription', 'treatment_notes')}),
        ('Follow-up', {'fields': ('treatment_date', 'follow_up_date', 'cost')}),
    )

# Register models with their custom admin configurations
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
# admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Treatment, TreatmentAdmin)


class TestInline(admin.TabularInline):
    model = Test
    extra = 1 

class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 1  # Number of empty forms to display
    fields = ('name', 'dosage', 'frequency', 'duration', 'notes')
    # readonly_fields = ('name',)  # Optional: make specific fields read-only
    can_delete = True 

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    inlines = [MedicationInline, TestInline]

    list_display = (
        'patient', 'doctor', 'diagnosis', 'treatment_date', 'follow_up_date', 
        'published', 'cost'
    )
    list_filter = ('published', 'treatment_date', 'doctor')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name', 'doctor__user__last_name', 'diagnosis')
    ordering = ('-treatment_date',)

    # Custom action to publish prescriptions from admin
    actions = ['publish_prescriptions']

    def publish_prescriptions(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f"{updated} prescription(s) published successfully.")

    publish_prescriptions.short_description = "Publish selected prescriptions"

    # Restrict certain fields to be read-only for patients (if applicable)
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if not request.user.is_superuser and request.user.role != 'doctor':
            readonly_fields = ['published', 'diagnosis', 'treatment_notes', 'cost']
        return readonly_fields





@admin.register(Notification)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'read', 'scheduled_time')
    list_filter = ('read', 'created_at', 'scheduled_time')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'message', 'scheduled_time', 'read')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )