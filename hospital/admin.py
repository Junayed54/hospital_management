from django.contrib import admin
from .models import Doctor, DoctorAvailability, WaitingList, Appointment, Treatment, Prescription, Notification, Medication, Test

# Custom admin configuration for Doctor
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'user', 'license_number', 'experience_years')
    search_fields = ('full_name', 'license_number')
    list_filter = ('experience_years',)

    fieldsets = (
        ('Personal Info', {'fields': ('user', 'full_name', 'license_number', 'bio')}),
        ('Professional Info', {'fields': ('experience_years', 'education')}),
        ('Contact Info', {'fields': ('contact_email', 'contact_phone')}),
    )

    # def get_specialties(self, obj):
    #     return ", ".join([s.name for s in obj.specialties.all()])
    # get_specialties.short_description = 'Specialties'  # Admin column name

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'doctor', 
        'date', 
        'start_time', 
        'session_duration', 
        'max_patients', 
        'booked_patients'
    )
    list_filter = ('doctor', 'date')
    search_fields = ('doctor__name', 'date')
    ordering = ('date', 'start_time')
    # readonly_fields = ('booked_patients',)

    # def has_add_permission(self, request):
    #     """
    #     Restrict doctors from adding their availability more than once for the same date and time.
    #     """
    #     return super().has_add_permission(request)

    # def has_change_permission(self, request, obj=None):
    #     """
    #     Allow changes to availability only before any appointments are booked.
    #     """
    #     if obj and obj.booked_patients > 0:
    #         return False
    #     return super().has_change_permission(request, obj=obj)

@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):  # Fixed class name
    list_display = ('availability', 'patient', 'requested_at')  # Fields to display in the list view
    list_filter = ('availability__doctor', 'requested_at')  # Filters for the admin panel
    search_fields = ('patient__name', 'availability__doctor__name')  # Searchable fields
    ordering = ('requested_at',)  # Order by requested_at field
# Custom admin configuration for Appointment
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'doctor', 'phone_number', 'email', 'appointment_date', 'patient', 'status')
    search_fields = ('patient_name', 'doctor__user__username', 'phone_number', 'email')
    list_filter = ('doctor', 'appointment_date')
    ordering = ('-appointment_date',)
    readonly_fields = ('appointment_date',)

    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_name', 'status', 'phone_number', 'email', 'address', 'patient', 'video_link')
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
        'id', 'patient', 'doctor', 'diagnosis', 'treatment_date', 'follow_up_date', 
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
    
    