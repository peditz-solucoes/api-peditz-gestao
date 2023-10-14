import os
import requests
from rest_framework import serializers
from apps.ifood.models import IfoodUserCredentials
class IfoodClientApi:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'accept': 'application/json'
        }
        self.base_url = os.environ.get('IFOOD_URL', 'https://merchant-api.ifood.com.br')
        self.client_id = os.environ.get('IFOOD_CLIENT_ID', 'e195a843-debc-4581-a1f3-7f467c0b315e')
        self.client_secret = os.environ.get('IFOOD_CLIENT_SECRET', 'ylw7nd5fa2ri3gzanrviux34zrcm2270t5eme4q0kgfod471trlimgrm0lnihig9215r3vfkrdmfrq5ttbu9slqfs7w9u79fxxf')
    
    def get_user_code(self):
        url = f'{self.base_url}/authentication/v1.0/oauth/userCode'
        data = {
            'clientId': self.client_id
        }

        response = requests.post(url, data=data, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise serializers.ValidationError({"detail": response.json()})
        
    def get_auth_token(self, authorization_code, authorization_code_verifier):
        url = f'{self.base_url}/authentication/v1.0/oauth/token'
        
        data = {
            'grantType': 'authorization_code',
            'clientSecret': self.client_secret,
            'clientId': self.client_id,
            'authorizationCode': authorization_code,
            'authorizationCodeVerifier': authorization_code_verifier
        }

        response = requests.post(url, data=data, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise serializers.ValidationError({"detail": response.json()})
        
    def get_merchants(self, token):
        url = f'{self.base_url}/merchant/v1.0/merchants'
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json',
            'authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise serializers.ValidationError({"detail": response.json()})
        
    def get_refresh_token(self, refresh_token):
        url = f'{self.base_url}/authentication/v1.0/oauth/token'
        data = {
            'grantType': 'refresh_token',
            'clientSecret': self.client_secret,
            'clientId': self.client_id,
            'refreshToken': refresh_token
        }

        response = requests.post(url, data=data, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise serializers.ValidationError({"detail": response.json()})
        
    def get_merchant(self, token, merchant_id):
        url = f'{self.base_url}/merchant/v1.0/merchants/{merchant_id}'
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json',
            'authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise serializers.ValidationError({"detail": response.json()})