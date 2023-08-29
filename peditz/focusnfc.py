from datetime import datetime
from decimal import Decimal
import os
import pytz
import requests
from requests.auth import HTTPBasicAuth
from apps.financial.models import Order
from apps.restaurants.models import Product
from rest_framework import serializers
from django.db import transaction
attributes_to_check = [
    ("codigo_ncm", "código NCM"),
    ("cfop", "CFOP"),
    ("valor_unitario_tributavel", "valor unitário tributável"),
    ("valor_unitario_comercial", "valor unitário comercial"),
    ("icms_aliquota", "alíquota de ICMS"),
    ("icms_base_calculo", "base de cálculo de ICMS"),
    ("icms_origem", "origem de ICMS"),
    ("icms_situacao_tributaria", "situação tributária de ICMS"),
]

class FocusClientApi:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.api_key = os.environ.get('FOCUS_API_KEY', 'GuWQE3faeJLGp62vj2qaboDKNIjMyKoj')
        self.api_key_hml = os.environ.get('FOCUS_API_KEY_HML', 'GuWQE3faeJLGp62vj2qaboDKNIjMyKoj')
        self.base_url = os.environ.get('FOCUS_URL', 'https://homologacao.focusnfe.com.br')
        self.base_url_hml = os.environ.get('FOCUS_URL_HML', 'https://homologacao.focusnfe.com.br')
    
    @transaction.atomic
    def send_nfce(self, data, payments_data, items):
        note_values = data
        note_items = []

        for index, item in enumerate(items, 1):
            try:
                order = Order.objects.get(id=item['product_id'])
                product = order.product
            except Product.DoesNotExist:
                raise serializers.ValidationError({"detail":f"Produto {item['product_id']} produto não existe."})
            for attr, description in attributes_to_check:
                if getattr(product, attr) is None:
                    raise serializers.ValidationError({"detail": f"Produto {product.title} não possui {description}."})
            icm_base_calculation = product.icms_base_calculo * Decimal(
                round(item['quantity'], 3)
            )
            if product.calc_icms_base_calculo:
                icm_base_calculation = (product.icms_base_calculo/100 * order.total)
            icms_value = icm_base_calculation * (product.icms_aliquota/100)
            icms_value = str(round(icms_value, 2))
            icm_base_calculation = str(round(icm_base_calculation, 2))
            note_item = {
                "numero_item": index,
                "codigo_ncm": product.codigo_ncm,
                "quantidade_comercial": str(item['quantity']),
                "quantidade_tributavel": str(item['quantity']),
                "cfop": product.cfop,
                "valor_unitario_tributavel": str(order.total/order.quantity),
                "valor_unitario_comercial": str(order.total/order.quantity),
                "valor_desconto": "0.00",
                "descricao": product.title,
                "valor_bruto": str(order.total),
                "codigo_produto": product.codigo_produto,
                "icms_origem": product.icms_origem,
                "icms_situacao_tributaria": product.icms_situacao_tributaria,
                "icms_aliquota": str(product.icms_aliquota),
                "icms_base_calculo": icm_base_calculation,
                "icms_valor": icms_value,
                "icms_modalidade_base_calculo": product.icms_modalidade_base_calculo,
                "unidade_comercial": product.unidade_comercial,
                "unidade_tributavel": product.unidade_tributavel,
            }


            note_items.append(note_item)

        note_values['items'] = note_items

        payments = []

        for index, payment in enumerate(payments_data, 1):
            payment = {
                "forma_pagamento": payment['forma_pagamento'],
                "valor_pagamento": str(payment['valor_pagamento']),
            }
            payments.append(payment)

        note_values['formas_pagamento'] = payments
        url = f'{self.base_url}/v2/nfce?ref={note_values["ref"]}'
        response = requests.post(f'{url}', json=note_values, headers=self.headers, auth=HTTPBasicAuth(self.api_key, ''))
        if response.status_code < 300:
            if response.json()['status'] == 'autorizado':
                data_resp = response.json()
                data_resp['url'] = self.base_url + response.json()['caminho_danfe']
                return data_resp
        raise serializers.ValidationError({"detail": response.text})
    
    def test_product(self, product_id, company):
        try:
                product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"detail":f"Produto {product_id} produto não existe."})
        for attr, description in attributes_to_check:
            if getattr(product, attr) is None:
                raise serializers.ValidationError({"detail": f"Produto {product.title} não possui {description}."})
        
        fuso_horario = pytz.timezone('America/Sao_Paulo')
        icm_base_calculation = product.icms_base_calculo * 1
        icms_value = icm_base_calculation * (product.icms_aliquota/100)
        icms_value = str(round(icms_value, 2))
        icm_base_calculation = str(round(icm_base_calculation, 2))
        note_values = {
	        "cnpj_emitente": company.cnpj,
            "data_emissao": datetime.now(fuso_horario).strftime("%Y-%m-%d %H:%M:%S"),
            "modalidade_frete": company.modalidade_frete,
            "local_destino": company.local_destino,
            "presenca_comprador": company.presenca_comprador,
            "natureza_operacao": company.natureza_operacao,
            "forma_pagamento": "1",
            "ref": datetime.now(fuso_horario).strftime("%Y-%m-%d %H:%M:%S") + str(product.id),
	        "tipo_documento": "1",
	        "finalidade_emissao": "1",
	        "consumidor_final": "1",
	        "items": [
                {
                "numero_item": '1',
                "codigo_ncm": product.codigo_ncm,
                "quantidade_comercial": 1,
                "quantidade_tributavel": 1,
                "cfop": product.cfop,
                "valor_unitario_tributavel": str(product.valor_unitario_tributavel),
                "valor_unitario_comercial": str(product.valor_unitario_comercial),
                "valor_desconto": "0.00",
                "descricao": product.title,
                "valor_bruto": str(product.valor_unitario_comercial * 1),
                "codigo_produto": product.codigo_produto,
                "icms_origem": product.icms_origem,
                "icms_situacao_tributaria": product.icms_situacao_tributaria,
                "icms_aliquota": str(product.icms_aliquota),
                "icms_base_calculo": icm_base_calculation,
                "icms_valor": icms_value,
                "icms_modalidade_base_calculo": product.icms_modalidade_base_calculo,
                "unidade_comercial": product.unidade_comercial,
                "unidade_tributavel": product.unidade_tributavel,
            }
            ],
	        "formas_pagamento": [
                {
                "forma_pagamento": "1",
                "valor_pagamento": str(product.valor_unitario_comercial * 1),
                }
            ]
        }

        url = f'{self.base_url_hml}/v2/nfce?ref={note_values["ref"]}'
        response = requests.post(f'{url}', json=note_values, headers=self.headers, auth=HTTPBasicAuth(self.api_key_hml, ''))
        if response.status_code < 300:
            if response.json()['status'] == 'autorizado':
                data_resp = response.json()
                data_resp['url'] = self.base_url_hml + response.json()['caminho_danfe']
                return data_resp
        raise serializers.ValidationError({"detail": response.text})
        