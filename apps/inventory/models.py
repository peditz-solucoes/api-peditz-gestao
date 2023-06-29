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
    minimum_stock = models.DecimalField(_('Minimum stock'), default=0, max_digits=10, decimal_places=3)

    relatedProducts = models.ManyToManyField(Product, verbose_name=_('Related products'), related_name='related_items', blank=True)

    stock = models.DecimalField(_('stock'), default=0, max_digits=10, decimal_places=3)

    def __str__(self):
        return self.title
    
class ItemTransaction(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Item transaction')
        verbose_name_plural = _('Item transactions')

    item = models.ForeignKey(Item, verbose_name=_('Item'), on_delete=models.CASCADE, related_name='transactions')
    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2)

    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.SET('deleted'), related_name='item_transactions')
    user_name = models.CharField(_('User name'), max_length=255)

    file = models.FileField(_('File'), upload_to=upload_path, blank=True, null=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.user:
            self.user_name = self.user.get_full_name()
        self.item.stock += self.quantity
        self.item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.item.title}'
