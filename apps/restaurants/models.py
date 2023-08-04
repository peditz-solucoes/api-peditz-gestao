from django.db import models
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from apps.user.models import User
from localflavor.br.models import BRCPFField, BRPostalCodeField, BRStateField
def upload_path(instance, filname):
    return '/'.join(['restaurants', str(instance.slug), filname])

def upload_path_catalogs(instance, filname):
    return '/'.join(['catalogs', str(instance.restaurant.slug), str(instance.slug), filname])

PRODUCT_TYPES = (
    ('KG', 'KG'),
    ('L', 'L'),
    ('UN', 'UN'),
)
ICMS_ORIGEM = (
    ('0', '0 - Nacional'),
    ('1', '1 - Estrangeira - Importação direta'),
    ('2', '2 - Estrangeira - Adquirida no mercado interno'),
    ('3', '3 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 40% e inferior ou igual a 70%'),
    ('4', '4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de que tratam as legislações citadas nos Ajustes'),
    ('5', '5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%'),
    ('6', '6 - Estrangeira - Importação direta, sem similar nacional, constante em lista da CAMEX e gás natural'),
    ('7', '7 - Estrangeira - Adquirida no mercado interno, sem similar nacional, constante lista CAMEX e gás natural'),
)
ICMS_SITUACAO_TRIBUTARIA = (
    ('102', '102 – Tributada pelo Simples Nacional sem permissão de crédito'),
    ('300', '300 - Imune'),
    ('500', '500 - CMS cobrado anteriormente por substituição tributária (substituído) ou por antecipação'),
    ('00', '00 – tributada integralmente'),
    ('40', '40 – Isenta'),
    ('41', '41 - Não tributada'),
    ('60', '60 - ICMS cobrado anteriormente por substituição tributária'),
)
ICMS_MODALIDADE_BASE_CALCULO = (
    ('0', '0 – margem de valor agregado (%)'),
    ('1', '1 – pauta (valor)'),
    ('2', '2 – preço tabelado máximo (valor)'),
    ('3', '3 – valor da operação'),
)


