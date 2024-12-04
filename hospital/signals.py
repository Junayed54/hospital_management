from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Appointment

CustomUser = get_user_model()

@receiver(post_save, sender=CustomUser)
def link_appointments(sender, instance, created, **kwargs):
    if not created:  # Only run for existing users
        Appointment.objects.filter(
            user__isnull=True,
            phone_number=instance.phone_number  # Match by phone number
        ).update(user=instance)
