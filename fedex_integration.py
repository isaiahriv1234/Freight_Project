#!/usr/bin/env python3
"""
FedEx API Integration for Real-Time Shipping Rates
"""

import requests
import json
import os
from typing import Dict, List
from datetime import datetime

class FedExRateAPI:
    def __init__(self, api_key: str = None, secret_key: str = None):
        """Initialize FedEx API client"""
        self.api_key = api_key or os.getenv('FEDEX_API_KEY', 'your_fedex_api_key_here')
        self.secret_key = secret_key or os.getenv('FEDEX_SECRET_KEY', 'your_fedex_secret_key_here')
        self.base_url = "https://apis-sandbox.fedex.com"  # Test environment
        self.access_token = None
        
    def authenticate(self) -> bool:
        """Get OAuth access token from FedEx"""
        if self.api_key == 'your_fedex_api_key_here':
            print("⚠️ FedEx credentials not configured. Set FEDEX_API_KEY and FEDEX_SECRET_KEY")
            return False
            
        auth_url = f"{self.base_url}/oauth/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.secret_key
        }
        
        try:
            response = requests.post(auth_url, headers=headers, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                return True
            else:
                print(f"FedEx authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"FedEx authentication error: {e}")
            return False
    
    def get_shipping_rates(self, shipment_data: Dict) -> List[Dict]:
        """Get FedEx shipping rates for a shipment"""
        if not self.access_token and not self.authenticate():
            return []
        
        rate_url = f"{self.base_url}/rate/v1/rates/quotes"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'X-locale': 'en_US'
        }
        
        # Build FedEx rate request
        request_data = {
            "accountNumber": {
                "value": "740561073"  # Test account number
            },
            "requestedShipment": {
                "shipper": {
                    "address": {
                        "streetLines": ["1 Grand Ave"],
                        "city": "San Luis Obispo",
                        "stateOrProvinceCode": "CA",
                        "postalCode": "93407",
                        "countryCode": "US"
                    }
                },
                "recipient": {
                    "address": {
                        "city": shipment_data.get('dest_city', 'Los Angeles'),
                        "stateOrProvinceCode": shipment_data.get('dest_state', 'CA'),
                        "postalCode": shipment_data.get('dest_zip', '90210'),
                        "countryCode": "US"
                    }
                },
                "requestedPackageLineItems": [{
                    "weight": {
                        "units": "LB",
                        "value": shipment_data.get('weight', 5)
                    },
                    "dimensions": {
                        "length": shipment_data.get('length', 12),
                        "width": shipment_data.get('width', 12),
                        "height": shipment_data.get('height', 6),
                        "units": "IN"
                    }
                }]
            }
        }
        
        try:
            response = requests.post(rate_url, headers=headers, json=request_data)
            if response.status_code == 200:
                return self._parse_fedex_response(response.json())
            else:
                print(f"FedEx rate request failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"FedEx rate request error: {e}")
            return []
    
    def _parse_fedex_response(self, response_data: Dict) -> List[Dict]:
        """Parse FedEx API response into standardized format"""
        rates = []
        
        try:
            rate_replies = response_data.get('output', {}).get('rateReplyDetails', [])
            
            for reply in rate_replies:
                service_type = reply.get('serviceType')
                rated_shipment_details = reply.get('ratedShipmentDetails', [])
                
                for detail in rated_shipment_details:
                    total_charges = detail.get('totalNetCharge', 0)
                    
                    rates.append({
                        'carrier': 'FedEx',
                        'service_code': service_type,
                        'service_name': self._get_fedex_service_name(service_type),
                        'cost': float(total_charges),
                        'currency': 'USD',
                        'transit_days': reply.get('commit', {}).get('businessDaysInTransit', 'N/A'),
                        'delivery_date': reply.get('commit', {}).get('dateDetail', {}).get('dayFormat')
                    })
        except Exception as e:
            print(f"Error parsing FedEx response: {e}")
        
        return rates
    
    def _get_fedex_service_name(self, service_code: str) -> str:
        """Convert FedEx service codes to readable names"""
        service_names = {
            'FEDEX_GROUND': 'FedEx Ground',
            'FEDEX_EXPRESS_SAVER': 'FedEx Express Saver',
            'FEDEX_2_DAY': 'FedEx 2Day',
            'STANDARD_OVERNIGHT': 'FedEx Standard Overnight',
            'PRIORITY_OVERNIGHT': 'FedEx Priority Overnight',
            'FIRST_OVERNIGHT': 'FedEx First Overnight'
        }
        return service_names.get(service_code, f'FedEx {service_code}')

def get_fedex_rates_for_order(order_value: float, weight: float = 5.0, 
                             dest_city: str = 'Los Angeles', dest_state: str = 'CA', 
                             dest_zip: str = '90210') -> List[Dict]:
    """Get FedEx rates for a specific order"""
    fedex_api = FedExRateAPI()
    
    shipment_data = {
        'dest_city': dest_city,
        'dest_state': dest_state,
        'dest_zip': dest_zip,
        'weight': weight,
        'length': 12,
        'width': 12,
        'height': 6
    }
    
    return fedex_api.get_shipping_rates(shipment_data)

def main():
    """Demo FedEx API integration"""
    print("📦 FedEx API Integration Demo")
    print("=" * 30)
    
    rates = get_fedex_rates_for_order(1000, 5.0, 'Los Angeles', 'CA', '90210')
    
    if rates:
        print(f"Found {len(rates)} FedEx shipping options:")
        for rate in rates:
            print(f"• {rate['service_name']}: ${rate['cost']:.2f} ({rate['transit_days']} days)")
    else:
        print("No FedEx rates available (check credentials)")

if __name__ == "__main__":
    main()