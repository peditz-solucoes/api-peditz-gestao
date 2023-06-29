from django.db import models
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from apps.user.models import User
from apps.restaurants.models import Restaurant, Table, Product
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum, Max
from django.db import transaction

# Create your models here.

class Cashier(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Cashier')
        verbose_name_plural = _('Cashiers')
        ordering = ['-created']

    open = models.BooleanField(_('Open'), default=True)
    identifier = models.CharField(_('Identifier'), max_length=255, blank=True, null=True)
    initial_value = models.DecimalField(_('Initial value'), max_digits=10, decimal_places=2)
    opened_by_name = models.CharField(_('Opened by'), max_length=255, blank=True, null=True)
    opened_by = models.ForeignKey(User, verbose_name=_('Opened by'), on_delete=models.SET('Usuário deletado'), related_name='cashier_opened_by', blank=True, null=True)
    closed_by_name = models.CharField(_('Closed by'), max_length=255, blank=True, null=True)
    closed_by = models.ForeignKey(User, verbose_name=_('Closed by'), on_delete=models.SET('Usuário deletado'), related_name='cashier_closed_by', blank=True, null=True)
    closed_at = models.DateTimeField(_('Closed at'), blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='cashiers')

    def clean(self):

        if self.open and self.opened_by is None:
            raise ValidationError(_('A cashier can only be open if there is an associated user who opened it.'))

        if not self.open and self.closed_by is None:
            raise ValidationError(_('A cashier can only be closed if there is an associated user who closed it.'))

        open_cashiers = Cashier.objects.filter(restaurant=self.restaurant, open=True)
        if self.open and open_cashiers.exists():
            raise ValidationError(_('There can only be one open cashier per restaurant.'))

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


    opened_by_name = models.CharField(_('Opened by'), max_length=255)
    opened_by = models.ForeignKey(User, verbose_name=_('Opened by'), on_delete=models.SET('Usuário deletado'), related_name='bill_opened_by')

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

    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.SET('produto excluido'), related_name='orders')
    product_title = models.CharField(_('Product title'), max_length=255)

    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2)

    note = models.TextField(_('Note'), blank=True, null=True)
    order_number = models.PositiveIntegerField(_('Order Number'), blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.product:
            self.product_title = self.product.title
            self.unit_price = self.product.price
        self.total = self.quantity * self.unit_price

        if not self.pk:
            max_order_number = Order.objects.filter(bill__cashier__restaurant=self.bill.cashier.restaurant).aggregate(Max('order_number'))['order_number__max']
            if max_order_number is None:
                self.order_number = 1
            else:
                self.order_number = max_order_number + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.title}'
    

class PaymentMethod(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')

    title = models.CharField(_('Title'), max_length=255)
    active = models.BooleanField(_('Active'), default=True)
    order = models.IntegerField(_('Order'), default=0)
    tax_percentage = models.DecimalField(_('Tax percentage'), max_digits=3, decimal_places=2, default=0)
    tax = models.DecimalField(_('Tax'), max_digits=10, decimal_places=2, default=0)
    payout_schedule = models.IntegerField(_('Payout schedule'), help_text=_("Number of days to receive the payment"), default=0)

    def __str__(self):
        return f'{self.title}'

class Payment(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    bill = models.ForeignKey(Bill, verbose_name=_('Bill'), on_delete=models.CASCADE, related_name='payments')

    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_('Payment Method'), on_delete=models.SET('Método de pagamento excluído'), related_name='payments')
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
            if total_payments + self.value > self.bill.total:
                self.bill.tip = total_payments - self.bill.total
                self.bill.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.payment_method.title} - {self.value}'
    

    


