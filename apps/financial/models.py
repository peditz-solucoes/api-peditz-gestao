from django.db import models
from django.dispatch import receiver
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from apps.user.models import User
from apps.restaurants.models import Restaurant, Table, Product, ProductComplementItem
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum, Max
from django.db import transaction
from django.db.models.signals import post_save
# Create your models here.
# Forma do recebimento. Alguns valores possíveis:01: Dinheiro.02: Cheque.03: Cartão de Crédito.04: Cartão de Débito.05: Crédito Loja.10: Vale Alimentação.11: Vale Refeição.12: Vale Presente.13: Vale Combustível.99: Outros
PAYMENT_METHODS = (
    ('01', 'Dinheiro'),
    ('01', 'PIX'),
    ('03', 'Cartão de Crédito'),
    ('04', 'Cartão de Débito'),
    ('10', 'Vale Alimentação'),
    ('11', 'Vale Refeição'),
    ('99', 'Outros'),
)

class Cashier(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Cashier')
        verbose_name_plural = _('Cashiers')
        ordering = ['-created']

    open = models.BooleanField(_('Open'), default=True)
    identifier = models.CharField(_('Identifier'), max_length=255, blank=True, null=True)
    initial_value = models.DecimalField(_('Initial value'), max_digits=10, decimal_places=2)
    
    opened_by_name = models.CharField(_('Opened by'), max_length=255, blank=True, null=True)
    opened_by = models.ForeignKey(User, verbose_name=_('Opened by'), on_delete=models.PROTECT, related_name='cashier_opened_by')
    closed_by_name = models.CharField(_('Closed by'), max_length=255, blank=True, null=True)
    closed_by = models.ForeignKey(User, verbose_name=_('Closed by'), on_delete=models.PROTECT, related_name='cashier_closed_by', blank=True, null=True)
    
    closed_at = models.DateTimeField(_('Closed at'), blank=True, null=True)
    
    restaurant = models.ForeignKey(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='cashiers')


    def clean(self) -> None:
        if self.pk and self.open == False and self.closed_by is None:
            raise ValidationError(_('A cashier can only be closed if there is an associated user who closed it.'))
        if self.pk and self.open == False and self.closed_at is None:
            raise ValidationError(_('A cashier can only be closed if there is a closed_at date.'))
        if self.pk and self.open == True and self.opened_by is None:
            raise ValidationError(_('A cashier can only be open if there is an associated user who opened it.'))
        open_cashiers = Cashier.objects.filter(restaurant=self.restaurant, open=True)
        if self.open and open_cashiers.exists() and open_cashiers.first().pk != self.pk:
            raise ValidationError(_('There can only be one open cashier per restaurant.'))
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.opened_by:
            self.opened_by_name = self.opened_by.get_full_name()
        if self.closed_by:
            self.closed_by_name = self.closed_by.get_full_name()
        if not self.open:
            self.closed_at = self.modified
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.identifier} - {self.restaurant.title} - {self.created}'
    

