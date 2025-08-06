import os
from datetime import datetime
from typing import Dict, List, Optional

try:
    import easypost
    EASYPOST_AVAILABLE = True
except ImportError:
    EASYPOST_AVAILABLE = False

class EasyPostIntegration:
    def __init__(self):
        self.api_key = os.getenv('EASYPOST_API_KEY')
        if self.api_key and EASYPOST_AVAILABLE:
            self.client = easypost.EasyPostClient(self.api_key)
    
    def get_shipping_rates(self, shipment_data: Dict) -> List[Dict]:
        """Get shipping rates from multiple carriers via EasyPost"""
        if not EASYPOST_AVAILABLE or not self.api_key:
            return self._get_mock_rates()
            
        try:
            shipment = self.client.shipment.create(
                to_address=shipment_data['to_address'],
                from_address=shipment_data['from_address'],
                parcel=shipment_data['parcel']
            )
            
            rates = []
            for rate in shipment.rates:
                rates.append({
                    'carrier': rate.carrier,
                    'service': rate.service,
                    'cost': float(rate.rate),
                    'currency': rate.currency,
                    'estimated_days': rate.delivery_days,
                    'rate_id': rate.id
                })
            
            return sorted(rates, key=lambda x: x['cost'])
            
        except Exception as e:
            print(f"Error getting rates: {e}")
            return self._get_mock_rates()
    
    def create_shipping_label(self, rate_id: str) -> Dict:
        """Create shipping label using selected rate"""
        if not EASYPOST_AVAILABLE or not self.api_key:
            return {'success': False, 'error': 'EasyPost not available'}
            
        try:
            shipment = self.client.shipment.buy(rate_id)
            
            return {
                'success': True,
                'tracking_number': shipment.tracking_code,
                'label_url': shipment.postage_label.label_url,
                'cost': float(shipment.selected_rate.rate)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def track_shipment(self, tracking_number: str, carrier: str) -> Dict:
        """Track shipment status"""
        if not EASYPOST_AVAILABLE or not self.api_key:
            return {'error': 'EasyPost not available'}
            
        try:
            tracker = self.client.tracker.create(tracking_code=tracking_number, carrier=carrier)
            
            return {
                'tracking_number': tracking_number,
                'carrier': carrier,
                'status': tracker.status,
                'est_delivery_date': tracker.est_delivery_date,
                'tracking_details': [
                    {
                        'status': detail.status,
                        'message': detail.message,
                        'datetime': detail.datetime,
                        'location': detail.tracking_location
                    } for detail in tracker.tracking_details
                ]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_mock_rates(self) -> List[Dict]:
        """Mock rates for testing when API not available"""
        return [
            {'carrier': 'UPS', 'service': 'Ground', 'cost': 12.50, 'currency': 'USD', 'estimated_days': 3},
            {'carrier': 'FedEx', 'service': 'Ground', 'cost': 13.25, 'currency': 'USD', 'estimated_days': 3},
            {'carrier': 'UPS', 'service': '2nd Day Air', 'cost': 25.75, 'currency': 'USD', 'estimated_days': 2},
            {'carrier': 'FedEx', 'service': '2Day', 'cost': 26.50, 'currency': 'USD', 'estimated_days': 2},
            {'carrier': 'DHL', 'service': 'Express', 'cost': 35.00, 'currency': 'USD', 'estimated_days': 1}
        ]

# Example usage
if __name__ == "__main__":
    easypost_api = EasyPostIntegration()
    
    # Test shipment data
    test_shipment = {
        'from_address': {
            'name': 'Cal Poly SLO',
            'street1': '1 Grand Ave',
            'city': 'San Luis Obispo',
            'state': 'CA',
            'zip': '93407',
            'country': 'US'
        },
        'to_address': {
            'name': 'Test Recipient',
            'street1': '123 Main St',
            'city': 'Los Angeles',
            'state': 'CA',
            'zip': '90210',
            'country': 'US'
        },
        'parcel': {
            'length': 10,
            'width': 8,
            'height': 6,
            'weight': 32  # in ounces
        }
    }
    
    rates = easypost_api.get_shipping_rates(test_shipment)
    print("Available shipping rates:")
    for rate in rates:
        print(f"{rate['carrier']} {rate['service']}: ${rate['cost']} ({rate['estimated_days']} days)")