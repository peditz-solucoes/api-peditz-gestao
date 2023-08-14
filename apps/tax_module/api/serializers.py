from decimal import Decimal
import json
import requests
from rest_framework import serializers

from ..models import Tax
import pytz
from datetime import datetime
from django.db import transaction

from peditz.focusnfc import FocusClientApi

focus_api = FocusClientApi()

class TaxSerializer(serializers.ModelSerializer):
    tax_items = serializers.JSONField(write_only=True)
    payments_methods = serializers.JSONField(write_only=True)
    response = serializers.JSONField(read_only=True)
    class Meta:
        model = Tax
        fields = '__all__'
        read_only_fields = [
            'company',
            'data_emissao',
            'emited',
            'ref',
            'status',
            'status_sefaz',
            'mensagem_sefaz',
            'serie',
            'numero',
            'chave_nfe',
            'caminho_xml_nota_fiscal',
            'caminho_danfe',
            'qrcode_url',
            'url_consulta_nf',
            'response',
            'link'
        ]


    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        if validated_data['tax_items'] is None or validated_data['tax_items'] == 'null' or len(validated_data['tax_items']) == 0 :
            raise serializers.ValidationError({"detail":"Esta nota não possui itens."})
        if validated_data['payments_methods'] is None or validated_data['payments_methods'] == 'null' or len(validated_data['payments_methods']) == 0:
            raise serializers.ValidationError({"detail":"Esta nota não possui formas de pagamento."})
        try: 
            restaurant = user.employer.restaurant
        except AttributeError:
            try:
                restaurant = user.restaurants
            except AttributeError:
                raise serializers.ValidationError({"detail":"Este usuário não possui um restaurante."})
        try:
            company = restaurant.company
        except AttributeError:
            raise serializers.ValidationError({"detail":"Este restaurante não possui perfil de empresa para emitir nota."})
        validated_data['company'] = restaurant.company
        tax = Tax.objects.create(
            company=validated_data['company'],
        )

        fuso_horario = pytz.timezone('America/Sao_Paulo')

        note_values = {
	        "cnpj_emitente": company.cnpj,
            "data_emissao": datetime.now(fuso_horario).strftime("%Y-%m-%d %H:%M:%S"),
            "modalidade_frete": company.modalidade_frete,
            "local_destino": company.local_destino,
            "presenca_comprador": company.presenca_comprador,
            "natureza_operacao": company.natureza_operacao,
            "forma_pagamento": "1",
            "ref": str(tax.id),
	        "tipo_documento": "1",
	        "finalidade_emissao": "1",
	        "consumidor_final": "1",
	        "items": [],
	        "formas_pagamento": []
        }

        resp = focus_api.send_nfce(
            data=note_values,
            items=validated_data['tax_items'],
            payments_data=validated_data['payments_methods'],
        )
        print(resp)
        tax.data_emissao = datetime.now(fuso_horario).strftime("%Y-%m-%d %H:%M:%S")
        tax.emited = True
        tax.ref = tax.id
        tax.status = '5'
        tax.status_sefaz = resp['status_sefaz']
        tax.mensagem_sefaz = resp['mensagem_sefaz']
        tax.serie = resp['serie']
        tax.numero = resp['numero']
        tax.chave_nfe = resp['chave_nfe']
        tax.caminho_xml_nota_fiscal = resp['caminho_xml_nota_fiscal']
        tax.caminho_danfe = resp['caminho_danfe']
        tax.qrcode_url = resp['qrcode_url']
        tax.url_consulta_nf = resp['url_consulta_nf']
        tax.link = resp['caminho_danfe']
        tax.data_emissao = note_values['data_emissao']
        tax.save()
        resp['link'] = resp['url']
        resp['data_emissao'] = tax.data_emissao
        return resp


        
        


    
