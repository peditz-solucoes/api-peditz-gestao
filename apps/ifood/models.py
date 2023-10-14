from django.db import models
from apps.restaurants.models import Restaurant
# Create your models here.

class IfoodUserCredentials(models.Model):
    class Meta:
        verbose_name = 'Ifood user credentials'
        verbose_name_plural = 'Ifood user credentials'

    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=255)
    expires_in = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='ifood_user_credentials')
    
    def __str__(self):
        return self.restaurant.title