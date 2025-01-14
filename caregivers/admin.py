from django.contrib import admin
from .models import Caregiver, CareRequest, CareSchedule, CaregiverRating, CaregiverPayment, CaregiverAvailability, PatientCaregiverInteraction

# Caregiver model
class CaregiverAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'date_of_birth', 'phone_number', 'email', 'experience_years', 'available_from', 'available_to', 'user')
    search_fields = ('full_name', 'phone_number', 'email')
    list_filter = ('gender', 'experience_years', 'available_from', 'available_to')

admin.site.register(Caregiver, CaregiverAdmin)

# CareRequest model
class CareRequestAdmin(admin.ModelAdmin):
    list_display = ('patient', 'caregiver', 'start_date', 'end_date', 'status', 'payment_amount', 'created_at')
    search_fields = ('patient__phone_number', 'caregiver__phone_number', 'status')
    list_filter = ('status', 'start_date', 'end_date')

admin.site.register(CareRequest, CareRequestAdmin)

# CareSchedule model
class CareScheduleAdmin(admin.ModelAdmin):
    list_display = ('caregiver', 'day_of_week', 'start_time', 'end_time')
    search_fields = ('caregiver__full_name', 'day_of_week')
    list_filter = ('day_of_week',)

admin.site.register(CareSchedule, CareScheduleAdmin)

# CaregiverRating model
class CaregiverRatingAdmin(admin.ModelAdmin):
    list_display = ('caregiver', 'patient', 'rating', 'created_at')
    search_fields = ('caregiver__full_name', 'patient__full_name')
    list_filter = ('rating', 'created_at')

admin.site.register(CaregiverRating, CaregiverRatingAdmin)

# CaregiverPayment model
class CaregiverPaymentAdmin(admin.ModelAdmin):
    list_display = ('caregiver', 'care_request', 'amount', 'payment_date', 'payment_status')
    search_fields = ('caregiver__full_name', 'care_request__patient__full_name')
    list_filter = ('payment_status', 'payment_date')

admin.site.register(CaregiverPayment, CaregiverPaymentAdmin)

# CaregiverAvailability model
class CaregiverAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('caregiver', 'available_date', 'available_start_time', 'available_end_time')
    search_fields = ('caregiver__full_name',)
    list_filter = ('available_date',)

admin.site.register(CaregiverAvailability, CaregiverAvailabilityAdmin)

# PatientCaregiverInteraction model
class PatientCaregiverInteractionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'caregiver', 'interaction_date', 'interaction_details')
    search_fields = ('patient__full_name', 'caregiver__full_name')
    list_filter = ('interaction_date',)

admin.site.register(PatientCaregiverInteraction, PatientCaregiverInteractionAdmin)
