import os
from datetime import datetime
from typing import Dict, List, Optional

try:
    import shippo
    SHIPPO_AVAILABLE = True
except ImportError:
    SHIPPO_AVAILABLE = False

class ShippoIntegration:
    def __init__(self):
        self.api_token = os.getenv('SHIPPO_API_TOKEN')
        if self.api_token and SHIPPO_AVAILABLE:
            shippo.config.api_key = self.api_token
    
    def get_shipping_rates(self, shipment_data: Dict) -> List[Dict]:
        """Get shipping rates from multiple carriers via Shippo"""
        if not SHIPPO_AVAILABLE or not self.api_token:
            return self._get_mock_rates()
            
        try:
            # Create address objects
            address_from = shippo.Address.create(**shipment_data['from_address'])
            address_to = shippo.Address.create(**shipment_data['to_address'])
            
            # Create parcel object
            parcel = shippo.Parcel.create(**shipment_data['parcel'])
            
            # Create shipment to get rates
            shipment = shippo.Shipment.create(
                address_from=address_from,
                address_to=address_to,
                parcels=[parcel],
                async_=False
            )
            
            rates = []
            for rate in shipment.rates:
                rates.append({
                    'carrier': rate.provider,
                    'service': rate.servicelevel.name,
                    'cost': float(rate.amount),
                    'currency': rate.currency,
                    'estimated_days': rate.estimated_days,
                    'rate_id': rate.object_id
                })
            
            return sorted(rates, key=lambda x: x['cost'])
            
        except Exception as e:
            print(f"Error getting rates: {e}")
            return self._get_mock_rates()
    
    def create_shipping_label(self, rate_id: str) -> Dict:
        """Create shipping label using selected rate"""
        if not SHIPPO_AVAILABLE or not self.api_token:
            return {'success': False, 'error': 'Shippo not available'}
            
        try:
            transaction = shippo.Transaction.create(
                rate=rate_id,
                label_file_type="PDF",
                async_=False
            )
            
            return {
                'success': True,
                'tracking_number': transaction.tracking_number,
                'label_url': transaction.label_url,
                'cost': float(transaction.rate.amount)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def track_shipment(self, tracking_number: str, carrier: str) -> Dict:
        """Track shipment status"""
        if not SHIPPO_AVAILABLE or not self.api_token:
            return {'error': 'Shippo not available'}
            
        try:
            tracking = shippo.Track.get_status(carrier, tracking_number)
            
            return {
                'tracking_number': tracking_number,
                'carrier': carrier,
                'status': tracking.tracking_status,
                'location': tracking.tracking_location,
                'eta': tracking.eta,
                'tracking_history': [
                    {
                        'status': event.status,
                        'location': event.location,
                        'datetime': event.status_date
                    } for event in tracking.tracking_history
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
    shippo_api = ShippoIntegration()
    
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
            'length': '10',
            'width': '8',
            'height': '6',
            'distance_unit': 'in',
            'weight': '2',
            'mass_unit': 'lb'
        }
    }
    
    rates = shippo_api.get_shipping_rates(test_shipment)
    print("Available shipping rates:")
    for rate in rates:
        print(f"{rate['carrier']} {rate['service']}: ${rate['cost']} ({rate['estimated_days']} days)")