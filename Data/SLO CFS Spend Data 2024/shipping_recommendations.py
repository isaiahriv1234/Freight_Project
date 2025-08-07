#!/usr/bin/env python3
"""
Intelligent Shipping Recommendations System
Provides real-time shipping optimization recommendations based on cost, time, and efficiency
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

class ShippingRecommendationEngine:
    def __init__(self, data_file, live_rates_file=None):
        self.df = pd.read_csv(data_file)
        
        # Load live rates if available
        try:
            self.live_rates = pd.read_csv('easypost_shipping_rates_20250807_002133.csv')
        except:
            self.live_rates = None
        
        # Define carrier performance profiles
        self.carrier_profiles = {
            'USPS': {'cost_factor': 0.7, 'speed_factor': 0.8, 'reliability': 0.85},
            'UPS': {'cost_factor': 1.2, 'speed_factor': 0.9, 'reliability': 0.95},
            'FedEx': {'cost_factor': 1.3, 'speed_factor': 0.85, 'reliability': 0.95},
            'Ground': {'cost_factor': 0.6, 'speed_factor': 0.7, 'reliability': 0.8},
            'Freight': {'cost_factor': 0.9, 'speed_factor': 0.6, 'reliability': 0.9},
            'Electronic': {'cost_factor': 0.1, 'speed_factor': 1.0, 'reliability': 0.99}
        }
        
        # Recommendation thresholds
        self.thresholds = {
            'cost_savings_min': 5.00,      # Minimum $5 savings to recommend
            'time_improvement_min': 1,      # Minimum 1 day improvement
            'consolidation_min_orders': 2,  # Minimum orders for consolidation
            'volume_discount_threshold': 1000  # Minimum value for volume discounts
        }
    
    def generate_carrier_recommendations(self):
        """Generate carrier optimization recommendations for each order"""
        
        recommendations = []
        
        for _, order in self.df.iterrows():
            if order['shipping_cost'] == 0:
                continue
                
            current_carrier = order['carrier']
            current_cost = order['shipping_cost']
            current_time = order['lead_time_days']
            order_value = order['total_amount']
            
            # Get alternative carrier options
            alternatives = self.get_carrier_alternatives(order_value, current_cost, current_time)
            
            # Find best alternatives
            best_cost_option = min(alternatives, key=lambda x: x['estimated_cost'])
            best_time_option = min(alternatives, key=lambda x: x['estimated_time'])
            
            # Generate recommendations
            order_recommendations = []
            
            # Cost optimization recommendation
            if best_cost_option['estimated_cost'] < current_cost - self.thresholds['cost_savings_min']:
                cost_savings = current_cost - best_cost_option['estimated_cost']
                order_recommendations.append({
                    'type': 'cost_optimization',
                    'priority': 'High' if cost_savings > 20 else 'Medium',
                    'current_carrier': current_carrier,
                    'recommended_carrier': best_cost_option['carrier'],
                    'current_cost': current_cost,
                    'recommended_cost': best_cost_option['estimated_cost'],
                    'savings': round(cost_savings, 2),
                    'savings_percentage': round((cost_savings / current_cost) * 100, 1),
                    'time_impact': best_cost_option['estimated_time'] - current_time,
                    'reason': f"Switch to {best_cost_option['carrier']} to save ${cost_savings:.2f}"
                })
            
            # Time optimization recommendation
            if best_time_option['estimated_time'] < current_time - self.thresholds['time_improvement_min']:
                time_savings = current_time - best_time_option['estimated_time']
                cost_impact = best_time_option['estimated_cost'] - current_cost
                order_recommendations.append({
                    'type': 'time_optimization',
                    'priority': 'High' if time_savings > 3 else 'Medium',
                    'current_carrier': current_carrier,
                    'recommended_carrier': best_time_option['carrier'],
                    'current_time': current_time,
                    'recommended_time': best_time_option['estimated_time'],
                    'time_savings': time_savings,
                    'cost_impact': round(cost_impact, 2),
                    'reason': f"Switch to {best_time_option['carrier']} to save {time_savings} days"
                })
            
            if order_recommendations:
                recommendations.append({
                    'supplier': order['supplier_name'],
                    'order_value': order_value,
                    'current_shipping': current_cost,
                    'recommendations': order_recommendations
                })
        
        return recommendations
    
    def get_carrier_alternatives(self, order_value, current_cost, current_time):
        """Get alternative carrier options with estimated costs and times"""
        
        alternatives = []
        
        # Use live rates if available
        if self.live_rates is not None:
            for _, rate in self.live_rates.iterrows():
                alternatives.append({
                    'carrier': rate['carrier'],
                    'service': rate['service'],
                    'estimated_cost': rate['rate'],
                    'estimated_time': rate['delivery_days'] if rate['delivery_days'] else 3
                })
        
        # Add estimated alternatives based on carrier profiles
        for carrier, profile in self.carrier_profiles.items():
            base_cost = current_cost * profile['cost_factor']
            base_time = max(1, int(current_time * profile['speed_factor']))
            
            # Apply volume discounts
            if order_value > self.thresholds['volume_discount_threshold']:
                base_cost *= 0.9  # 10% volume discount
            
            alternatives.append({
                'carrier': carrier,
                'service': 'Standard',
                'estimated_cost': round(base_cost, 2),
                'estimated_time': base_time,
                'reliability': profile['reliability']
            })
        
        return alternatives
    
    def generate_consolidation_recommendations(self):
        """Generate consolidation recommendations by supplier"""
        
        consolidation_recs = []
        
        # Group by supplier
        for supplier, supplier_orders in self.df.groupby('supplier_name'):
            if len(supplier_orders) < self.thresholds['consolidation_min_orders']:
                continue
            
            # Analyze consolidation potential
            total_orders = len(supplier_orders)
            total_shipping = supplier_orders['shipping_cost'].sum()
            total_value = supplier_orders['total_amount'].sum()
            avg_order_size = total_value / total_orders
            
            # Calculate consolidation scenarios
            scenarios = self.calculate_consolidation_scenarios(supplier_orders)
            
            best_scenario = max(scenarios, key=lambda x: x['total_savings'])
            
            if best_scenario['total_savings'] > 50:  # Minimum $50 savings
                consolidation_recs.append({
                    'supplier': supplier,
                    'current_orders': total_orders,
                    'current_shipping_cost': round(total_shipping, 2),
                    'recommended_scenario': best_scenario,
                    'priority': 'High' if best_scenario['total_savings'] > 200 else 'Medium',
                    'implementation_steps': self.generate_consolidation_steps(supplier, best_scenario)
                })
        
        return consolidation_recs
    
    def calculate_consolidation_scenarios(self, orders):
        """Calculate different consolidation scenarios"""
        
        current_orders = len(orders)
        current_shipping = orders['shipping_cost'].sum()
        
        scenarios = []
        
        # Scenario 1: Weekly consolidation
        weekly_orders = max(1, current_orders // 4)
        weekly_shipping = current_shipping * 0.7  # 30% savings
        weekly_savings = current_shipping - weekly_shipping
        
        scenarios.append({
            'name': 'Weekly Consolidation',
            'target_orders': weekly_orders,
            'estimated_shipping': round(weekly_shipping, 2),
            'total_savings': round(weekly_savings, 2),
            'frequency': 'Weekly',
            'implementation_difficulty': 'Medium'
        })
        
        # Scenario 2: Bi-weekly consolidation
        biweekly_orders = max(1, current_orders // 2)
        biweekly_shipping = current_shipping * 0.6  # 40% savings
        biweekly_savings = current_shipping - biweekly_shipping
        
        scenarios.append({
            'name': 'Bi-weekly Consolidation',
            'target_orders': biweekly_orders,
            'estimated_shipping': round(biweekly_shipping, 2),
            'total_savings': round(biweekly_savings, 2),
            'frequency': 'Bi-weekly',
            'implementation_difficulty': 'Low'
        })
        
        # Scenario 3: Monthly consolidation
        monthly_orders = max(1, current_orders // 8)
        monthly_shipping = current_shipping * 0.5  # 50% savings
        monthly_savings = current_shipping - monthly_shipping
        
        scenarios.append({
            'name': 'Monthly Consolidation',
            'target_orders': monthly_orders,
            'estimated_shipping': round(monthly_shipping, 2),
            'total_savings': round(monthly_savings, 2),
            'frequency': 'Monthly',
            'implementation_difficulty': 'High'
        })
        
        return scenarios
    
    def generate_consolidation_steps(self, supplier, scenario):
        """Generate implementation steps for consolidation"""
        
        return [
            f"Contact {supplier} to discuss {scenario['frequency'].lower()} ordering schedule",
            f"Negotiate minimum order quantities to reduce to {scenario['target_orders']} orders",
            "Set up inventory buffer to support larger order quantities",
            "Implement automated reorder points and scheduling",
            f"Monitor savings and adjust {scenario['frequency'].lower()} schedule as needed"
        ]
    
    def generate_volume_discount_recommendations(self):
        """Generate volume discount recommendations"""
        
        volume_recs = []
        
        # Analyze spending by supplier
        supplier_spending = self.df.groupby('supplier_name').agg({
            'total_amount': 'sum',
            'shipping_cost': 'sum',
            'supplier_name': 'count'
        }).rename(columns={'supplier_name': 'order_count'})
        
        for supplier, data in supplier_spending.iterrows():
            annual_spend = data['total_amount'] * 12  # Annualize
            annual_shipping = data['shipping_cost'] * 12
            
            # Calculate potential volume discounts
            if annual_spend > 50000:  # High-value suppliers
                potential_discount = 0.15  # 15% discount
                priority = 'High'
            elif annual_spend > 20000:
                potential_discount = 0.10  # 10% discount
                priority = 'Medium'
            elif annual_spend > 10000:
                potential_discount = 0.05  # 5% discount
                priority = 'Low'
            else:
                continue
            
            shipping_savings = annual_shipping * potential_discount
            product_savings = annual_spend * (potential_discount * 0.5)  # Assume 50% of discount applies to products
            total_savings = shipping_savings + product_savings
            
            volume_recs.append({
                'supplier': supplier,
                'annual_spend': round(annual_spend, 2),
                'potential_discount': f"{potential_discount*100}%",
                'estimated_annual_savings': round(total_savings, 2),
                'priority': priority,
                'negotiation_points': [
                    f"Annual spend of ${annual_spend:,.2f} qualifies for volume pricing",
                    f"Request {potential_discount*100}% discount on shipping and products",
                    "Commit to minimum annual volume in exchange for better rates",
                    "Explore multi-year contracts for additional savings"
                ]
            })
        
        return sorted(volume_recs, key=lambda x: x['estimated_annual_savings'], reverse=True)
    
    def generate_comprehensive_recommendations(self):
        """Generate comprehensive shipping recommendations report"""
        
        print("🚀 GENERATING SHIPPING RECOMMENDATIONS...")
        
        # Generate all recommendation types
        carrier_recs = self.generate_carrier_recommendations()
        consolidation_recs = self.generate_consolidation_recommendations()
        volume_recs = self.generate_volume_discount_recommendations()
        
        # Calculate total potential savings
        carrier_savings = sum(
            rec['recommendations'][0].get('savings', 0) 
            for rec in carrier_recs 
            if rec['recommendations']
        )
        
        consolidation_savings = sum(
            rec['recommended_scenario']['total_savings'] 
            for rec in consolidation_recs
        )
        
        volume_savings = sum(rec['estimated_annual_savings'] for rec in volume_recs)
        
        total_potential_savings = carrier_savings + consolidation_savings + (volume_savings / 12)  # Monthly volume savings
        
        # Create comprehensive report
        report = {
            'generation_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_recommendations': len(carrier_recs) + len(consolidation_recs) + len(volume_recs),
                'carrier_recommendations': len(carrier_recs),
                'consolidation_recommendations': len(consolidation_recs),
                'volume_discount_opportunities': len(volume_recs),
                'total_potential_monthly_savings': round(total_potential_savings, 2),
                'total_potential_annual_savings': round(total_potential_savings * 12, 2)
            },
            'carrier_optimization': carrier_recs,
            'consolidation_opportunities': consolidation_recs,
            'volume_discount_opportunities': volume_recs,
            'implementation_priority': self.prioritize_recommendations(carrier_recs, consolidation_recs, volume_recs)
        }
        
        return report
    
    def prioritize_recommendations(self, carrier_recs, consolidation_recs, volume_recs):
        """Prioritize recommendations by impact and ease of implementation"""
        
        all_recommendations = []
        
        # Add carrier recommendations
        for rec in carrier_recs:
            for subrec in rec['recommendations']:
                all_recommendations.append({
                    'type': 'Carrier Optimization',
                    'supplier': rec['supplier'],
                    'savings': subrec.get('savings', 0),
                    'priority': subrec['priority'],
                    'implementation_effort': 'Low',
                    'timeframe': '1-2 weeks',
                    'action': subrec['reason']
                })
        
        # Add consolidation recommendations
        for rec in consolidation_recs:
            all_recommendations.append({
                'type': 'Order Consolidation',
                'supplier': rec['supplier'],
                'savings': rec['recommended_scenario']['total_savings'],
                'priority': rec['priority'],
                'implementation_effort': rec['recommended_scenario']['implementation_difficulty'],
                'timeframe': '4-6 weeks',
                'action': f"Implement {rec['recommended_scenario']['name'].lower()}"
            })
        
        # Add volume discount recommendations
        for rec in volume_recs[:5]:  # Top 5 volume opportunities
            all_recommendations.append({
                'type': 'Volume Discount',
                'supplier': rec['supplier'],
                'savings': rec['estimated_annual_savings'] / 12,  # Monthly savings
                'priority': rec['priority'],
                'implementation_effort': 'High',
                'timeframe': '8-12 weeks',
                'action': f"Negotiate {rec['potential_discount']} volume discount"
            })
        
        # Sort by savings potential and priority
        prioritized = sorted(all_recommendations, 
                           key=lambda x: (x['savings'], x['priority'] == 'High'), 
                           reverse=True)
        
        return prioritized[:10]  # Top 10 recommendations

def main():
    """Execute shipping recommendations system"""
    
    print("📊 INTELLIGENT SHIPPING RECOMMENDATIONS SYSTEM")
    print("=" * 60)
    
    # Initialize recommendation engine
    engine = ShippingRecommendationEngine('master_shipping_dataset_20250807_002133.csv')
    
    # Generate comprehensive recommendations
    report = engine.generate_comprehensive_recommendations()
    
    # Save detailed report
    with open('shipping_recommendations_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Display key results
    summary = report['summary']
    print(f"📈 Total Recommendations: {summary['total_recommendations']}")
    print(f"💰 Monthly Savings Potential: ${summary['total_potential_monthly_savings']:,.2f}")
    print(f"📅 Annual Savings Potential: ${summary['total_potential_annual_savings']:,.2f}")
    
    print(f"\n🎯 TOP 5 PRIORITY RECOMMENDATIONS:")
    for i, rec in enumerate(report['implementation_priority'][:5], 1):
        print(f"{i}. {rec['type']} - {rec['supplier']}")
        print(f"   💵 Savings: ${rec['savings']:,.2f}/month")
        print(f"   ⏱️  Timeline: {rec['timeframe']}")
        print(f"   🎯 Action: {rec['action']}")
        print()
    
    # Create actionable CSV for procurement team
    priority_df = pd.DataFrame(report['implementation_priority'])
    priority_df.to_csv('priority_shipping_recommendations.csv', index=False)
    
    print(f"✅ Shipping recommendations generated successfully!")
    print(f"📄 Detailed report: shipping_recommendations_report.json")
    print(f"📊 Priority actions: priority_shipping_recommendations.csv")
    
    return report

if __name__ == "__main__":
    main()