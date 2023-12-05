from django.db import models

# Create your models here.
from django.db import models
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from apps.restaurants.models import Restaurant
from apps.financial.models import OrderGroup, PaymentMethod, PaymentGroup
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from localflavor.br.models import BRCPFField, BRPostalCodeField, BRStateField


class Client(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')

    name = models.CharField(_('Name'), max_length=255)
    phone = PhoneNumberField(_('Phone'), region='BR')
    cpf = BRCPFField(_('CPF'), blank=True, null=True)
    email = models.EmailField(_('Email'), blank=True, null=True)

    verified_email = models.BooleanField(_('Verified email'), default=False)
    verified_phone = models.BooleanField(_('Verified phone'), default=False)


    def __str__(self):
        return self.name
    
class ClientAdress(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Client adress')
        verbose_name_plural = _('Client adresses')

    client = models.ForeignKey(Client, verbose_name=_('Client'), on_delete=models.CASCADE, related_name='adresses')
    street = models.CharField(_('Street'), max_length=255)
    number = models.CharField(_('Number'), max_length=255)
    complement = models.CharField(_('Complement'), max_length=255, blank=True, null=True)
    neighborhood = models.CharField(_('Neighborhood'), max_length=255)
    city = models.CharField(_('City'), max_length=255)
    state = BRStateField(_('State'))
    postal_code = BRPostalCodeField(_('Postal code'))
    main = models.BooleanField(_('Main'), default=False)
    title = models.CharField(_('Title'), max_length=255, default="Casa", blank=True, null=True)

    def __str__(self):
        return self.street + ', ' + self.number + ' - ' + self.neighborhood + ' - ' + self.city + '/' + self.state
    
DELIVERY_TYPES = (
    ('IFOOD', 'Ifood'),
    ('DELIVERY_APP', 'Delivery App'),
    ('DELIVERY_SITE', 'Delivery Site'),
)


class DeliveryRestaurantConfig(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Delivery restaurant config')
        verbose_name_plural = _('Delivery restaurant configs')

    restaurant = models.OneToOneField(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='delivery_config')
    delivery_base_time = models.IntegerField(_('Delivery base time'), default=0)
    enable_delivery = models.BooleanField(_('Enable delivery'), default=False)
    price_per_km = models.DecimalField(_('Price per km'), max_digits=10, decimal_places=2, default=0.00)
    base_price = models.DecimalField(_('Base price'), max_digits=10, decimal_places=2, default=0.00)
    free_delivery_min_price = models.DecimalField(_('Free delivery min price'), max_digits=10, decimal_places=2, default=0.00)
    free_delivery_max_distance = models.DecimalField(_('Free delivery max distance'), max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.restaurant.title
    


class DeliveryOrder(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Delivery order')
        verbose_name_plural = _('Delivery orders')

    client = models.ForeignKey(Client, verbose_name=_('Client'), on_delete=models.SET_NULL,null=True, blank=True, related_name='delivery_orders')
    client_name = models.CharField(_('Client name'), max_length=255, blank=True, null=True)
    client_phone = PhoneNumberField(_('Client phone'), region='BR', blank=True, null=True)
    street = models.CharField(_('Street'), max_length=255, blank=True, null=True)
    number = models.CharField(_('Number'), max_length=255, blank=True, null=True)
    complement = models.CharField(_('Complement'), max_length=255, blank=True, null=True)
    neighborhood = models.CharField(_('Neighborhood'), max_length=255, blank=True, null=True)
    city = models.CharField(_('City'), max_length=255, blank=True, null=True)
    state = BRStateField(_('State'), blank=True, null=True)
    postal_code = BRPostalCodeField(_('Postal code'), blank=True, null=True)
    type = models.CharField(_('Type'), max_length=255, choices=DELIVERY_TYPES, default='DELIVERY_SITE')

    delivery_price = models.DecimalField(_('Delivery price'), max_digits=10, decimal_places=2, default=0.00)

    order_group = models.OneToOneField(OrderGroup, verbose_name=_('Order group'), related_name='delivery_order', on_delete=models.CASCADE)

    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_('Payment Method'), on_delete=models.SET_NULL, null=True,related_name='payments_methods')
    payment_method_title = models.CharField(_('Payment Method title'), max_length=255, blank=True, null=True)

    troco = models.DecimalField(_('Troco'), max_digits=10, decimal_places=2, default=0.00)
    payment_group = models.OneToOneField(PaymentGroup, verbose_name=_('Payment Group'), related_name='delivery_order', on_delete=models.SET_NULL, blank=True, null=True)

    canceled = models.BooleanField(_('Canceled'), default=False)

    takeaway = models.BooleanField(_('Takeaway'), default=False)
    
    def get_status_display(self):
        return self.status


    def __str__(self):
        return f'{self.client_name} - pedido {self.order_group.order_number}'


class DeliveryStatus(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Delivery status')
        verbose_name_plural = _('Delivery status')
        unique_together = ('title', 'order')

    AVAILIBLE_DELIVERY_STATUS = (
        ('WAITING', 'Aguardando confirmação do restaurante'),
        ('IN_PROGRESS', 'Em produção'),
        ('IN_ROUTE', 'Saiu para entrega'),
        ('DELIVERED', 'Entregue'),
        ('CANCELED', 'Cancelado'),
    )

    title = models.CharField(_('Title'), max_length=11, choices=AVAILIBLE_DELIVERY_STATUS, default='WAITING')
    order = models.ForeignKey(DeliveryOrder, verbose_name=_('Order'), on_delete=models.CASCADE, related_name='status')
    

    def __str__(self):
        return self.title + ' - ' + self.order.order_group.restaurant.title + ' - ' + str(self.order.order_group.order_number)