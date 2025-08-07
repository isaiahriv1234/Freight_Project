#!/usr/bin/env python3
"""
Automated Consolidation Strategy Implementation
Executes real consolidation actions based on opportunity analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class ConsolidationStrategy:
    def __init__(self, data_file):
        self.df = pd.read_csv(data_file)
        self.consolidation_rules = self.define_consolidation_rules()
        
    def define_consolidation_rules(self):
        """Define automated consolidation rules"""
        return {
            'supplier_consolidation': {
                'min_orders': 3,
                'max_avg_order': 1000,
                'time_window_days': 30
            },
            'carrier_consolidation': {
                'min_volume_threshold': 5000,
                'cost_savings_threshold': 0.15
            },
            'geographic_consolidation': {
                'same_location_window': 7,  # days
                'min_shipment_value': 100
            },
            'time_consolidation': {
                'batch_window_hours': 48,
                'min_batch_size': 2
            }
        }
    
    def execute_supplier_consolidation(self):
        """Execute supplier-level consolidation strategy"""
        
        consolidation_actions = []
        
        # Group by supplier and analyze patterns
        supplier_analysis = self.df.groupby('supplier_name').agg({
            'total_amount': ['count', 'sum', 'mean'],
            'shipping_cost': 'sum',
            'lead_time_days': 'mean'
        })
        
        supplier_analysis.columns = ['order_count', 'total_spend', 'avg_order', 'shipping_cost', 'avg_lead_time']
        
        # Apply consolidation rules
        rules = self.consolidation_rules['supplier_consolidation']
        candidates = supplier_analysis[
            (supplier_analysis['order_count'] >= rules['min_orders']) &
            (supplier_analysis['avg_order'] < rules['max_avg_order'])
        ]
        
        for supplier, data in candidates.iterrows():
            # Calculate consolidation impact
            current_orders = int(data['order_count'])
            consolidated_orders = max(1, current_orders // 3)  # Consolidate to 1/3 of orders
            
            shipping_savings = data['shipping_cost'] * 0.25  # 25% shipping savings
            admin_savings = (current_orders - consolidated_orders) * 50  # $50 per order admin cost
            
            action = {
                'supplier': supplier,
                'strategy': 'supplier_consolidation',
                'current_orders': current_orders,
                'target_orders': consolidated_orders,
                'estimated_shipping_savings': round(shipping_savings, 2),
                'estimated_admin_savings': round(admin_savings, 2),
                'total_savings': round(shipping_savings + admin_savings, 2),
                'implementation_steps': self.generate_supplier_consolidation_steps(supplier, data)
            }
            
            consolidation_actions.append(action)
        
        return consolidation_actions
    
    def execute_carrier_consolidation(self):
        """Execute carrier-level consolidation strategy"""
        
        consolidation_actions = []
        
        # Analyze carrier usage by supplier
        carrier_analysis = self.df.groupby(['supplier_name', 'carrier']).agg({
            'total_amount': 'sum',
            'shipping_cost': ['sum', 'mean'],
            'lead_time_days': 'mean'
        }).reset_index()
        
        carrier_analysis.columns = ['supplier', 'carrier', 'volume', 'total_shipping', 'avg_shipping', 'avg_lead_time']
        
        # Find suppliers using multiple carriers
        multi_carrier = carrier_analysis.groupby('supplier').size()
        consolidation_candidates = multi_carrier[multi_carrier > 1].index
        
        for supplier in consolidation_candidates:
            supplier_carriers = carrier_analysis[carrier_analysis['supplier'] == supplier]
            
            # Find best performing carrier
            best_carrier = supplier_carriers.loc[
                supplier_carriers['avg_shipping'].idxmin()
            ]
            
            # Calculate consolidation savings
            total_current_shipping = supplier_carriers['total_shipping'].sum()
            projected_shipping = total_current_shipping * (best_carrier['avg_shipping'] / supplier_carriers['avg_shipping'].mean())
            savings = total_current_shipping - projected_shipping
            
            if savings > 0:
                action = {
                    'supplier': supplier,
                    'strategy': 'carrier_consolidation',
                    'recommended_carrier': best_carrier['carrier'],
                    'current_carriers': supplier_carriers['carrier'].tolist(),
                    'estimated_savings': round(savings, 2),
                    'implementation_steps': self.generate_carrier_consolidation_steps(supplier, best_carrier)
                }
                
                consolidation_actions.append(action)
        
        return consolidation_actions
    
    def execute_time_based_consolidation(self):
        """Execute time-based consolidation strategy"""
        
        if 'PO_Date' not in self.df.columns:
            return [{'message': 'Date data required for time-based consolidation'}]
        
        consolidation_actions = []
        
        # Convert dates and sort
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        df_sorted = self.df.sort_values(['supplier_name', 'PO_Date'])
        
        # Group by supplier and find close-proximity orders
        for supplier in df_sorted['supplier_name'].unique():
            supplier_orders = df_sorted[df_sorted['supplier_name'] == supplier].copy()
            
            if len(supplier_orders) < 2:
                continue
            
            # Find orders within consolidation window
            consolidation_groups = []
            current_group = [supplier_orders.iloc[0]]
            
            for i in range(1, len(supplier_orders)):
                current_order = supplier_orders.iloc[i]
                last_order = current_group[-1]
                
                time_diff = (current_order['PO_Date'] - last_order['PO_Date']).days
                
                if time_diff <= self.consolidation_rules['time_consolidation']['batch_window_hours'] / 24:
                    current_group.append(current_order)
                else:
                    if len(current_group) >= self.consolidation_rules['time_consolidation']['min_batch_size']:
                        consolidation_groups.append(current_group)
                    current_group = [current_order]
            
            # Add final group if it meets criteria
            if len(current_group) >= self.consolidation_rules['time_consolidation']['min_batch_size']:
                consolidation_groups.append(current_group)
            
            # Generate consolidation actions for each group
            for group in consolidation_groups:
                if len(group) > 1:
                    total_value = sum(order['total_amount'] for order in group)
                    total_shipping = sum(order['shipping_cost'] for order in group)
                    estimated_savings = total_shipping * 0.30  # 30% savings from consolidation
                    
                    action = {
                        'supplier': supplier,
                        'strategy': 'time_based_consolidation',
                        'orders_to_consolidate': len(group),
                        'total_value': round(total_value, 2),
                        'current_shipping': round(total_shipping, 2),
                        'estimated_savings': round(estimated_savings, 2),
                        'implementation_steps': self.generate_time_consolidation_steps(supplier, group)
                    }
                    
                    consolidation_actions.append(action)
        
        return consolidation_actions
    
    def execute_geographic_consolidation(self):
        """Execute geographic-based consolidation strategy"""
        
        if 'geographic_location' not in self.df.columns:
            return [{'message': 'Geographic data required for location-based consolidation'}]
        
        consolidation_actions = []
        
        # Group by location and find consolidation opportunities
        location_analysis = self.df.groupby('geographic_location').agg({
            'supplier_name': 'nunique',
            'total_amount': 'sum',
            'shipping_cost': 'sum'
        })
        
        # Find locations with multiple suppliers
        multi_supplier_locations = location_analysis[location_analysis['supplier_name'] > 1]
        
        for location, data in multi_supplier_locations.iterrows():
            location_suppliers = self.df[self.df['geographic_location'] == location]
            
            # Calculate potential savings from consolidated shipping
            current_shipping = data['shipping_cost']
            estimated_consolidated_shipping = current_shipping * 0.60  # 40% savings
            savings = current_shipping - estimated_consolidated_shipping
            
            action = {
                'location': location,
                'strategy': 'geographic_consolidation',
                'suppliers_count': int(data['supplier_name']),
                'total_volume': round(data['total_amount'], 2),
                'current_shipping': round(current_shipping, 2),
                'estimated_savings': round(savings, 2),
                'implementation_steps': self.generate_geographic_consolidation_steps(location, location_suppliers)
            }
            
            consolidation_actions.append(action)
        
        return consolidation_actions
    
    def generate_supplier_consolidation_steps(self, supplier, data):
        """Generate specific implementation steps for supplier consolidation"""
        return [
            f"Contact {supplier} to discuss order consolidation program",
            f"Negotiate minimum order quantities to reduce from {int(data['order_count'])} to {max(1, int(data['order_count']) // 3)} orders",
            "Establish regular ordering schedule (weekly/bi-weekly)",
            "Implement inventory buffer to support larger order quantities",
            "Set up automated reorder points",
            "Monitor savings and adjust strategy quarterly"
        ]
    
    def generate_carrier_consolidation_steps(self, supplier, best_carrier):
        """Generate specific implementation steps for carrier consolidation"""
        return [
            f"Negotiate volume discount with {best_carrier['carrier']} for {supplier}",
            f"Transition all shipments to {best_carrier['carrier']}",
            "Update procurement system with preferred carrier",
            "Train staff on new shipping procedures",
            "Monitor performance metrics (cost, delivery time, quality)",
            "Review carrier performance quarterly"
        ]
    
    def generate_time_consolidation_steps(self, supplier, group):
        """Generate specific implementation steps for time-based consolidation"""
        return [
            f"Implement batch ordering system for {supplier}",
            f"Consolidate {len(group)} orders into single shipment",
            "Establish 48-hour order batching window",
            "Update ordering procedures and staff training",
            "Monitor delivery performance and adjust timing",
            "Measure cost savings and efficiency gains"
        ]
    
    def generate_geographic_consolidation_steps(self, location, suppliers):
        """Generate specific implementation steps for geographic consolidation"""
        supplier_list = suppliers['supplier_name'].unique()
        return [
            f"Coordinate shipments to {location} from {len(supplier_list)} suppliers",
            "Establish regional distribution hub or consolidation point",
            "Negotiate group shipping rates for the region",
            "Implement shared logistics coordination",
            "Set up regional inventory management",
            "Monitor regional performance metrics"
        ]
    
    def execute_comprehensive_consolidation(self):
        """Execute all consolidation strategies and prioritize actions"""
        
        all_actions = []
        
        # Execute all consolidation strategies
        supplier_actions = self.execute_supplier_consolidation()
        carrier_actions = self.execute_carrier_consolidation()
        time_actions = self.execute_time_based_consolidation()
        geographic_actions = self.execute_geographic_consolidation()
        
        all_actions.extend(supplier_actions)
        all_actions.extend(carrier_actions)
        all_actions.extend(time_actions)
        all_actions.extend(geographic_actions)
        
        # Prioritize actions by savings potential
        prioritized_actions = sorted(
            [action for action in all_actions if 'estimated_savings' in action],
            key=lambda x: x.get('estimated_savings', 0),
            reverse=True
        )
        
        # Generate implementation plan
        implementation_plan = self.generate_implementation_plan(prioritized_actions)
        
        return {
            'total_actions': len(prioritized_actions),
            'total_estimated_savings': sum(action.get('estimated_savings', 0) for action in prioritized_actions),
            'prioritized_actions': prioritized_actions[:10],  # Top 10 actions
            'implementation_plan': implementation_plan
        }
    
    def generate_implementation_plan(self, actions):
        """Generate phased implementation plan"""
        
        phases = {
            'Phase 1 (0-30 days)': [],
            'Phase 2 (30-60 days)': [],
            'Phase 3 (60-90 days)': []
        }
        
        # Distribute actions across phases based on complexity and savings
        for i, action in enumerate(actions[:15]):  # Top 15 actions
            if i < 5:
                phases['Phase 1 (0-30 days)'].append(action)
            elif i < 10:
                phases['Phase 2 (30-60 days)'].append(action)
            else:
                phases['Phase 3 (60-90 days)'].append(action)
        
        return phases

def main():
    """Execute comprehensive consolidation strategy"""
    
    # Initialize consolidation strategy
    strategy = ConsolidationStrategy('master_shipping_dataset_20250807_002133.csv')
    
    # Execute comprehensive consolidation
    results = strategy.execute_comprehensive_consolidation()
    
    # Save results
    import json
    with open('consolidation_strategy_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("🎯 CONSOLIDATION STRATEGY EXECUTED")
    print(f"📊 Total Actions: {results['total_actions']}")
    print(f"💰 Estimated Savings: ${results['total_estimated_savings']:,.2f}")
    print(f"🚀 Top Priority Actions: {len(results['prioritized_actions'])}")
    
    # Display top 3 actions
    for i, action in enumerate(results['prioritized_actions'][:3], 1):
        print(f"\n{i}. {action['strategy'].replace('_', ' ').title()}")
        print(f"   Target: {action.get('supplier', action.get('location', 'Multiple'))}")
        print(f"   Savings: ${action.get('estimated_savings', 0):,.2f}")
    
    return results

if __name__ == "__main__":
    main()