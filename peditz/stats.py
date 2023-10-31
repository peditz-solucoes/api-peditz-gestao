import os
from typing import Optional
import requests
from rest_framework import serializers
from datetime import datetime, timedelta
class StatsApi:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'accept': 'application/json'
        }
        self.base_url = os.environ.get('STATS_API_URL', 'http://localhost:3333')
    
    def get_products_stats(self, restaurant_id, initial_date, final_date, category_id: Optional[str] = ''):
        if not initial_date:
            initial_date = datetime.now() - timedelta(days=7)
            initial_date = initial_date.strftime("%Y-%m-%d %H:%M:%S")
        if not final_date:
            final_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        url = f'{self.base_url}/products/{restaurant_id}?initial_date={initial_date}&final_date={final_date}&category_id={category_id}'
        headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise serializers.ValidationError({"detail": response.json()})