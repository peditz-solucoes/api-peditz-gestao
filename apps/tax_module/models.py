from django.db import models
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from django.utils.translation import gettext as _
from apps.restaurants.models import Restaurant
from apps.financial.models import Order, Payment
from localflavor.br.models import BRCNPJField, BRPostalCodeField, BRStateField
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
PRESENCA_COMPRADOR = (
    ('1', 'Operação presencial'),
    ('4', 'Entrega a domicílio'),
)
MODALIDADE_FRETE = (
    ('0', 'Por conta do emitente'),
    ('1', 'Por conta do destinatário'),
    ('2', 'Por conta de terceiros'),
    ('9', 'Sem frete'),
)
LOCAL_DESTINO = (
    ('1', 'Operação interna'),
    ('2', 'Operação interestadual'),
    ('3', 'Operação com exterior'),
)
# "Regime tributário. Valores possíveis: 1 - Simples Nacional; 2 - Simples Nacional - Excesso de sublimite de receita bruta; 3 - Regime Normal

REGIME_TRIBUTARIO = (
    ('1', 'Simples Nacional'),
    ('2', 'Simples Nacional - Excesso de sublimite de receita bruta'),
    ('3', 'Regime Normal'),
)
CARD_FLAGS = (
    ('01', 'Visa'),
    ('02', 'Mastercard'),
    ('03', 'American Express'),
    ('04', 'Sorocred'),
    ('99', 'Outros'),
)
# Valores possíveis:1: Pagamento integrado com o sistema de automação da empresa (Ex.: equipamento TEF, Comércio Eletrônico) – Obrigatório informar cnpj_credenciadora e numero_autorizacao.2: Pagamento não integrado com o sistema de automação da empresa (valor padrão). Informar apenas se forma_pagamento for 03 ou 04.
TIPO_INTEGRACAO = (
    ('1', 'Pagamento integrado com o sistema de automação da empresa'),
    ('2', 'Pagamento não integrado com o sistema de automação da empresa'),
)

