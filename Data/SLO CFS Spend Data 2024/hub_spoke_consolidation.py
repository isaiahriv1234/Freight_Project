#!/usr/bin/env python3
"""
Hub and Spoke Consolidation Model for Cal Poly SLO
Consolidates smaller packages through regional hubs to reduce costs and improve efficiency
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class HubSpokeConsolidation:
    def __init__(self, data_file):
        self.df = pd.read_csv(data_file)
        self.destination = "Cal Poly SLO"
        self.destination_zip = "93407"
        
        # Define regional hubs for consolidation
        self.regional_hubs = {
            'Los Angeles Hub': {
                'location': 'Los Angeles, CA',
                'zip': '90210',
                'coverage_radius': 150,  # miles
                'consolidation_capacity': 50000,  # dollars
                'processing_time': 1  # days
            },
            'San Francisco Hub': {
                'location': 'San Francisco, CA', 
                'zip': '94102',
                'coverage_radius': 200,
                'consolidation_capacity': 75000,
                'processing_time': 1
            },
            'Sacramento Hub': {
                'location': 'Sacramento, CA',
                'zip': '95814', 
                'coverage_radius': 100,
                'consolidation_capacity': 30000,
                'processing_time': 1
            }
        }
        
        # Consolidation thresholds and savings
        self.consolidation_rules = {
            'min_package_value': 50,      # Minimum value to consolidate
            'max_package_value': 2000,    # Maximum for small package consolidation
            'consolidation_window': 3,    # Days to wait for consolidation
            'volume_discount_threshold': 1000,  # Minimum consolidated value for discount
            'shipping_savings_rate': 0.35,      # 35% savings on consolidated shipping
            'admin_cost_reduction': 25,         # $25 saved per consolidated order
            'hub_processing_cost': 15           # $15 cost per package at hub
        }
    
    def assign_packages_to_hubs(self):
        """Assign packages to appropriate regional hubs based on supplier location"""
        
        # Simulate supplier locations (in real implementation, use actual addresses)
        supplier_locations = {
            'ADVANCED BIOMEDICAL': 'Los Angeles Hub',
            'CENTRAL COAST SPECIALTY I': 'San Francisco Hub', 
            'DEEP BLUE INTEGRATION INC': 'Sacramento Hub',
            'A-TOWN AV INC': 'Los Angeles Hub'
        }
        
        # Add hub assignment to dataframe
        self.df['assigned_hub'] = self.df['supplier_name'].map(supplier_locations)
        self.df['hub_assignment'] = self.df['assigned_hub'].fillna('Direct Ship')
        
        return self.df
    
    def identify_consolidation_candidates(self):
        """Identify packages suitable for hub consolidation"""
        
        rules = self.consolidation_rules
        
        # Filter packages suitable for consolidation
        candidates = self.df[
            (self.df['total_amount'] >= rules['min_package_value']) &
            (self.df['total_amount'] <= rules['max_package_value']) &
            (self.df['shipping_cost'] > 0) &
            (self.df['hub_assignment'] != 'Direct Ship')
        ].copy()
        
        candidates['consolidation_eligible'] = True
        
        return candidates
    
    def create_consolidated_shipments(self):
        """Create consolidated shipments through hub and spoke model"""
        
        candidates = self.identify_consolidation_candidates()
        consolidated_shipments = []
        
        # Group by hub and create consolidated shipments
        for hub_name, hub_packages in candidates.groupby('hub_assignment'):
            if hub_name == 'Direct Ship':
                continue
                
            hub_info = self.regional_hubs[hub_name]
            
            # Sort packages by supplier and create consolidation groups
            for supplier, supplier_packages in hub_packages.groupby('supplier_name'):
                
                # Create consolidation batches
                package_list = supplier_packages.to_dict('records')
                batches = self.create_consolidation_batches(package_list, hub_info)
                
                for batch_id, batch in enumerate(batches):
                    consolidated_shipment = self.calculate_consolidated_shipment(
                        batch, hub_name, hub_info, supplier, batch_id
                    )
                    consolidated_shipments.append(consolidated_shipment)
        
        return consolidated_shipments
    
    def create_consolidation_batches(self, packages, hub_info):
        """Create optimal batches for consolidation"""
        
        batches = []
        current_batch = []
        current_value = 0
        max_capacity = hub_info['consolidation_capacity']
        
        for package in packages:
            package_value = package['total_amount']
            
            # Check if adding this package exceeds capacity or time window
            if (current_value + package_value <= max_capacity and 
                len(current_batch) < 10):  # Max 10 packages per batch
                
                current_batch.append(package)
                current_value += package_value
            else:
                # Start new batch
                if current_batch:
                    batches.append(current_batch)
                current_batch = [package]
                current_value = package_value
        
        # Add final batch
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def calculate_consolidated_shipment(self, batch, hub_name, hub_info, supplier, batch_id):
        """Calculate costs and delivery time for consolidated shipment"""
        
        # Calculate original costs
        original_shipping_cost = sum(pkg['shipping_cost'] for pkg in batch)
        original_lead_time = max(pkg['lead_time_days'] for pkg in batch)
        total_value = sum(pkg['total_amount'] for pkg in batch)
        package_count = len(batch)
        
        # Calculate hub and spoke costs
        # Leg 1: Supplier to Hub
        supplier_to_hub_cost = original_shipping_cost * 0.6  # 60% of original (shorter distance)
        supplier_to_hub_time = max(2, original_lead_time - 2)  # 2 days less
        
        # Hub processing
        hub_processing_cost = package_count * self.consolidation_rules['hub_processing_cost']
        hub_processing_time = hub_info['processing_time']
        
        # Leg 2: Hub to Cal Poly SLO (consolidated)
        hub_to_destination_cost = self.calculate_hub_to_slo_cost(total_value, hub_name)
        hub_to_destination_time = self.calculate_hub_to_slo_time(hub_name)
        
        # Total consolidated costs
        total_consolidated_cost = (supplier_to_hub_cost + 
                                 hub_processing_cost + 
                                 hub_to_destination_cost)
        
        total_consolidated_time = (supplier_to_hub_time + 
                                 hub_processing_time + 
                                 hub_to_destination_time)
        
        # Calculate savings
        cost_savings = original_shipping_cost - total_consolidated_cost
        admin_savings = (package_count - 1) * self.consolidation_rules['admin_cost_reduction']
        total_savings = cost_savings + admin_savings
        
        # Time efficiency (negative means faster)
        time_efficiency = original_lead_time - total_consolidated_time
        
        return {
            'consolidation_id': f"{hub_name.replace(' ', '_')}_{supplier.replace(' ', '_')}_{batch_id}",
            'hub_name': hub_name,
            'supplier': supplier,
            'package_count': package_count,
            'total_value': round(total_value, 2),
            'original_shipping_cost': round(original_shipping_cost, 2),
            'consolidated_shipping_cost': round(total_consolidated_cost, 2),
            'cost_savings': round(cost_savings, 2),
            'admin_savings': round(admin_savings, 2),
            'total_savings': round(total_savings, 2),
            'original_lead_time': original_lead_time,
            'consolidated_lead_time': total_consolidated_time,
            'time_efficiency': time_efficiency,
            'supplier_to_hub_cost': round(supplier_to_hub_cost, 2),
            'hub_processing_cost': round(hub_processing_cost, 2),
            'hub_to_slo_cost': round(hub_to_destination_cost, 2),
            'delivery_schedule': self.create_delivery_schedule(total_consolidated_time),
            'packages': [{'value': pkg['total_amount'], 'original_shipping': pkg['shipping_cost']} for pkg in batch]
        }
    
    def calculate_hub_to_slo_cost(self, total_value, hub_name):
        """Calculate shipping cost from hub to Cal Poly SLO"""
        
        # Base rates from each hub to SLO (simulated)
        base_rates = {
            'Los Angeles Hub': 45.00,
            'San Francisco Hub': 35.00,
            'Sacramento Hub': 25.00
        }
        
        base_cost = base_rates.get(hub_name, 40.00)
        
        # Volume discounts for consolidated shipments
        if total_value >= 5000:
            discount = 0.25  # 25% discount
        elif total_value >= 2000:
            discount = 0.15  # 15% discount
        elif total_value >= 1000:
            discount = 0.10  # 10% discount
        else:
            discount = 0.05  # 5% discount
        
        return base_cost * (1 - discount)
    
    def calculate_hub_to_slo_time(self, hub_name):
        """Calculate delivery time from hub to Cal Poly SLO"""
        
        # Transit times from each hub to SLO
        transit_times = {
            'Los Angeles Hub': 2,  # 2 days
            'San Francisco Hub': 1,  # 1 day
            'Sacramento Hub': 1   # 1 day
        }
        
        return transit_times.get(hub_name, 2)
    
    def create_delivery_schedule(self, total_lead_time):
        """Create detailed delivery schedule"""
        
        start_date = datetime.now()
        delivery_date = start_date + timedelta(days=total_lead_time)
        
        return {
            'order_date': start_date.strftime('%Y-%m-%d'),
            'estimated_delivery': delivery_date.strftime('%Y-%m-%d'),
            'total_transit_days': total_lead_time,
            'business_days': max(1, total_lead_time - 2)  # Exclude weekends
        }
    
    def generate_consolidation_report(self):
        """Generate comprehensive consolidation analysis report"""
        
        # Assign packages to hubs
        self.assign_packages_to_hubs()
        
        # Create consolidated shipments
        consolidated_shipments = self.create_consolidated_shipments()
        
        # Calculate overall impact
        total_original_cost = sum(ship['original_shipping_cost'] for ship in consolidated_shipments)
        total_consolidated_cost = sum(ship['consolidated_shipping_cost'] for ship in consolidated_shipments)
        total_savings = sum(ship['total_savings'] for ship in consolidated_shipments)
        total_packages = sum(ship['package_count'] for ship in consolidated_shipments)
        
        # Calculate efficiency metrics
        avg_time_improvement = np.mean([ship['time_efficiency'] for ship in consolidated_shipments])
        consolidation_ratio = len(consolidated_shipments) / total_packages if total_packages > 0 else 0
        
        report = {
            'consolidation_summary': {
                'total_packages_consolidated': total_packages,
                'total_consolidated_shipments': len(consolidated_shipments),
                'consolidation_ratio': round(consolidation_ratio, 3),
                'total_original_shipping_cost': round(total_original_cost, 2),
                'total_consolidated_shipping_cost': round(total_consolidated_cost, 2),
                'total_cost_savings': round(total_savings, 2),
                'savings_percentage': round((total_savings / total_original_cost * 100) if total_original_cost > 0 else 0, 1),
                'average_time_improvement_days': round(avg_time_improvement, 1)
            },
            'hub_performance': self.analyze_hub_performance(consolidated_shipments),
            'consolidated_shipments': consolidated_shipments,
            'implementation_plan': self.create_implementation_plan(),
            'roi_analysis': self.calculate_roi_analysis(total_savings, total_packages)
        }
        
        return report
    
    def analyze_hub_performance(self, shipments):
        """Analyze performance by hub"""
        
        hub_performance = {}
        
        for hub_name in self.regional_hubs.keys():
            hub_shipments = [s for s in shipments if s['hub_name'] == hub_name]
            
            if hub_shipments:
                hub_performance[hub_name] = {
                    'shipment_count': len(hub_shipments),
                    'total_packages': sum(s['package_count'] for s in hub_shipments),
                    'total_value': sum(s['total_value'] for s in hub_shipments),
                    'total_savings': sum(s['total_savings'] for s in hub_shipments),
                    'avg_time_improvement': np.mean([s['time_efficiency'] for s in hub_shipments]),
                    'utilization_rate': min(100, sum(s['total_value'] for s in hub_shipments) / self.regional_hubs[hub_name]['consolidation_capacity'] * 100)
                }
        
        return hub_performance
    
    def create_implementation_plan(self):
        """Create step-by-step implementation plan"""
        
        return {
            'phase_1_setup': [
                'Establish partnerships with regional hub facilities',
                'Set up consolidation processing capabilities',
                'Implement tracking and inventory management systems',
                'Train staff on hub and spoke procedures'
            ],
            'phase_2_pilot': [
                'Launch pilot program with A-TOWN AV INC (45 packages)',
                'Test consolidation processes and measure savings',
                'Optimize routing and timing procedures',
                'Gather performance data and feedback'
            ],
            'phase_3_expansion': [
                'Expand to all suppliers and product categories',
                'Implement automated consolidation scheduling',
                'Negotiate volume discounts with carriers',
                'Deploy real-time tracking and reporting'
            ],
            'timeline': '6 months total implementation',
            'estimated_setup_cost': 25000,
            'break_even_period': '8 months'
        }
    
    def calculate_roi_analysis(self, annual_savings, package_count):
        """Calculate return on investment analysis"""
        
        setup_cost = 25000
        monthly_operational_cost = 2000
        annual_operational_cost = monthly_operational_cost * 12
        
        return {
            'annual_cost_savings': round(annual_savings * 12, 2),  # Annualized
            'setup_investment': setup_cost,
            'annual_operational_cost': annual_operational_cost,
            'net_annual_savings': round((annual_savings * 12) - annual_operational_cost, 2),
            'roi_percentage': round(((annual_savings * 12 - annual_operational_cost) / setup_cost * 100), 1),
            'payback_period_months': round(setup_cost / (annual_savings - monthly_operational_cost), 1),
            'packages_processed_annually': package_count * 12
        }

def main():
    """Execute hub and spoke consolidation analysis"""
    
    print("🚚 HUB AND SPOKE CONSOLIDATION MODEL")
    print("=" * 50)
    
    # Initialize consolidation system
    consolidator = HubSpokeConsolidation('master_shipping_dataset_20250807_002133.csv')
    
    # Generate comprehensive report
    report = consolidator.generate_consolidation_report()
    
    # Save detailed report
    with open('hub_spoke_consolidation_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Display key results
    summary = report['consolidation_summary']
    print(f"📦 Packages Consolidated: {summary['total_packages_consolidated']}")
    print(f"🚛 Consolidated Shipments: {summary['total_consolidated_shipments']}")
    print(f"💰 Total Savings: ${summary['total_cost_savings']:,.2f}")
    print(f"📊 Savings Percentage: {summary['savings_percentage']}%")
    print(f"⏰ Avg Time Improvement: {summary['average_time_improvement_days']} days")
    
    print(f"\n🎯 ROI ANALYSIS:")
    roi = report['roi_analysis']
    print(f"💵 Annual Savings: ${roi['annual_cost_savings']:,.2f}")
    print(f"📈 ROI: {roi['roi_percentage']}%")
    print(f"⏱️  Payback Period: {roi['payback_period_months']} months")
    
    # Create summary CSV for easy analysis
    shipments_df = pd.DataFrame(report['consolidated_shipments'])
    shipments_df.to_csv('consolidated_shipments_summary.csv', index=False)
    
    print(f"\n✅ Hub and Spoke consolidation analysis complete!")
    print(f"📄 Detailed report saved: hub_spoke_consolidation_report.json")
    print(f"📊 Shipments summary: consolidated_shipments_summary.csv")
    
    return report

if __name__ == "__main__":
    main()