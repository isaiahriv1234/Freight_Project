#!/usr/bin/env python3
"""
Executive Dashboard for Enhanced Visibility
Real-time consolidation opportunities and diversity metrics visibility
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from shipping_optimizer import ShippingOptimizer
from consolidation_optimizer import ConsolidationOptimizer
from supplier_diversity_tracker import SupplierDiversityTracker
from automated_shipping_optimizer import AutomatedShippingOptimizer

class ExecutiveDashboard:
    def __init__(self, data_path: str = 'Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv'):
        """Initialize executive dashboard with all analytics"""
        self.df = pd.read_csv(data_path)
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        
        # Initialize all analytics engines
        self.shipping_optimizer = ShippingOptimizer(data_path)
        self.consolidation_optimizer = ConsolidationOptimizer(data_path)
        self.diversity_tracker = SupplierDiversityTracker(data_path)
        self.automated_optimizer = AutomatedShippingOptimizer(data_path)
    
    def get_executive_summary(self) -> Dict:
        """Get high-level executive summary metrics"""
        total_spend = self.df['Total_Amount'].sum()
        total_shipping = self.df['Shipping_Cost'].sum()
        
        # Get key metrics from each system
        consolidation_summary = self.consolidation_optimizer.get_consolidation_summary()
        diversity_summary = self.diversity_tracker.get_diversity_performance_summary()
        shipping_savings = self.shipping_optimizer.get_cost_savings_analysis()
        
        return {
            'total_procurement_spend': total_spend,
            'total_shipping_costs': total_shipping,
            'shipping_percentage': (total_shipping / total_spend * 100) if total_spend > 0 else 0,
            'consolidation_opportunities': consolidation_summary['total_opportunities'],
            'consolidation_savings_potential': consolidation_summary['total_potential_savings'],
            'diversity_spend_percentage': diversity_summary['diversity_spend_percentage'],
            'diversity_goal_status': 'Exceeds Target' if diversity_summary['diversity_spend_percentage'] >= 25 else 'Below Target',
            'shipping_optimization_savings': shipping_savings['potential_savings'],
            'total_cost_savings_potential': (
                consolidation_summary['total_potential_savings'] + 
                shipping_savings['potential_savings']
            ),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_consolidation_visibility(self) -> Dict:
        """Enhanced visibility into consolidation opportunities"""
        opportunities = self.consolidation_optimizer.find_consolidation_opportunities()
        
        # Categorize opportunities by savings potential
        high_value = [opp for opp in opportunities if opp['potential_savings'] > 1000]
        medium_value = [opp for opp in opportunities if 500 <= opp['potential_savings'] <= 1000]
        low_value = [opp for opp in opportunities if opp['potential_savings'] < 500]
        
        # Calculate time-sensitive opportunities
        urgent_opportunities = []
        for opp in opportunities[:10]:  # Top 10
            # Simulate urgency based on date ranges and savings
            days_old = (datetime.now() - datetime.strptime(opp['date_range'].split(' to ')[0], '%Y-%m-%d')).days
            urgency = 'High' if days_old > 14 and opp['potential_savings'] > 500 else 'Medium' if days_old > 7 else 'Low'
            
            urgent_opportunities.append({
                **opp,
                'urgency': urgency,
                'days_since_first_order': days_old
            })
        
        return {
            'total_opportunities': len(opportunities),
            'high_value_opportunities': len(high_value),
            'medium_value_opportunities': len(medium_value),
            'low_value_opportunities': len(low_value),
            'urgent_opportunities': sorted(urgent_opportunities, key=lambda x: x['potential_savings'], reverse=True)[:5],
            'top_suppliers_for_consolidation': [
                {
                    'supplier': opp['supplier'],
                    'potential_savings': opp['potential_savings'],
                    'order_count': opp['order_count']
                }
                for opp in opportunities[:10]
            ],
            'monthly_consolidation_trend': self._get_consolidation_trends()
        }
    
    def get_diversity_visibility(self) -> Dict:
        """Enhanced visibility into diversity metrics"""
        diversity_summary = self.diversity_tracker.get_diversity_performance_summary()
        diverse_suppliers = self.diversity_tracker.identify_diverse_suppliers()
        goals_tracking = self.diversity_tracker.track_diversity_goals(25.0)
        trends = self.diversity_tracker.get_monthly_diversity_trends()
        
        # Calculate diversity performance scores
        diversity_scores = {}
        for category, data in diversity_summary['diversity_breakdown'].items():
            score = min(100, (data['spend_percentage'] / 25) * 100)  # 25% target
            diversity_scores[category] = {
                'score': score,
                'status': 'Excellent' if score >= 100 else 'Good' if score >= 75 else 'Needs Improvement'
            }
        
        return {
            'overall_diversity_percentage': diversity_summary['diversity_spend_percentage'],
            'diversity_goal_status': goals_tracking['goal_status'],
            'diversity_categories_breakdown': diversity_summary['diversity_breakdown'],
            'diversity_performance_scores': diversity_scores,
            'top_diverse_suppliers': diverse_suppliers[:10],
            'diversity_trends': trends['trend_analysis'],
            'recommendations': goals_tracking['recommendations'],
            'compliance_status': {
                'meets_federal_goals': diversity_summary['diversity_spend_percentage'] >= 23,
                'meets_state_goals': diversity_summary['diversity_spend_percentage'] >= 25,
                'risk_level': 'Low' if diversity_summary['diversity_spend_percentage'] >= 25 else 'Medium'
            }
        }
    
    def get_cost_savings_visibility(self) -> Dict:
        """Enhanced visibility into all cost savings opportunities"""
        shipping_savings = self.shipping_optimizer.get_cost_savings_analysis()
        consolidation_summary = self.consolidation_optimizer.get_consolidation_summary()
        automation_alerts = self.automated_optimizer.generate_automation_alerts()
        
        # Calculate ROI metrics
        total_spend = self.df['Total_Amount'].sum()
        total_potential_savings = (
            shipping_savings['potential_savings'] + 
            consolidation_summary['total_potential_savings']
        )
        roi_percentage = (total_potential_savings / total_spend * 100) if total_spend > 0 else 0
        
        # Categorize savings by type
        savings_breakdown = {
            'shipping_optimization': shipping_savings['potential_savings'],
            'consolidation_opportunities': consolidation_summary['total_potential_savings'],
            'automation_alerts': sum(alert['potential_savings'] for alert in automation_alerts)
        }
        
        return {
            'total_potential_savings': total_potential_savings,
            'roi_percentage': roi_percentage,
            'savings_breakdown': savings_breakdown,
            'quick_wins': [
                alert for alert in automation_alerts 
                if alert['potential_savings'] > 100 and alert['priority'] == 'high'
            ][:5],
            'annual_savings_projection': total_potential_savings * 4,  # Quarterly data * 4
            'payback_period_months': 1,  # Immediate savings
            'implementation_priority': self._prioritize_savings_initiatives(savings_breakdown)
        }
    
    def _get_consolidation_trends(self) -> Dict:
        """Calculate consolidation trends over time"""
        # Group by month and calculate consolidation metrics
        monthly_data = self.df.groupby(self.df['PO_Date'].dt.to_period('M')).agg({
            'Consolidation_Opportunity': lambda x: (x == 'High').sum(),
            'Total_Amount': 'sum',
            'PO_ID': 'count'
        })
        
        return {
            'monthly_high_consolidation_orders': monthly_data['Consolidation_Opportunity'].to_dict(),
            'trend': 'Increasing' if monthly_data['Consolidation_Opportunity'].iloc[-1] > monthly_data['Consolidation_Opportunity'].iloc[0] else 'Stable'
        }
    
    def _prioritize_savings_initiatives(self, savings_breakdown: Dict) -> List[Dict]:
        """Prioritize savings initiatives by impact and effort"""
        initiatives = [
            {
                'initiative': 'Shipping Optimization',
                'potential_savings': savings_breakdown['shipping_optimization'],
                'effort': 'Low',
                'timeframe': '1-2 weeks',
                'priority_score': savings_breakdown['shipping_optimization'] / 1  # Low effort = high score
            },
            {
                'initiative': 'Order Consolidation',
                'potential_savings': savings_breakdown['consolidation_opportunities'],
                'effort': 'Medium',
                'timeframe': '2-4 weeks',
                'priority_score': savings_breakdown['consolidation_opportunities'] / 2  # Medium effort
            },
            {
                'initiative': 'Process Automation',
                'potential_savings': savings_breakdown['automation_alerts'],
                'effort': 'High',
                'timeframe': '1-3 months',
                'priority_score': savings_breakdown['automation_alerts'] / 3  # High effort
            }
        ]
        
        return sorted(initiatives, key=lambda x: x['priority_score'], reverse=True)
    
    def generate_executive_report(self) -> Dict:
        """Generate comprehensive executive report"""
        return {
            'executive_summary': self.get_executive_summary(),
            'consolidation_visibility': self.get_consolidation_visibility(),
            'diversity_visibility': self.get_diversity_visibility(),
            'cost_savings_visibility': self.get_cost_savings_visibility(),
            'key_recommendations': self._generate_key_recommendations(),
            'report_metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_period': f"{self.df['PO_Date'].min().strftime('%Y-%m-%d')} to {self.df['PO_Date'].max().strftime('%Y-%m-%d')}",
                'total_records_analyzed': len(self.df)
            }
        }
    
    def _generate_key_recommendations(self) -> List[Dict]:
        """Generate top executive recommendations"""
        consolidation_summary = self.consolidation_optimizer.get_consolidation_summary()
        diversity_summary = self.diversity_tracker.get_diversity_performance_summary()
        
        recommendations = []
        
        # Top consolidation recommendation
        if consolidation_summary['total_potential_savings'] > 1000:
            recommendations.append({
                'priority': 'High',
                'category': 'Cost Savings',
                'title': 'Implement Order Consolidation Program',
                'description': f"Consolidate orders to save ${consolidation_summary['total_potential_savings']:,.2f} annually",
                'impact': 'High',
                'effort': 'Medium'
            })
        
        # Diversity recommendation
        if diversity_summary['diversity_spend_percentage'] < 25:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Compliance',
                'title': 'Increase Diverse Supplier Utilization',
                'description': f"Current {diversity_summary['diversity_spend_percentage']:.1f}% vs 25% target",
                'impact': 'Medium',
                'effort': 'Low'
            })
        
        # Automation recommendation
        recommendations.append({
            'priority': 'High',
            'category': 'Efficiency',
            'title': 'Expand Shipping Automation',
            'description': 'Implement automated carrier selection for all orders',
            'impact': 'High',
            'effort': 'Low'
        })
        
        return recommendations

def main():
    """Demo executive dashboard"""
    print("📊 Executive Dashboard Demo")
    print("=" * 40)
    
    dashboard = ExecutiveDashboard()
    
    # Generate executive summary
    summary = dashboard.get_executive_summary()
    print(f"\n💼 Executive Summary:")
    print(f"Total Procurement Spend: ${summary['total_procurement_spend']:,.2f}")
    print(f"Total Cost Savings Potential: ${summary['total_cost_savings_potential']:,.2f}")
    print(f"Diversity Performance: {summary['diversity_spend_percentage']:.1f}% ({summary['diversity_goal_status']})")
    
    # Show consolidation visibility
    consolidation = dashboard.get_consolidation_visibility()
    print(f"\n📦 Consolidation Opportunities:")
    print(f"Total Opportunities: {consolidation['total_opportunities']}")
    print(f"High Value (>$1000): {consolidation['high_value_opportunities']}")
    
    # Show diversity visibility
    diversity = dashboard.get_diversity_visibility()
    print(f"\n🏢 Diversity Performance:")
    print(f"Overall: {diversity['overall_diversity_percentage']:.1f}%")
    print(f"Compliance Status: {diversity['compliance_status']['risk_level']} Risk")

if __name__ == "__main__":
    main()