from django.db import models
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from apps.user.models import User
from apps.restaurants.models import Employer, Restaurant, Table, Product, ProductComplementCategory, ProductComplementItem
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum, Max
from django.db import transaction
from localflavor.br.models import BRCPFField

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
ORDER_GOUP_TYPES = (
    ('DELIVERY', 'DELIVERY'),
    ('TAKEOUT', 'TAKEOUT'),
    ('BILL', 'BILL'),
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
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.identifier} - {self.restaurant.title} - {self.created}'
    
class PaymentGroup(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Payment Group')
        verbose_name_plural = _('Payments Groups')
        ordering = ['-created']

    type = models.CharField(_('Type'), max_length=255, choices=ORDER_GOUP_TYPES)
    tip = models.DecimalField(_('Tip'), max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(_('Discount'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, default=0)
    cashier  = models.ForeignKey(Cashier, verbose_name=_('Cashier'), on_delete=models.CASCADE, related_name='payment_groups')

    def update_total(self):
        self.total = self.payments.aggregate(total=Sum('value'))['total']
        related_bills = self.bills.all()
        bills_order_group_total = OrderGroup.objects.filter(bill__in=related_bills).aggregate(total=Sum('total'))['total'] or 0
        if bills_order_group_total and bills_order_group_total < self.total:
            self.tip = self.total - bills_order_group_total
        else:
            self.tip = 0
        self.save()

    def __str__(self):
        return f'{self.type} - {self.created}'
    

class Bill(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Bill')
        verbose_name_plural = _('Bills')
        ordering = ['-created']

    number =  models.PositiveBigIntegerField(_('Number'))
    cashier = models.ForeignKey(Cashier, verbose_name=_('Cashier'), on_delete=models.CASCADE, related_name='bills')
    table = models.ForeignKey(Table, verbose_name=_('Table'), on_delete=models.SET_NULL, related_name='bills', blank=True, null=True)
    open = models.BooleanField(_('Open'), default=True)

    client_name = models.CharField(_('Client name'), max_length=255, blank=True, null=True)
    client_phone = PhoneNumberField(verbose_name=_('Phone'), blank=True, region='BR')


    opened_by_name = models.CharField(_('Opened by'), max_length=255, blank=True, null=True)
    opened_by = models.ForeignKey(User, verbose_name=_('Opened by'), on_delete=models.SET_NULL, null=True,  blank=True,related_name='bill_opened_by')

    tip = models.DecimalField(_('Tip'), max_digits=10, decimal_places=2, default=0)
    payment_group = models.ForeignKey(PaymentGroup, verbose_name=_('Payment Group'), on_delete=models.SET_NULL, related_name='bills', blank=True, null=True)
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.opened_by:
            self.opened_by_name = self.opened_by.get_full_name()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'COMANDA {self.number} - CAIXA {self.cashier.identifier}'



TAKEOUT_STATUS = (
    ('PAID', 'PAID'),
    ('CANCELED', 'CANCELED'),
)

class OrderStatus(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Order Status')
        verbose_name_plural = _('Order Status')
        ordering = ['created']

    status = models.CharField(_('Status'), max_length=255)
    color = models.CharField(_('Color'), max_length=255, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='order_status')
    active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Order'), default=0)

    def __str__(self):
        return f'{self.status} - {self.restaurant}'

class OrderGroup(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Order Group')
        verbose_name_plural = _('Order Groups')
        ordering = ['-created']
        unique_together = ['order_number', 'restaurant']
    type = models.CharField(_('Type'), max_length=255, choices=ORDER_GOUP_TYPES, default='BILL')
    bill = models.ForeignKey(Bill, verbose_name=_('Bill'), null=True, blank=True,on_delete=models.CASCADE, related_name='order_groups')
    order_number = models.PositiveIntegerField(_('Order Number'), blank=True, null=True)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, default=0)
    status = models.ForeignKey(OrderStatus, verbose_name=_('Status'), on_delete=models.PROTECT, related_name='order_groups')
    collaborator = models.ForeignKey(Employer, verbose_name=_('Colaborator'), on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    collaborator_name = models.CharField(_('Colaborator name'), max_length=255, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='order_groups')
    notes = models.TextField(_('Notes'), blank=True, null=True)
    cashier = models.ForeignKey(Cashier, verbose_name=_('Cashier'), on_delete=models.SET_NULL, related_name='order_groups', blank=True, null=True)
    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.type == 'BILL' and self.bill is None:
            raise ValidationError({
                'detail': _('Um grupo de pedidos do tipo COMANDA deve ter uma comanda.')
            }, code='invalid')
        if self.bill is not None and self.type != 'BILL':
            raise ValidationError({
                'detail': _('Um grupo de pedidos do tipo COMANDA não pode ser atribuido a esse tipo.')
            }, code='invalid')
        if self.collaborator is None and self.type == 'BILL':
            raise ValidationError({
                'detail': _('Um grupo de pedidos do tipo COMANDA deve ter um colaborador.')
            }, code='invalid')
        if self.order_number is None:
            if self.collaborator:
                self.collaborator_name = self.collaborator.user.get_full_name()
            max_order_number = OrderGroup.objects.filter(restaurant=self.restaurant).aggregate(Max('order_number'))['order_number__max']
            if max_order_number is None:
                self.order_number = 1
            else:
                self.order_number = max_order_number + 1
        if self.id is None:
            self.total = 0
        elif self.total is None:
            self.total = 0
        elif self.orders.exists() and self.id is not None:
            self.total = self.orders.aggregate(Sum('total'))['total__sum']
        super().save(*args, **kwargs)


    def __str__(self):
        return f'Pedido {self.order_number}'
    
    
class TakeoutOrder(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Takeout')
        verbose_name_plural = _('Takeouts')
        ordering = ['-created']

    client_name = models.CharField(_('Client name'), max_length=255, blank=True, null=True)
    client_phone = PhoneNumberField(verbose_name=_('Phone'), blank=True, region='BR', null=True)
    cpf = BRCPFField(verbose_name=_('CPF'), blank=True, null=True)
    status = models.CharField(_('Status'), max_length=255, choices=TAKEOUT_STATUS, default='PAID')
    order_group = models.OneToOneField(OrderGroup, verbose_name=_('Order Group'), on_delete=models.CASCADE, related_name='takeout_order')
    cashier = models.ForeignKey(Cashier, verbose_name=_('Cashier'), on_delete=models.CASCADE, related_name='takeout_orders')
    payment_group = models.ForeignKey(PaymentGroup, verbose_name=_('Payment Group'), on_delete=models.SET_NULL, related_name='takeout_orders', blank=True, null=True)
    sequence = models.PositiveIntegerField(_('Sequence'), default=0)

    def __str__(self):
        return f'{self.order_group.order_number}'
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.order_group.bill is not None:
            raise ValidationError({
                'detail': _('Um pedido para retirada não pode ter uma comanda.')
            }, code='invalid')
        if self.order_group.type == 'DELIVERY':
            raise ValidationError({
                'detail': _('Um pedido para retirada não pode ser do tipo delivery.')
            }, code='invalid')
        if self.pk is None:
            self.order_group.type = 'TAKEOUT'
            self.order_group.save()
        super().save(*args, **kwargs)
    
class Order(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created']

    order_group = models.ForeignKey(OrderGroup, verbose_name=_('Order Group'), on_delete=models.CASCADE, related_name='orders') 

    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    product_title = models.CharField(_('Product title'), max_length=255)

    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2, blank=True, null=True, default=0)

    note = models.TextField(_('Note'), blank=True, null=True)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    
    active = models.BooleanField(_('Active'), default=True)

    def __str__(self):
        return f'pedido {self.order_group.order_number} - {self.product_title}'
        
    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.product:
            self.product_title = self.product.title
        all_groups = self.complements.all()
        if all_groups.exists():
            self.total = float((sum(group.total for group in all_groups) + self.unit_price)) * float(self.quantity)
        elif self.unit_price:
            self.total = float(self.unit_price) * float(self.quantity)
        super().save(*args, **kwargs)
        self.order_group.save()

    @transaction.atomic
    def delete(self, using = None, keep_parents = False):
        super().delete(using, keep_parents)
        self.order_group.save()
        if self.order_group.type == 'BILL' and self.order_group.orders.count() == 0:
            self.order_group.delete()
    
class OrderComplement(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Order Complement')
        verbose_name_plural = _('Order Complement')
        ordering = ['-created']
        unique_together = ['order', 'complement_group']

    order = models.ForeignKey(Order, verbose_name=_('Order'), on_delete=models.CASCADE, related_name='complements')
    complement_group = models.ForeignKey(ProductComplementCategory, verbose_name=_('Complement Item'), on_delete=models.SET_NULL, related_name='order_complements', null=True, blank=True)
    complement_group_title = models.CharField(_('Complement Item title'), max_length=255, default='', blank=True)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.complement_group:
            self.complement_group_title = self.complement_group.title
        items = self.items.all()
        if not items:
            return
        if self.complement_group.business_rules == 'maior':
            self.total = max(item.total for item in items)
        elif self.complement_group.business_rules == 'media':
            self.total = sum(item.total for item in items) / len(items)
        elif self.complement_group.business_rules == 'soma':
            self.total = sum(item.total for item in items)
        self.order.save()
        super().save(*args, **kwargs)
       
        

    def __str__(self):
        return f'{self.complement_group_title} complemento do pedido {self.order.id}'
    
class OrderComplementItem(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Order Complement Item')
        verbose_name_plural = _('Order Complement Items')
        ordering = ['-created']
        unique_together = ['order_complement', 'complement']

    order_complement = models.ForeignKey(OrderComplement, verbose_name=_('Order Complement'), on_delete=models.CASCADE, related_name='items')
    complement = models.ForeignKey(ProductComplementItem, verbose_name=_('Complement'), on_delete=models.SET_NULL, related_name='order_complements', null=True, blank=True)
    complement_title = models.CharField(_('Complement title'), max_length=255, default='', blank=True)

    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.complement:
            self.complement_title = self.complement.title
            self.total = self.unit_price * self.quantity

        if self.order_complement.complement_group:
            if int(sum(item.quantity for item in self.order_complement.items.all())) > self.order_complement.complement_group.max_value:
                raise ValidationError({
                    'detail': f'Você pode adicionar no máximo {self.order_complement.complement_group.max_value} items'}, code='400')
        super().save(*args, **kwargs)
        self.order_complement.save()

    def __str__(self):
        return f'{self.complement_title} complemento do pedido {self.order_complement.order.id}'

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
    acept_on_delivery = models.BooleanField(_('Acept on delivery'), default=True)
    needs_change = models.BooleanField(_('Needs change'), default=False)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} - {self.restaurant.title}'


class Payment(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created']

    TRANSACTION_TYPES = (
        ('PAYMENT', 'ENTRADA'),
        ('REFUND', 'REENBOLSO'),
        ('CHARGEBACK', 'TROCO'),
        ('WITHDRAW', 'SANAGRIA'),
    )

    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_('Payment Method'), on_delete=models.PROTECT, related_name='payments')
    payment_method_title = models.CharField(_('Payment Method title'), max_length=255)
    value = models.DecimalField(_('Value'), max_digits=10, decimal_places=2)
    note = models.TextField(_('Note'), blank=True, null=True)
    type = models.CharField(_('Type'), max_length=255, choices=TRANSACTION_TYPES, default='PAYMENT')
    payment_group = models.ForeignKey(PaymentGroup, verbose_name=_('Payment Group'), on_delete=models.CASCADE, related_name='payments')

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.payment_method:
            self.payment_method_title = self.payment_method.title
        super().save(*args, **kwargs)
        if self.payment_group:
            self.payment_group.update_total()


    def __str__(self):
        return f'{self.payment_method.title} - {self.value}'
    
            


class CancelationReason(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Cancelation Reason')
        verbose_name_plural = _('Cancelation Reasons')
        ordering = ['-created']

    CANCEL_TYPES = (
        ('ORDER', 'Pedido'),
        ('BILL', 'Comanda'),
    )

    title = models.CharField(_('Title'), max_length=255)
    type = models.CharField(_('Type'), max_length=255, choices=CANCEL_TYPES, default='ORDER')
    restaurant = models.ForeignKey(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='cancelation_reasons')
    reason = models.TextField(_('Reason'), blank=True, null=True)
    operator = models.ForeignKey(User, verbose_name=_('Operator'), on_delete=models.SET_NULL, related_name='cancelation_reasons', blank=True, null=True)
    operator_name = models.CharField(_('Operator name'), max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.SET_NULL, related_name='cancelation_reasons', blank=True, null=True)
    product_title = models.CharField(_('Product title'), max_length=255, blank=True, null=True)
    cashier = models.ForeignKey(Cashier, verbose_name=_('Cashier'), on_delete=models.SET_NULL, related_name='cancelation_reasons', blank=True, null=True)
    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=3, default=1)
    bill = models.ForeignKey(Bill, verbose_name=_('Bill'), on_delete=models.SET_NULL, related_name='cancelation_reasons', blank=True, null=True)
    bill_number = models.PositiveIntegerField(_('Bill number'), blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.product:
            self.product_title = self.product.title
        if self.operator:
            self.operator_name = self.operator.get_full_name()
        if self.bill:
            self.bill_number = self.bill.number
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} - {self.restaurant.title}'

    