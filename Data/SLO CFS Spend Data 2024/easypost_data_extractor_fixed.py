#!/usr/bin/env python3
"""
EasyPost Data Extractor - Fixed Version
Retrieves all shipping data and creates downloadable files for team upload
"""

import pandas as pd
import easypost
import os
import json
from datetime import datetime
from dotenv import load_dotenv

class EasyPostDataExtractor:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('EASYPOST_API_KEY', 'EZTKb7ab379918a0406aac1cd2a44582d931BDJfUVZ3aOi70rManrbpXg')
        self.client = easypost.EasyPostClient(self.api_key)
        
    def get_all_shipments(self):
        """Retrieve all shipments from EasyPost"""
        print("📦 Retrieving all shipments from EasyPost...")
        
        try:
            shipments = self.client.shipment.all(page_size=100)
            shipment_data = []
            
            # Handle both dict and object responses
            shipment_list = shipments.get('shipments', []) if isinstance(shipments, dict) else getattr(shipments, 'shipments', [])
            
            for shipment in shipment_list:
                shipment_info = {
                    'shipment_id': getattr(shipment, 'id', ''),
                    'tracking_code': getattr(shipment, 'tracking_code', ''),
                    'status': getattr(shipment, 'status', ''),
                    'created_at': getattr(shipment, 'created_at', ''),
                    'updated_at': getattr(shipment, 'updated_at', ''),
                    'from_name': getattr(shipment.from_address, 'name', '') if hasattr(shipment, 'from_address') and shipment.from_address else '',
                    'from_city': getattr(shipment.from_address, 'city', '') if hasattr(shipment, 'from_address') and shipment.from_address else '',
                    'from_state': getattr(shipment.from_address, 'state', '') if hasattr(shipment, 'from_address') and shipment.from_address else '',
                    'to_name': getattr(shipment.to_address, 'name', '') if hasattr(shipment, 'to_address') and shipment.to_address else '',
                    'to_city': getattr(shipment.to_address, 'city', '') if hasattr(shipment, 'to_address') and shipment.to_address else '',
                    'to_state': getattr(shipment.to_address, 'state', '') if hasattr(shipment, 'to_address') and shipment.to_address else '',
                    'selected_rate_cost': float(getattr(shipment.selected_rate, 'rate', 0)) if hasattr(shipment, 'selected_rate') and shipment.selected_rate else 0,
                    'selected_rate_carrier': getattr(shipment.selected_rate, 'carrier', '') if hasattr(shipment, 'selected_rate') and shipment.selected_rate else '',
                    'selected_rate_service': getattr(shipment.selected_rate, 'service', '') if hasattr(shipment, 'selected_rate') and shipment.selected_rate else '',
                    'parcel_weight': getattr(shipment.parcel, 'weight', 0) if hasattr(shipment, 'parcel') and shipment.parcel else 0,
                    'parcel_length': getattr(shipment.parcel, 'length', 0) if hasattr(shipment, 'parcel') and shipment.parcel else 0,
                    'parcel_width': getattr(shipment.parcel, 'width', 0) if hasattr(shipment, 'parcel') and shipment.parcel else 0,
                    'parcel_height': getattr(shipment.parcel, 'height', 0) if hasattr(shipment, 'parcel') and shipment.parcel else 0
                }
                shipment_data.append(shipment_info)
            
            print(f"✅ Retrieved {len(shipment_data)} shipments")
            return shipment_data
            
        except Exception as e:
            print(f"❌ Error retrieving shipments: {e}")
            return []
    
    def get_all_addresses(self):
        """Retrieve all addresses from EasyPost"""
        print("📍 Retrieving all addresses from EasyPost...")
        
        try:
            addresses = self.client.address.all(page_size=100)
            address_data = []
            
            # Handle both dict and object responses
            address_list = addresses.get('addresses', []) if isinstance(addresses, dict) else getattr(addresses, 'addresses', [])
            
            for address in address_list:
                address_info = {
                    'address_id': getattr(address, 'id', ''),
                    'name': getattr(address, 'name', ''),
                    'company': getattr(address, 'company', ''),
                    'street1': getattr(address, 'street1', ''),
                    'street2': getattr(address, 'street2', ''),
                    'city': getattr(address, 'city', ''),
                    'state': getattr(address, 'state', ''),
                    'zip': getattr(address, 'zip', ''),
                    'country': getattr(address, 'country', ''),
                    'phone': getattr(address, 'phone', ''),
                    'email': getattr(address, 'email', ''),
                    'created_at': getattr(address, 'created_at', ''),
                    'updated_at': getattr(address, 'updated_at', ''),
                    'verified': getattr(address, 'verified', False)
                }
                address_data.append(address_info)
            
            print(f"✅ Retrieved {len(address_data)} addresses")
            return address_data
            
        except Exception as e:
            print(f"❌ Error retrieving addresses: {e}")
            return []
    
    def get_sample_rates(self):
        """Get sample shipping rates for common routes"""
        print("💰 Generating sample shipping rates...")
        
        sample_routes = [
            {
                'from': {'name': 'Cal Poly SLO', 'street1': '1 Grand Ave', 'city': 'San Luis Obispo', 'state': 'CA', 'zip': '93407'},
                'to': {'name': 'Los Angeles Office', 'street1': '123 Main St', 'city': 'Los Angeles', 'state': 'CA', 'zip': '90210'},
                'parcel': {'length': 12, 'width': 8, 'height': 6, 'weight': 16}
            },
            {
                'from': {'name': 'Cal Poly SLO', 'street1': '1 Grand Ave', 'city': 'San Luis Obispo', 'state': 'CA', 'zip': '93407'},
                'to': {'name': 'San Francisco Office', 'street1': '456 Market St', 'city': 'San Francisco', 'state': 'CA', 'zip': '94102'},
                'parcel': {'length': 10, 'width': 10, 'height': 8, 'weight': 24}
            },
            {
                'from': {'name': 'Cal Poly SLO', 'street1': '1 Grand Ave', 'city': 'San Luis Obispo', 'state': 'CA', 'zip': '93407'},
                'to': {'name': 'Sacramento Office', 'street1': '789 Capitol Ave', 'city': 'Sacramento', 'state': 'CA', 'zip': '95814'},
                'parcel': {'length': 14, 'width': 12, 'height': 10, 'weight': 32}
            }
        ]
        
        all_rates = []
        
        for i, route in enumerate(sample_routes):
            try:
                shipment = self.client.shipment.create(
                    to_address=route['to'],
                    from_address=route['from'],
                    parcel=route['parcel']
                )
                
                # Handle rates - could be list or dict
                rates = getattr(shipment, 'rates', [])
                if not isinstance(rates, list):
                    rates = [rates] if rates else []
                
                for rate in rates:
                    rate_info = {
                        'route_id': f"route_{i+1}",
                        'from_city': route['from']['city'],
                        'to_city': route['to']['city'],
                        'carrier': getattr(rate, 'carrier', ''),
                        'service': getattr(rate, 'service', ''),
                        'rate': float(getattr(rate, 'rate', 0)),
                        'currency': getattr(rate, 'currency', 'USD'),
                        'delivery_days': getattr(rate, 'delivery_days', None),
                        'delivery_date': getattr(rate, 'delivery_date', ''),
                        'parcel_weight': route['parcel']['weight'],
                        'parcel_dimensions': f"{route['parcel']['length']}x{route['parcel']['width']}x{route['parcel']['height']}",
                        'created_at': datetime.now().isoformat()
                    }
                    all_rates.append(rate_info)
                
                print(f"✅ Generated rates for route {i+1}: {route['from']['city']} → {route['to']['city']}")
                
            except Exception as e:
                print(f"❌ Error generating rates for route {i+1}: {e}")
        
        print(f"✅ Generated {len(all_rates)} shipping rates")
        return all_rates
    
    def create_downloadable_files(self):
        """Create downloadable files for team upload"""
        print("📁 Creating downloadable files...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get all data
        shipments = self.get_all_shipments()
        addresses = self.get_all_addresses()
        rates = self.get_sample_rates()
        
        # Create DataFrames
        files_created = []
        
        if shipments:
            shipments_df = pd.DataFrame(shipments)
            shipments_file = f"easypost_shipments_{timestamp}.csv"
            shipments_df.to_csv(shipments_file, index=False)
            files_created.append(shipments_file)
            print(f"📄 Created: {shipments_file}")
        
        if addresses:
            addresses_df = pd.DataFrame(addresses)
            addresses_file = f"easypost_addresses_{timestamp}.csv"
            addresses_df.to_csv(addresses_file, index=False)
            files_created.append(addresses_file)
            print(f"📄 Created: {addresses_file}")
        
        if rates:
            rates_df = pd.DataFrame(rates)
            rates_file = f"easypost_shipping_rates_{timestamp}.csv"
            rates_df.to_csv(rates_file, index=False)
            files_created.append(rates_file)
            print(f"📄 Created: {rates_file}")
        
        # Create combined dataset
        combined_data = {
            'extraction_timestamp': timestamp,
            'api_key_used': self.api_key[:10] + "...",
            'total_shipments': len(shipments),
            'total_addresses': len(addresses),
            'total_rates': len(rates),
            'files_created': files_created
        }
        
        # Save metadata
        metadata_file = f"easypost_extraction_metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(combined_data, f, indent=2)
        files_created.append(metadata_file)
        print(f"📄 Created: {metadata_file}")
        
        # Create master dataset for model upload
        master_data = []
        
        # Add procurement data if available
        try:
            procurement_df = pd.read_csv('Cleaned_Procurement_Data.csv')
            for _, row in procurement_df.iterrows():
                master_data.append({
                    'data_type': 'procurement',
                    'supplier_name': row['Supplier_Name'],
                    'total_amount': row['Total_Amount'],
                    'shipping_cost': row['Shipping_Cost'],
                    'carrier': row['Carrier'],
                    'lead_time_days': row['Lead_Time_Days'],
                    'diversity_category': row['Supplier_Diversity_Category'],
                    'consolidation_opportunity': row['Consolidation_Opportunity'],
                    'source': 'internal_procurement'
                })
        except:
            print("⚠️  Procurement data not found")
        
        # Add EasyPost rates
        for rate in rates:
            master_data.append({
                'data_type': 'shipping_rate',
                'supplier_name': f"{rate['from_city']}_to_{rate['to_city']}",
                'total_amount': 0,
                'shipping_cost': rate['rate'],
                'carrier': rate['carrier'],
                'lead_time_days': rate['delivery_days'] or 3,
                'diversity_category': 'external_rate',
                'consolidation_opportunity': 'medium',
                'source': 'easypost_api'
            })
        
        if master_data:
            master_df = pd.DataFrame(master_data)
            master_file = f"master_shipping_dataset_{timestamp}.csv"
            master_df.to_csv(master_file, index=False)
            files_created.append(master_file)
            print(f"📄 Created: {master_file}")
        
        return files_created
    
    def generate_model_ready_dataset(self):
        """Generate a clean dataset ready for ML model upload"""
        print("🤖 Generating model-ready dataset...")
        
        try:
            # Load procurement data
            df = pd.read_csv('Cleaned_Procurement_Data.csv')
            
            # Get sample rates for enhancement
            rates = self.get_sample_rates()
            
            # Create model features
            model_data = []
            
            for _, row in df.iterrows():
                # Base features from procurement data
                features = {
                    'order_value': row['Total_Amount'],
                    'current_shipping_cost': row['Shipping_Cost'],
                    'current_carrier': row['Carrier'],
                    'lead_time': row['Lead_Time_Days'],
                    'supplier_diversity': row['Supplier_Diversity_Category'],
                    'consolidation_score': {'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}.get(row['Consolidation_Opportunity'], 2),
                    'shipping_ratio': row['Shipping_Cost'] / row['Total_Amount'] if row['Total_Amount'] > 0 else 0,
                    'order_frequency': row['Order_Frequency'],
                    'geographic_zone': row['Geographic_Location']
                }
                
                # Add EasyPost rate alternatives (using sample data)
                if rates:
                    # Calculate average rates by carrier
                    ups_rates = [r['rate'] for r in rates if r['carrier'] == 'UPS']
                    fedex_rates = [r['rate'] for r in rates if r['carrier'] == 'FedEx']
                    usps_rates = [r['rate'] for r in rates if r['carrier'] == 'USPS']
                    
                    features.update({
                        'alternative_cost_ups': sum(ups_rates) / len(ups_rates) if ups_rates else None,
                        'alternative_cost_fedex': sum(fedex_rates) / len(fedex_rates) if fedex_rates else None,
                        'alternative_cost_usps': sum(usps_rates) / len(usps_rates) if usps_rates else None,
                        'potential_savings': 0,
                        'optimization_opportunity': 0
                    })
                    
                    # Calculate potential savings
                    all_alt_rates = [r for r in [features['alternative_cost_ups'], features['alternative_cost_fedex'], features['alternative_cost_usps']] if r is not None]
                    if all_alt_rates and row['Shipping_Cost'] > 0:
                        min_alt_rate = min(all_alt_rates)
                        features['potential_savings'] = max(0, row['Shipping_Cost'] - min_alt_rate)
                        features['optimization_opportunity'] = 1 if row['Shipping_Cost'] > min_alt_rate else 0
                
                model_data.append(features)
            
            # Create model dataset
            model_df = pd.DataFrame(model_data)
            
            # Clean and prepare for ML
            model_df = model_df.fillna(0)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_file = f"ml_ready_shipping_dataset_{timestamp}.csv"
            model_df.to_csv(model_file, index=False)
            
            print(f"🤖 Model-ready dataset created: {model_file}")
            print(f"📊 Features: {len(model_df.columns)}")
            print(f"📈 Records: {len(model_df)}")
            
            return model_file
            
        except Exception as e:
            print(f"❌ Error creating model dataset: {e}")
            return None

def main():
    """Main extraction function"""
    print("🚀 EASYPOST DATA EXTRACTION FOR TEAM UPLOAD")
    print("=" * 60)
    
    extractor = EasyPostDataExtractor()
    
    # Create all downloadable files
    files = extractor.create_downloadable_files()
    
    # Create model-ready dataset
    model_file = extractor.generate_model_ready_dataset()
    if model_file:
        files.append(model_file)
    
    print(f"\n✅ EXTRACTION COMPLETE!")
    print(f"📁 Files created for team upload:")
    for file in files:
        print(f"   - {file}")
    
    print(f"\n🎯 RECOMMENDED FOR MODEL UPLOAD:")
    print(f"   - ml_ready_shipping_dataset_*.csv (primary)")
    print(f"   - master_shipping_dataset_*.csv (backup)")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Share files with your team")
    print(f"   2. Upload to your ML model platform")
    print(f"   3. Use for shipping optimization training")

if __name__ == "__main__":
    main()