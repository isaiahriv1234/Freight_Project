#!/usr/bin/env python3
"""
DHL API Integration for Real-Time Shipping Rates
"""

import requests
import json
import os
from typing import Dict, List
from datetime import datetime

class DHLRateAPI:
    def __init__(self, api_key: str = None):
        """Initialize DHL API client"""
        self.api_key = api_key or os.getenv('DHL_API_KEY', 'your_dhl_api_key_here')
        self.base_url = "https://api-mock.dhl.com/mydhlapi"  # Test environment
        
    def get_shipping_rates(self, shipment_data: Dict) -> List[Dict]:
        """Get DHL shipping rates for a shipment"""
        if self.api_key == 'your_dhl_api_key_here':
            print("⚠️ DHL credentials not configured. Set DHL_API_KEY")
            return []
            
        rate_url = f"{self.base_url}/rates"
        
        headers = {
            'Content-Type': 'application/json',
            'DHL-API-Key': self.api_key
        }
        
        # Build DHL rate request
        request_data = {
            "customerDetails": {
                "shipperDetails": {
                    "postalAddress": {
                        "postalCode": "93407",
                        "cityName": "San Luis Obispo",
                        "countryCode": "US",
                        "provinceCode": "CA",
                        "addressLine1": "1 Grand Ave"
                    }
                },
                "receiverDetails": {
                    "postalAddress": {
                        "postalCode": shipment_data.get('dest_zip', '90210'),
                        "cityName": shipment_data.get('dest_city', 'Los Angeles'),
                        "countryCode": "US",
                        "provinceCode": shipment_data.get('dest_state', 'CA')
                    }
                }
            },
            "accounts": [{
                "typeCode": "shipper",
                "number": "123456789"  # Test account number
            }],
            "productCode": "P",  # DHL Express Worldwide
            "localProductCode": "P",
            "valueAddedServices": [],
            "productsAndServices": [{
                "productCode": "P"
            }],
            "payerCountryCode": "US",
            "plannedShippingDateAndTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S GMT+00:00"),
            "unitOfMeasurement": "metric",
            "isCustomsDeclarable": False,
            "monetaryAmount": [{
                "typeCode": "declaredValue",
                "value": shipment_data.get('order_value', 100),
                "currency": "USD"
            }],
            "requestAllValueAddedServices": False,
            "returnStandardProductsOnly": False,
            "nextBusinessDay": False,
            "packages": [{
                "typeCode": "3BX",  # Box
                "weight": shipment_data.get('weight', 5),
                "dimensions": {
                    "length": shipment_data.get('length', 12),
                    "width": shipment_data.get('width', 12),
                    "height": shipment_data.get('height', 6)
                }
            }]
        }
        
        try:
            response = requests.post(rate_url, headers=headers, json=request_data)
            if response.status_code == 200:
                return self._parse_dhl_response(response.json())
            else:
                print(f"DHL rate request failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"DHL rate request error: {e}")
            return []
    
    def _parse_dhl_response(self, response_data: Dict) -> List[Dict]:
        """Parse DHL API response into standardized format"""
        rates = []
        
        try:
            products = response_data.get('products', [])
            
            for product in products:
                product_code = product.get('productCode')
                product_name = product.get('productName')
                total_price = product.get('totalPrice', [{}])[0]
                delivery_capabilities = product.get('deliveryCapabilities', {})
                
                rates.append({
                    'carrier': 'DHL',
                    'service_code': product_code,
                    'service_name': product_name or f'DHL {product_code}',
                    'cost': float(total_price.get('price', 0)),
                    'currency': total_price.get('currencyType', 'USD'),
                    'transit_days': delivery_capabilities.get('totalTransitDays', 'N/A'),
                    'delivery_date': delivery_capabilities.get('deliveryTypeCode')
                })
        except Exception as e:
            print(f"Error parsing DHL response: {e}")
        
        return rates

def get_dhl_rates_for_order(order_value: float, weight: float = 5.0, 
                           dest_city: str = 'Los Angeles', dest_state: str = 'CA', 
                           dest_zip: str = '90210') -> List[Dict]:
    """Get DHL rates for a specific order"""
    dhl_api = DHLRateAPI()
    
    shipment_data = {
        'order_value': order_value,
        'dest_city': dest_city,
        'dest_state': dest_state,
        'dest_zip': dest_zip,
        'weight': weight,
        'length': 12,
        'width': 12,
        'height': 6
    }
    
    return dhl_api.get_shipping_rates(shipment_data)

def main():
    """Demo DHL API integration"""
    print("📦 DHL API Integration Demo")
    print("=" * 30)
    
    rates = get_dhl_rates_for_order(1000, 5.0, 'Los Angeles', 'CA', '90210')
    
    if rates:
        print(f"Found {len(rates)} DHL shipping options:")
        for rate in rates:
            print(f"• {rate['service_name']}: ${rate['cost']:.2f} ({rate['transit_days']} days)")
    else:
        print("No DHL rates available (check credentials)")

if __name__ == "__main__":
    main()