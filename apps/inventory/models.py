from django.db import models
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from django.utils.translation import gettext as _
from apps.restaurants.models import Restaurant, Product

from apps.user.models import User

# Create your models here.
from django.db import transaction

def upload_path(instance, filname):
    return '/'.join(['stock', str(instance.item.category.restaurant.slug), str(instance.item.title), filname])

PRODUCT_TYPES = (
    ('KG', 'KG'),
    ('L', 'Litros'),
    ('UN', 'Unidade'),
    ('CX', 'Caixa'),
    ('PCT', 'Pacote'),
)

class ItemCategory(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Item category')
        verbose_name_plural = _('Item categories')

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    order = models.PositiveIntegerField(_('Order'), default=0)
    restaurant = models.ForeignKey(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='item_categories')

    def __str__(self):
        return self.title

class Item(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    category = models.ForeignKey(ItemCategory, verbose_name=_('Category'), on_delete=models.CASCADE, related_name='items')
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    barcode = models.CharField(_('Barcode'), max_length=255, blank=True, null=True)
    product_type = models.CharField(_('Product type'), max_length=3, choices=PRODUCT_TYPES, default='UN')
    minimum_stock = models.DecimalField(_('Minimum stock'), default=0, max_digits=20, decimal_places=3)
    stock = models.DecimalField(_('stock'), default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.title
    
class ItemItem(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Item item')
        verbose_name_plural = _('Item items')
    item = models.ForeignKey(Item, verbose_name=_('Item'), on_delete=models.CASCADE, related_name='items')
    item_related = models.ForeignKey(Item, verbose_name=_('Item related'), on_delete=models.CASCADE, related_name='items_related')
    quantity = models.DecimalField(_('Quantity'), max_digits=100, decimal_places=3)

    def __str__(self):
        return f'{self.item.title} - {self.item_related.title}'
    

class ProductItem(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Product item')
        verbose_name_plural = _('Product items')

    product = models.ForeignKey(Product, verbose_name=_('Product'), on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, verbose_name=_('Item'), on_delete=models.CASCADE, related_name='products')
    quantity = models.DecimalField(_('Quantity'), max_digits=100, decimal_places=3)
    
    
class ItemTransaction(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Item transaction')
        verbose_name_plural = _('Item transactions')

    item = models.ForeignKey(Item, verbose_name=_('Item'), on_delete=models.CASCADE, related_name='transactions')
    quantity = models.DecimalField(_('Quantity'), max_digits=20, decimal_places=3)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(_('Total'), max_digits=20, decimal_places=2, default=0)

    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.SET_NULL, related_name='item_transactions', blank=True, null=True)
    user_name = models.CharField(_('User name'), max_length=255, blank=True, null=True)
    notes = models.TextField(_('Notes'), default='', blank=True, null=True)

    file = models.FileField(_('File'), upload_to=upload_path, blank=True, null=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.quantity * self.unit_price
        if not self.unit_price:
            self.unit_price = self.total / self.quantity
        if self.user:
            self.user_name = self.user.get_full_name()
        if self.quantity < 0:
            if self.item.stock < (-1 * self.quantity):
                raise Exception('Não há estoque suficiente para esta operação')
        elif self.quantity > 0:
            for item in self.item.items.all():
                if item.item_related.stock >= self.quantity * item.quantity:
                    ItemTransaction.objects.create(
                        item=item.item_related,
                        quantity=-1 * (item.quantity * self.quantity),
                        unit_price=self.unit_price,
                        total=self.total,
                        user=self.user,
                        notes='Baixa de estoque para o item ' + self.item.title,
                    )
                    item.item_related.save()
                else:
                    message = f'Não foi possível dar baixa no item {item.item_related.title} pois não há estoque suficiente'
                    raise Exception(message)
        self.item.stock += self.quantity
        self.item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.item.title}'
