#!/usr/bin/env python3
"""
Automated Shipping Cost Optimization Engine
Automatically selects optimal carriers and triggers cost-saving actions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from shipping_optimizer import ShippingOptimizer
from consolidation_optimizer import ConsolidationOptimizer
from ups_integration import get_ups_rates_for_order
from fedex_integration import get_fedex_rates_for_order
from dhl_integration import get_dhl_rates_for_order

class AutomatedShippingOptimizer:
    def __init__(self, data_path: str = 'Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv'):
        """Initialize automated shipping optimizer"""
        self.df = pd.read_csv(data_path)
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        self.shipping_optimizer = ShippingOptimizer(data_path)
        self.consolidation_optimizer = ConsolidationOptimizer(data_path)
        
        # Automation rules
        self.cost_threshold = 50.0  # Minimum savings to trigger automation
        self.consolidation_window = 7  # Days to look for consolidation
        
    def auto_select_carrier(self, order_details: Dict) -> Dict:
        """Automatically select optimal carrier for an order"""
        order_value = order_details.get('order_value', 1000)
        weight = order_details.get('weight', 5.0)
        urgency = order_details.get('urgency', 'standard')
        dest_city = order_details.get('dest_city', 'Los Angeles')
        dest_state = order_details.get('dest_state', 'CA')
        dest_zip = order_details.get('dest_zip', '90210')
        
        # Get historical recommendations
        historical_recs = self.shipping_optimizer.get_carrier_recommendations(
            order_value, 'medium', urgency
        )
        
        # Get real-time rates (if APIs are configured)
        real_time_rates = self._get_real_time_rates(order_value, weight, dest_city, dest_state, dest_zip)
        
        # Combine and analyze options
        best_option = self._analyze_shipping_options(historical_recs, real_time_rates, order_details)
        
        return {
            'recommended_carrier': best_option['carrier'],
            'estimated_cost': best_option['cost'],
            'estimated_days': best_option.get('transit_days', 'N/A'),
            'cost_savings': best_option.get('savings', 0),
            'automation_confidence': best_option.get('confidence', 0),
            'reasoning': best_option.get('reasoning', ''),
            'alternative_options': real_time_rates[:3] if real_time_rates else historical_recs[:3]
        }
    
    def _get_real_time_rates(self, order_value: float, weight: float, 
                           dest_city: str, dest_state: str, dest_zip: str) -> List[Dict]:
        """Get real-time rates from all configured APIs"""
        all_rates = []
        
        # Try UPS
        try:
            ups_rates = get_ups_rates_for_order(order_value, weight, dest_city, dest_state, dest_zip)
            all_rates.extend(ups_rates)
        except:
            pass
        
        # Try FedEx
        try:
            fedex_rates = get_fedex_rates_for_order(order_value, weight, dest_city, dest_state, dest_zip)
            all_rates.extend(fedex_rates)
        except:
            pass
        
        # Try DHL
        try:
            dhl_rates = get_dhl_rates_for_order(order_value, weight, dest_city, dest_state, dest_zip)
            all_rates.extend(dhl_rates)
        except:
            pass
        
        return sorted(all_rates, key=lambda x: x['cost'])
    
    def _analyze_shipping_options(self, historical: List[Dict], real_time: List[Dict], 
                                order_details: Dict) -> Dict:
        """Analyze and select best shipping option"""
        urgency = order_details.get('urgency', 'standard')
        
        # If real-time rates available, use them
        if real_time:
            best_rate = real_time[0]  # Already sorted by cost
            
            # Calculate savings vs historical average
            historical_avg = np.mean([r['predicted_cost'] for r in historical]) if historical else best_rate['cost']
            savings = max(0, historical_avg - best_rate['cost'])
            
            return {
                'carrier': best_rate['carrier'],
                'cost': best_rate['cost'],
                'transit_days': best_rate.get('transit_days', 'N/A'),
                'savings': savings,
                'confidence': 95,  # High confidence with real-time data
                'reasoning': f"Real-time rate from {best_rate['carrier']} - lowest cost option"
            }
        
        # Fall back to historical recommendations
        elif historical:
            best_historical = historical[0]
            return {
                'carrier': best_historical['carrier'],
                'cost': best_historical['predicted_cost'],
                'transit_days': best_historical.get('avg_lead_time', 'N/A'),
                'savings': 0,
                'confidence': 75,  # Lower confidence with historical data
                'reasoning': f"Historical analysis recommends {best_historical['carrier']}"
            }
        
        return {
            'carrier': 'Ground',
            'cost': 25.0,
            'transit_days': 5,
            'savings': 0,
            'confidence': 50,
            'reasoning': 'Default ground shipping - no data available'
        }
    
    def generate_automation_alerts(self) -> List[Dict]:
        """Generate automated alerts for cost-saving opportunities"""
        alerts = []
        
        # Consolidation alerts
        consolidation_opps = self.consolidation_optimizer.find_consolidation_opportunities()
        for opp in consolidation_opps[:5]:  # Top 5 opportunities
            if opp['potential_savings'] > self.cost_threshold:
                alerts.append({
                    'type': 'consolidation',
                    'priority': 'high' if opp['potential_savings'] > 500 else 'medium',
                    'title': f"Consolidation Opportunity: {opp['supplier']}",
                    'description': f"Combine {opp['order_count']} orders to save ${opp['potential_savings']:.2f}",
                    'potential_savings': opp['potential_savings'],
                    'action_required': f"Schedule consolidated order for {opp['supplier']}",
                    'deadline': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
                })
        
        # Carrier optimization alerts
        carrier_savings = self.shipping_optimizer.get_cost_savings_analysis()
        if carrier_savings['potential_savings'] > self.cost_threshold:
            alerts.append({
                'type': 'carrier_optimization',
                'priority': 'medium',
                'title': 'Carrier Optimization Opportunity',
                'description': f"Switch carriers to save ${carrier_savings['potential_savings']:.2f} ({carrier_savings['savings_percentage']:.1f}%)",
                'potential_savings': carrier_savings['potential_savings'],
                'action_required': 'Review and update preferred carrier selections',
                'deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            })
        
        # Overcharge detection alerts
        overcharge_alerts = self._detect_overcharges()
        alerts.extend(overcharge_alerts)
        
        return sorted(alerts, key=lambda x: x['potential_savings'], reverse=True)
    
    def _detect_overcharges(self) -> List[Dict]:
        """Detect potential overcharges in recent shipments"""
        alerts = []
        
        # Analyze recent orders (last 30 days)
        recent_orders = self.df[self.df['PO_Date'] >= datetime.now() - timedelta(days=30)]
        
        for _, order in recent_orders.iterrows():
            if pd.isna(order['Shipping_Cost']) or order['Shipping_Cost'] <= 0:
                continue
                
            # Get current market rate estimate
            historical_recs = self.shipping_optimizer.get_carrier_recommendations(
                order['Total_Amount'], 'medium', 'standard'
            )
            
            if historical_recs:
                market_rate = historical_recs[0]['predicted_cost']
                actual_cost = order['Shipping_Cost']
                
                if actual_cost > market_rate * 1.5:  # 50% over market rate
                    overcharge = actual_cost - market_rate
                    alerts.append({
                        'type': 'overcharge_detection',
                        'priority': 'high',
                        'title': f"Potential Overcharge Detected",
                        'description': f"PO {order['PO_ID']} paid ${actual_cost:.2f} vs market rate ${market_rate:.2f}",
                        'potential_savings': overcharge,
                        'action_required': f"Review billing for PO {order['PO_ID']} with {order['Carrier']}",
                        'deadline': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                    })
        
        return alerts
    
    def create_shipping_rules(self) -> Dict:
        """Create automated shipping rules based on data patterns"""
        rules = {
            'carrier_preferences': {},
            'consolidation_rules': {},
            'cost_thresholds': {},
            'automation_triggers': []
        }
        
        # Analyze carrier performance by order value ranges
        value_ranges = [(0, 500), (500, 2000), (2000, 10000), (10000, float('inf'))]
        
        for min_val, max_val in value_ranges:
            range_data = self.df[
                (self.df['Total_Amount'] >= min_val) & 
                (self.df['Total_Amount'] < max_val)
            ]
            
            if not range_data.empty:
                # Find best performing carrier for this range
                carrier_performance = range_data.groupby('Carrier').agg({
                    'Shipping_Cost': 'mean',
                    'Lead_Time_Days': 'mean',
                    'Total_Amount': 'count'
                }).round(2)
                
                if not carrier_performance.empty:
                    best_carrier = carrier_performance['Shipping_Cost'].idxmin()
                    range_key = f"${min_val}-${max_val if max_val != float('inf') else '10000+'}"
                    
                    rules['carrier_preferences'][range_key] = {
                        'preferred_carrier': best_carrier,
                        'avg_cost': carrier_performance.loc[best_carrier, 'Shipping_Cost'],
                        'avg_lead_time': carrier_performance.loc[best_carrier, 'Lead_Time_Days']
                    }
        
        # Consolidation rules
        rules['consolidation_rules'] = {
            'time_window_days': self.consolidation_window,
            'minimum_savings': self.cost_threshold,
            'auto_consolidate_threshold': 200.0  # Auto-consolidate if savings > $200
        }
        
        # Cost thresholds
        rules['cost_thresholds'] = {
            'overcharge_alert_percentage': 50,  # Alert if 50% over market rate
            'minimum_savings_alert': self.cost_threshold,
            'high_priority_savings': 500.0
        }
        
        # Automation triggers
        rules['automation_triggers'] = [
            {
                'condition': 'consolidation_savings > 200',
                'action': 'auto_schedule_consolidated_order',
                'approval_required': False
            },
            {
                'condition': 'overcharge_detected > 100',
                'action': 'send_billing_dispute_alert',
                'approval_required': True
            },
            {
                'condition': 'carrier_savings > 25%',
                'action': 'suggest_carrier_switch',
                'approval_required': True
            }
        ]
        
        return rules
    
    def get_automation_dashboard_data(self) -> Dict:
        """Get data for automation dashboard"""
        alerts = self.generate_automation_alerts()
        rules = self.create_shipping_rules()
        
        # Calculate automation metrics
        total_potential_savings = sum(alert['potential_savings'] for alert in alerts)
        high_priority_alerts = len([a for a in alerts if a['priority'] == 'high'])
        
        return {
            'summary': {
                'total_alerts': len(alerts),
                'high_priority_alerts': high_priority_alerts,
                'total_potential_savings': total_potential_savings,
                'automation_rules_active': len(rules['automation_triggers'])
            },
            'alerts': alerts,
            'shipping_rules': rules,
            'recent_automations': self._get_recent_automations()
        }
    
    def _get_recent_automations(self) -> List[Dict]:
        """Get recent automated actions (simulated for demo)"""
        return [
            {
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'action': 'Auto-selected Ground shipping for order #12345',
                'savings': 25.50,
                'status': 'completed'
            },
            {
                'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'action': 'Consolidated 3 orders for DEEP BLUE INTEGRATION',
                'savings': 150.00,
                'status': 'completed'
            }
        ]

def main():
    """Demo automated shipping optimizer"""
    print("🤖 Automated Shipping Optimizer Demo")
    print("=" * 45)
    
    optimizer = AutomatedShippingOptimizer()
    
    # Test auto carrier selection
    test_order = {
        'order_value': 2500,
        'weight': 10.0,
        'urgency': 'standard',
        'dest_city': 'Los Angeles',
        'dest_state': 'CA',
        'dest_zip': '90210'
    }
    
    print("\n🚚 Auto Carrier Selection:")
    selection = optimizer.auto_select_carrier(test_order)
    print(f"Recommended: {selection['recommended_carrier']}")
    print(f"Cost: ${selection['estimated_cost']:.2f}")
    print(f"Reasoning: {selection['reasoning']}")
    
    # Generate automation alerts
    print(f"\n🚨 Automation Alerts:")
    alerts = optimizer.generate_automation_alerts()
    for alert in alerts[:3]:
        print(f"• {alert['title']}: ${alert['potential_savings']:.2f} savings")
    
    # Show automation rules
    print(f"\n📋 Shipping Rules Created:")
    rules = optimizer.create_shipping_rules()
    print(f"Carrier preferences: {len(rules['carrier_preferences'])} rules")
    print(f"Automation triggers: {len(rules['automation_triggers'])} triggers")

if __name__ == "__main__":
    main()