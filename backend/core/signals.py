from geopy.geocoders import Nominatim
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Task


@receiver(pre_save, sender=Task)
def geocode_address(sender, instance, **kwargs):
    if instance.address and (not instance.latitude or not instance.longitude):
        geolocator = Nominatim(user_agent="taskoba")
        location = geolocator.geocode(instance.address)
        if location:
            instance.latitude = location.latitude
            instance.longitude = location.longitude