class Company(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
    
    restaurant = models.ForeignKey(Restaurant, verbose_name=_('Restaurant'), on_delete=models.CASCADE, related_name='companies')
    natureza_operacao = models.CharField(_('Natureza da operação'), max_length=255, blank=True, null=True, default="VENDA AO CONSUMIDOR")
    presenca_comprador = models.CharField(_('Presença do comprador'), max_length=1, choices=PRESENCA_COMPRADOR, default='1')
    modalidade_frete = models.CharField(_('Modalidade do frete'), max_length=1, choices=MODALIDADE_FRETE, default='9')
    local_destino = models.CharField(_('Local de destino'), max_length=1, choices=LOCAL_DESTINO, default='1')

    cnpj= BRCNPJField(_('CNPJ'))
    nome = models.CharField(_('Name'), max_length=255)
    nome_fantasia = models.CharField(_('Fantasy name'), max_length=255)
    inscricao_estadual = models.PositiveBigIntegerField(_('Inscrição estadual'))
    inscricao_municipal = models.PositiveBigIntegerField(_('Inscrição municipal'))
    regime_tributario = models.CharField(_('Regime tributário'), max_length=1, choices=REGIME_TRIBUTARIO, default='1')
    email = models.EmailField(_('Email'))
    telefone = PhoneNumberField(_('Phone number'))
    logradouro = models.CharField(_('Street'), max_length=255)
    numero = models.PositiveIntegerField(_('Number'))
    complemento = models.CharField(_('Complement'), max_length=255, blank=True, null=True)
    bairro = models.CharField(_('Neighborhood'), max_length=255)
    cep = BRPostalCodeField(_('Postal code'))
    municipio = models.CharField(_('City'), max_length=255)
    uf = BRStateField(_('State'))
    enviar_email_destinatario = models.BooleanField(_('Send email to recipient'), default=False)
    cpf_cnpj_contabilidade = BRCNPJField(_('CNPJ of accounting'), blank=True, null=True)
    csc_nfce_producao = models.CharField(_('CSC NFCE production'), max_length=36, blank=True, null=True, help_text="CSC para emissão de NFCe em ambiente de produção. Sem este campo não será possível emitir NFCe em produção. Veja com o SEFAZ do seu estado como gerar este código.")
    id_token_nfce_producao = models.CharField(_('ID Token NFCE production'), max_length=6, blank=True, null=True, help_text="d do CSC para emissão de NFCe em ambiente de produção. Sem este campo não será possível emitir NFCe em produção.Veja com o SEFAZ do seu estado como gerar este número.")
    arquivo_certificado_base64 = models.TextField(_('Certificate file'), blank=True, null=True, help_text="Arquivo do certificado digital em formato base64")
    senha_certificado = models.CharField(_('Certificate password'), max_length=255, blank=True, null=True, help_text="Senha do certificado digital")

    def __str__(self):
        return self.nome


class Tax(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Tax')
        verbose_name_plural = _('Taxes')
    
    company = models.ForeignKey(Company, verbose_name=_('Company'), on_delete=models.CASCADE, related_name='taxes')
    data_emissao = models.DateTimeField(_('Emission date'), blank=True, null=True)
    emited = models.BooleanField(_('Emited'), default=False)
    ref = models.CharField(_('External reference'), max_length=255, blank=True, null=True)
    status = models.CharField(_('Status'), max_length=255, blank=True, null=True)
    status_sefaz = models.CharField(_('Status SEFAZ'), max_length=255, blank=True, null=True)
    mensagem_sefaz = models.CharField(_('Message SEFAZ'), max_length=255, blank=True, null=True)
    serie = models.CharField(_('Series'), max_length=255, blank=True, null=True)
    numero = models.CharField(_('Number'), max_length=255, blank=True, null=True)
    chave_nfe = models.CharField(_('NFE key'), max_length=255, blank=True, null=True)
    caminho_xml_nota_fiscal = models.CharField(_('XML path'), max_length=255, blank=True, null=True)
    caminho_danfe = models.CharField(_('DANFE path'), max_length=255, blank=True, null=True)
    qrcode_url = models.CharField(_('QRCode URL'), max_length=255, blank=True, null=True)
    url_consulta_nf = models.CharField(_('URL for consultation'), max_length=255, blank=True, null=True)


    def __str__(self):
        return self.ref
    
class TaxItems(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Tax item')
        verbose_name_plural = _('Tax items')

    tax = models.ForeignKey(Tax, verbose_name=_('Tax'), on_delete=models.CASCADE, related_name='items')
    order = models.ForeignKey(Order, verbose_name=_('Order'), on_delete=models.CASCADE, related_name='tax_items')
    numero_item = models.PositiveIntegerField(_('Item number'))
    quantidade_comercial = models.DecimalField(_('Commercial quantity'), max_digits=10, decimal_places=3)
    quantidade_tributavel = models.DecimalField(_('Taxable quantity'), max_digits=10, decimal_places=3)
    cfop = models.CharField(_('CFOP'), max_length=255)
    valor_bruto = models.DecimalField(_('Gross value'), max_digits=10, decimal_places=2)
    valor_desconto = models.DecimalField(_('Discount value'), max_digits=10, decimal_places=2, blank=True, null=True)
    valor_frete = models.DecimalField(_('Freight value'), max_digits=10, decimal_places=2, blank=True, null=True)

class PaymentItemsMethods(TimeStampedModel, UUIDModel):
    class Meta:
        verbose_name = _('Payment item method')
        verbose_name_plural = _('Payment item methods')

    payment = models.ForeignKey(Payment, verbose_name=_('Payment'), on_delete=models.CASCADE, related_name='items_methods')
    tax = models.ForeignKey(Tax, verbose_name=_('Tax'), on_delete=models.CASCADE, related_name='items_methods')
    valor = models.DecimalField(_('Value'), max_digits=10, decimal_places=2)
    cnpj_credenciadora = BRCNPJField(_('CNPJ of the card operator'), blank=True, null=True, help_text="Obrigatório se tipo_integracao for 1")
    numero_autorizacao = models.CharField(_('Authorization number'), max_length=255, blank=True, null=True, help_text="Obrigatório se tipo_integracao for 1")
    tipo_integracao = models.CharField(_('Integration type'), max_length=1, choices=TIPO_INTEGRACAO, blank=True, null=True, help_text="Informar apenas se forma_pagamento for 03 ou 04.")
    bandeira_operadora = models.CharField(_('Flag operator'), max_length=255, blank=True, null=True, help_text="Obrigatório se forma_pagamento for cartão")
