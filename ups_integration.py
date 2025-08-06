#!/usr/bin/env python3
"""
UPS API Integration for Real-Time Shipping Rates
"""

import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class UPSRateAPI:
    def __init__(self, client_id: str = None, client_secret: str = None):
        """Initialize UPS API client"""
        self.client_id = client_id or os.getenv('UPS_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('UPS_CLIENT_SECRET')
        self.base_url = "https://wwwcie.ups.com/api"  # Test environment
        self.access_token = None
        
    def authenticate(self) -> bool:
        """Get OAuth access token from UPS"""
        if not self.client_id or not self.client_secret:
            print("⚠️ UPS credentials not found. Set UPS_CLIENT_ID and UPS_CLIENT_SECRET environment variables")
            return False
            
        auth_url = f"{self.base_url}/security/v1/oauth/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-merchant-id': self.client_id
        }
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(auth_url, headers=headers, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                return True
            else:
                print(f"UPS authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"UPS authentication error: {e}")
            return False
    
    def get_shipping_rates(self, shipment_data: Dict) -> List[Dict]:
        """Get UPS shipping rates for a shipment"""
        if not self.access_token and not self.authenticate():
            return []
        
        rate_url = f"{self.base_url}/rating/v1/Rate"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'transId': f'freight-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'transactionSrc': 'FreightOptimizer'
        }
        
        # Build UPS rate request
        request_data = {
            "RateRequest": {
                "Request": {
                    "RequestOption": "Rate",
                    "TransactionReference": {
                        "CustomerContext": "Freight Rate Request"
                    }
                },
                "Shipment": {
                    "Shipper": {
                        "Name": "Cal Poly SLO",
                        "Address": {
                            "AddressLine": ["1 Grand Ave"],
                            "City": "San Luis Obispo",
                            "StateProvinceCode": "CA",
                            "PostalCode": "93407",
                            "CountryCode": "US"
                        }
                    },
                    "ShipTo": {
                        "Name": shipment_data.get('recipient_name', 'Recipient'),
                        "Address": {
                            "City": shipment_data.get('dest_city', 'Los Angeles'),
                            "StateProvinceCode": shipment_data.get('dest_state', 'CA'),
                            "PostalCode": shipment_data.get('dest_zip', '90210'),
                            "CountryCode": "US"
                        }
                    },
                    "Package": [{
                        "PackagingType": {
                            "Code": "02",  # Customer Supplied Package
                            "Description": "Package"
                        },
                        "Dimensions": {
                            "UnitOfMeasurement": {
                                "Code": "IN"
                            },
                            "Length": str(shipment_data.get('length', 12)),
                            "Width": str(shipment_data.get('width', 12)),
                            "Height": str(shipment_data.get('height', 6))
                        },
                        "PackageWeight": {
                            "UnitOfMeasurement": {
                                "Code": "LBS"
                            },
                            "Weight": str(shipment_data.get('weight', 5))
                        }
                    }]
                }
            }
        }
        
        try:
            response = requests.post(rate_url, headers=headers, json=request_data)
            if response.status_code == 200:
                return self._parse_ups_response(response.json())
            else:
                print(f"UPS rate request failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"UPS rate request error: {e}")
            return []
    
    def _parse_ups_response(self, response_data: Dict) -> List[Dict]:
        """Parse UPS API response into standardized format"""
        rates = []
        
        try:
            rate_response = response_data.get('RateResponse', {})
            rated_shipments = rate_response.get('RatedShipment', [])
            
            if not isinstance(rated_shipments, list):
                rated_shipments = [rated_shipments]
            
            for shipment in rated_shipments:
                service = shipment.get('Service', {})
                total_charges = shipment.get('TotalCharges', {})
                
                rates.append({
                    'carrier': 'UPS',
                    'service_code': service.get('Code'),
                    'service_name': self._get_service_name(service.get('Code')),
                    'cost': float(total_charges.get('MonetaryValue', 0)),
                    'currency': total_charges.get('CurrencyCode', 'USD'),
                    'transit_days': shipment.get('GuaranteedDelivery', {}).get('BusinessDaysInTransit', 'N/A'),
                    'delivery_date': shipment.get('GuaranteedDelivery', {}).get('DeliveryByTime')
                })
        except Exception as e:
            print(f"Error parsing UPS response: {e}")
        
        return rates
    
    def _get_service_name(self, service_code: str) -> str:
        """Convert UPS service codes to readable names"""
        service_names = {
            '01': 'UPS Next Day Air',
            '02': 'UPS 2nd Day Air',
            '03': 'UPS Ground',
            '12': 'UPS 3 Day Select',
            '13': 'UPS Next Day Air Saver',
            '14': 'UPS Next Day Air Early',
            '59': 'UPS 2nd Day Air A.M.'
        }
        return service_names.get(service_code, f'UPS Service {service_code}')

def get_ups_rates_for_order(order_value: float, weight: float = 5.0, 
                           dest_city: str = 'Los Angeles', dest_state: str = 'CA', 
                           dest_zip: str = '90210') -> List[Dict]:
    """Get UPS rates for a specific order"""
    ups_api = UPSRateAPI()
    
    shipment_data = {
        'recipient_name': 'Customer',
        'dest_city': dest_city,
        'dest_state': dest_state,
        'dest_zip': dest_zip,
        'weight': weight,
        'length': 12,
        'width': 12,
        'height': 6
    }
    
    return ups_api.get_shipping_rates(shipment_data)

def main():
    """Demo UPS API integration"""
    print("📦 UPS API Integration Demo")
    print("=" * 30)
    
    # Test with sample shipment
    rates = get_ups_rates_for_order(1000, 5.0, 'Los Angeles', 'CA', '90210')
    
    if rates:
        print(f"Found {len(rates)} UPS shipping options:")
        for rate in rates:
            print(f"• {rate['service_name']}: ${rate['cost']:.2f} ({rate['transit_days']} days)")
    else:
        print("No UPS rates available (check credentials)")

if __name__ == "__main__":
    main()