class RestauratCategory(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Restaurant Category')
        verbose_name_plural = _('Restaurant Categories')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title

class Restaurant(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Restaurant')
        verbose_name_plural = _('Restaurants')
    
    email = models.EmailField(verbose_name=_('Email'), blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)
    phone = PhoneNumberField(verbose_name=_('Phone'), blank=True, region='BR')
    zip_code = BRPostalCodeField(verbose_name=_('Zip Code'), blank=True, null=True)
    state = BRStateField(verbose_name=_('State'), blank=True, null=True)
    city = models.CharField(max_length=255, default='', blank=True, null=True)
    street = models.CharField(max_length=255, default='', blank=True, null=True)
    number = models.CharField(max_length=255, default='', blank=True, null=True)
    complement = models.CharField(max_length=255, default='', blank=True, null=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurants')
    photo = models.ImageField(upload_to=upload_path, blank=True, null=True, verbose_name=_('Picture'))
    category = models.ForeignKey(RestauratCategory, on_delete=models.SET_NULL, related_name='restaurants', null=True, blank=True)
    open = models.BooleanField(default=True)
    def __str__(self):
        return self.title

class Printer(models.Model):
    name = models.CharField(max_length=100)
    ip = models.CharField(max_length=100)
    port = models.IntegerField()
    active = models.BooleanField(default=True)
    paper_width = models.IntegerField(default=80, help_text='valor em mm')
    titleFontSize = models.IntegerField(default=18)
    bodyFontSize = models.IntegerField(default=16)
    footerFontSize = models.IntegerField(default=14)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='printers')
    def __str__(self):
        return self.name

class Employer(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        unique_together = (
            ('cpf', 'restaurant'), 
            ('phone', 'restaurant'), 
            ('code', 'restaurant')
        )
    
    cpf = BRCPFField(verbose_name=_('CPF'))
    address = models.CharField(max_length=255)
    phone = PhoneNumberField(verbose_name=_(
        'Phone'), blank=True, unique=True, region='BR')
    office = models.CharField(max_length=255)
    sallary = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='employers')
    code = models.CharField(max_length=255, unique=True)
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
        return f'{self.title} | {self.restaurant.title}'

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
    type_of_sale = models.CharField(max_length=3, choices=PRODUCT_TYPES, default='UN')
    product_category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name='products')
    printer = models.ForeignKey(
        Printer, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    
    codigo_ncm = models.CharField(max_length=255, blank=True, null=True, help_text='Código NCM do produto (8 dígitos).')
    codigo_produto = models.CharField(verbose_name=_('Product Code'), max_length=255, blank=True, null=True)
    valor_unitario_comercial = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_unitario_tributavel = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_tax_description = models.TextField(max_length=255, blank=True, null=True)
    unidade_comercial = models.CharField(max_length=255, blank=True, null=True, choices=PRODUCT_TYPES, help_text='Unidade comercial do produto. Você pode utilizar valores como “KG”, “L”, “UN”, etc. Caso não se aplique utilize “UN”.')
    unidade_tributavel = models.CharField(max_length=255, blank=True, null=True, choices=PRODUCT_TYPES, help_text='Unidade tributável do produto. Caso não se aplique utilize o mesmo valor do campo unidade_comercial.')
    icms_origem = models.CharField(blank=True, null=True, max_length=255, choices=ICMS_ORIGEM)
    icms_situacao_tributaria =  models.CharField(blank=True, null=True, max_length=255, choices=ICMS_SITUACAO_TRIBUTARIA)
    icms_aliquota = models.DecimalField(blank=True, null=True, max_digits=3, decimal_places=2, help_text='Alíquota do ICMS. Deve estar entre 0 e 100.')
    icms_base_calculo = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2, help_text='Base de cálculo do ICMS. Normalmente é igual ao valor_bruto.')
    icms_modalidade_base_calculo = models.CharField(blank=True, null=True, max_length=255, choices=ICMS_MODALIDADE_BASE_CALCULO)
    def __str__(self):
        return self.title
    
class ProductComplementCategory(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Product Complement Category')
        verbose_name_plural = _('Product Complement Categories')

    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    input_type = models.CharField(max_length=255, choices=(
        ('checkbox', 'checkbox'),
        ('radio', 'radio'),
        ('number', 'number'),
    ), default='checkbox')
    business_rules = models.TextField(blank=True, null=True, choices=(
        ('maior', 'maior'),
        ('soma', 'soma'),
        ('media', 'media'),
    ))
    max_value = models.IntegerField(default=0)
    min_value = models.IntegerField(default=0)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='complement_categories')
    
    def __str__(self):
        return self.title + " | " + self.product.title

class ProductComplementItem(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Product Complement')
        verbose_name_plural = _('Product Complements')
    
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_value = models.IntegerField(default=0)
    min_value = models.IntegerField(default=0)
    complementCategory = models.ForeignKey(
        ProductComplementCategory, on_delete=models.CASCADE, related_name='complement_items')

    def __str__(self):
        return f'{self.complementCategory.title} | {self.title}'
    
class Table(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Table')
        verbose_name_plural = _('Tables')
    
    title = models.CharField(max_length=255)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    capacity = models.IntegerField(default=0)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='tables')

    def __str__(self):
        return self.title
    
class Catalog(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Catalog')
        verbose_name_plural = _('Catalogs')
        unique_together = ('restaurant', 'slug')
    
    title = models.CharField(max_length=255)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)
    slug = models.SlugField(max_length=255)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='catalogs')
    photo = models.ImageField(upload_to=upload_path_catalogs, blank=True, null=True)
    products = models.ManyToManyField(Product, related_name='catalogs', blank=True)

    def __str__(self):
        return self.title