from django.db import models
from model_utils.models import (
    TimeStampedModel,
    UUIDModel,
)
from django.utils.translation import gettext as _
from apps.restaurants.models import Restaurant
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