class Bill(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Bill')
        verbose_name_plural = _('Bills')
        ordering = ['-created']
        unique_together = ['number', 'cashier']

    number =  models.IntegerField(_('Number'))
    cashier = models.ForeignKey(Cashier, verbose_name=_('Cashier'), on_delete=models.CASCADE, related_name='bills')
    table = models.ForeignKey(Table, verbose_name=_('Table'), on_delete=models.SET_NULL, related_name='bills', blank=True, null=True)
    open = models.BooleanField(_('Open'), default=True)

    client_name = models.CharField(_('Client name'), max_length=255, blank=True, null=True)
    client_phone = PhoneNumberField(verbose_name=_('Phone'), blank=True, region='BR')


    opened_by_name = models.CharField(_('Opened by'), max_length=255, blank=True, null=True)
    opened_by = models.ForeignKey(User, verbose_name=_('Opened by'), on_delete=models.PROTECT, related_name='bill_opened_by')

    tip = models.DecimalField(_('Tip'), max_digits=10, decimal_places=2, default=0)


    def save(self, *args, **kwargs):
        if self.opened_by:
            self.opened_by_name = self.opened_by.get_full_name()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'COMANDA {self.number} - CAIXA {self.cashier.identifier}'
    
class Order(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created']

    bill = models.ForeignKey(Bill, verbose_name=_('Bill'), on_delete=models.CASCADE, related_name='orders')

    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    product_title = models.CharField(_('Product title'), max_length=255)

    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2, blank=True, null=True, default=0)

    note = models.TextField(_('Note'), blank=True, null=True)
    order_number = models.PositiveIntegerField(_('Order Number'), blank=True, null=True)

    def __str__(self):
        return f'{self.product.title}'
    
class OrderComplement(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Order Complement')
        verbose_name_plural = _('Order Complements')
        ordering = ['-created']
        unique_together = ['order', 'complement_item']

    order = models.ForeignKey(Order, verbose_name=_('Order'), on_delete=models.CASCADE, related_name='complements')
    complement_item = models.ForeignKey(ProductComplementItem, verbose_name=_('Complement Item'), on_delete=models.SET_NULL, related_name='order_complements', null=True, blank=True)
    complement_item_title = models.CharField(_('Complement Item title'), max_length=255, default='', blank=True)

    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, blank=True, null=True, default=0)

    def save(self, *args, **kwargs):
        if self.complement_item:
            self.complement_item_title = self.complement_item.title
            self.unit_price = self.complement_item.price
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.order.product.title} | {self.complement_item.complementCategory.title} | {self.complement_item_title}'

class PaymentMethod(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        unique_together = ['restaurant', 'title']
    method = models.CharField(_('Method'), max_length=255, choices=PAYMENT_METHODS, default=PAYMENT_METHODS[0][0])
    title = models.CharField(_('Title'), max_length=255, blank=True, null=True)
    active = models.BooleanField(_('Active'), default=True)
    order = models.IntegerField(_('Order'), default=0)
    tax_percentage = models.DecimalField(_('Tax percentage'), max_digits=3, decimal_places=2, default=0)
    tax = models.DecimalField(_('Tax'), max_digits=10, decimal_places=2, default=0)
    payout_schedule = models.IntegerField(_('Payout schedule'), help_text=_("Number of days to receive the payment"), default=0)
    restaurant = models.ForeignKey(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='payment_methods')

    def save(self, *args, **kwargs):
        if self.method:
            self.title = dict(PAYMENT_METHODS)[self.method]
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}'

class Payment(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    bill = models.ForeignKey(Bill, verbose_name=_('Bill'), on_delete=models.CASCADE, related_name='payments')

    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_('Payment Method'), on_delete=models.PROTECT, related_name='payments')
    payment_method_title = models.CharField(_('Payment Method title'), max_length=255)
    
    value = models.DecimalField(_('Value'), max_digits=10, decimal_places=2)
    
    note = models.TextField(_('Note'), blank=True, null=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.payment_method:
            self.payment_method_title = self.payment_method.title

        if self.bill:
            all_payments = Payment.objects.filter(bill=self.bill)
            total_payments = all_payments.aggregate(Sum('value'))['value__sum'] or 0
            total_bill = Order.objects.filter(bill=self.bill).aggregate(Sum('total'))['total__sum'] or 0
            if total_payments + self.value > total_bill:
                self.bill.tip = total_payments + self.value - total_bill
                self.bill.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.payment_method.title} - {self.value}'
    

@receiver(post_save, sender=Order)
def update_bill_total(sender, instance, created, **kwargs):
    if created:
        if instance.product:
            instance.product_title = instance.product.title
            instance.unit_price = instance.product.price
        max_order_number = Order.objects.filter(bill__cashier__restaurant=instance.bill.cashier.restaurant).aggregate(Max('order_number'))['order_number__max']
        if max_order_number is None:
            instance.order_number = 1
        else:
            instance.order_number = max_order_number + 1
            


    