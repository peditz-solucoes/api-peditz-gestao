from django.db import models
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from apps.user.models import User
from localflavor.br.models import BRCPFField

# Create your models here.

FIELDS_TYPES = (
    ('checkbox', _('Checkbox')),
    ('text', _('Text')),
    ('number', 'Incremento | número'),
)
class Restaurant(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Restaurant')
        verbose_name_plural = _('Restaurants')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    phone = PhoneNumberField(verbose_name=_(
        'Phone'), blank=True, unique=True, region='BR')
    email = models.EmailField(verbose_name=_('Email'), blank=True, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return self.title
    
class Employer(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Employer')
        verbose_name_plural = _('Employers')
        unique_together = ('cpf', 'restaurant')
    
    cpf = BRCPFField(verbose_name=_('CPF'))
    address = models.CharField(max_length=255)
    phone = PhoneNumberField(verbose_name=_(
        'Phone'), blank=True, unique=True, region='BR')
    office = models.CharField(max_length=255)
    sallary = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='employers')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer')

    def __str__(self):
        return self.user.first_name

class ProductCategory(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
    
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='product_categories')

    def __str__(self):
        return self.title

class Product(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
    
    title = models.CharField(max_length=255, verbose_name=_('Title'), blank=False, null=False)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    listed = models.BooleanField(default=True)
    product_category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.title

class ProductComplement(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Product Complement')
        verbose_name_plural = _('Product Complements')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.IntegerField(default=0)
    type = models.CharField(_('field type'), choices=FIELDS_TYPES, max_length=10, blank=False)
    active = models.BooleanField(default=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='complements')

    def __str__(self):
        return self.title