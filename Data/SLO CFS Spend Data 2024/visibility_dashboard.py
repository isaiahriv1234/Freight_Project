#!/usr/bin/env python3
"""
Enhanced Visibility Dashboard for Consolidation and Diversity Metrics
Solves the "limited visibility" problem with real-time analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class VisibilityDashboard:
    def __init__(self, data_file):
        self.df = pd.read_csv(data_file)
        self.df['PO_Date'] = pd.to_datetime(self.df.get('PO_Date', datetime.now()))
    
    def generate_consolidation_insights(self):
        """Generate detailed consolidation opportunity analysis"""
        
        consolidation_analysis = {
            'supplier_consolidation': self.analyze_supplier_consolidation(),
            'carrier_consolidation': self.analyze_carrier_consolidation(),
            'geographic_consolidation': self.analyze_geographic_consolidation(),
            'time_based_consolidation': self.analyze_time_consolidation(),
            'cost_impact_analysis': self.calculate_consolidation_savings()
        }
        
        return consolidation_analysis
    
    def analyze_supplier_consolidation(self):
        """Identify suppliers with multiple small orders that could be consolidated"""
        
        supplier_analysis = self.df.groupby('supplier_name').agg({
            'total_amount': ['count', 'sum', 'mean'],
            'shipping_cost': 'sum',
            'lead_time_days': 'mean'
        }).round(2)
        
        # Flatten column names
        supplier_analysis.columns = ['order_count', 'total_spend', 'avg_order_size', 'total_shipping', 'avg_lead_time']
        
        # Identify consolidation opportunities
        consolidation_candidates = supplier_analysis[
            (supplier_analysis['order_count'] >= 3) & 
            (supplier_analysis['avg_order_size'] < 1000)
        ].copy()
        
        consolidation_candidates['potential_savings'] = consolidation_candidates['total_shipping'] * 0.3  # 30% savings estimate
        
        return consolidation_candidates.to_dict('index')
    
    def analyze_carrier_consolidation(self):
        """Analyze carrier usage patterns for consolidation opportunities"""
        
        carrier_analysis = self.df.groupby(['supplier_name', 'carrier']).agg({
            'total_amount': 'sum',
            'shipping_cost': 'sum',
            'lead_time_days': 'mean'
        }).reset_index()
        
        # Find suppliers using multiple carriers
        multi_carrier_suppliers = carrier_analysis.groupby('supplier_name').size()
        consolidation_opportunities = multi_carrier_suppliers[multi_carrier_suppliers > 1]
        
        return {
            'multi_carrier_suppliers': consolidation_opportunities.to_dict(),
            'carrier_efficiency': carrier_analysis.groupby('carrier').agg({
                'shipping_cost': 'mean',
                'lead_time_days': 'mean'
            }).to_dict('index')
        }
    
    def analyze_geographic_consolidation(self):
        """Analyze geographic consolidation opportunities"""
        
        if 'geographic_location' in self.df.columns:
            geo_analysis = self.df.groupby('geographic_location').agg({
                'supplier_name': 'nunique',
                'total_amount': 'sum',
                'shipping_cost': 'sum'
            })
            
            return geo_analysis.to_dict('index')
        
        return {'message': 'Geographic data not available'}
    
    def analyze_time_consolidation(self):
        """Analyze time-based consolidation opportunities"""
        
        # Group by month to find consolidation patterns
        self.df['month'] = self.df['PO_Date'].dt.to_period('M')
        
        monthly_analysis = self.df.groupby(['supplier_name', 'month']).agg({
            'total_amount': ['count', 'sum'],
            'shipping_cost': 'sum'
        })
        
        # Find suppliers with frequent small orders
        frequent_orders = monthly_analysis[monthly_analysis[('total_amount', 'count')] >= 2]
        
        return {
            'frequent_order_suppliers': len(frequent_orders),
            'consolidation_potential': frequent_orders.sum().to_dict()
        }
    
    def calculate_consolidation_savings(self):
        """Calculate potential cost savings from consolidation"""
        
        # Current state
        current_shipping_cost = self.df['shipping_cost'].sum()
        current_orders = len(self.df)
        
        # Consolidation scenarios
        scenarios = {
            'conservative': {
                'order_reduction': 0.15,  # 15% fewer orders
                'shipping_savings': 0.20   # 20% shipping savings
            },
            'moderate': {
                'order_reduction': 0.25,
                'shipping_savings': 0.35
            },
            'aggressive': {
                'order_reduction': 0.40,
                'shipping_savings': 0.50
            }
        }
        
        savings_analysis = {}
        for scenario, params in scenarios.items():
            potential_savings = current_shipping_cost * params['shipping_savings']
            order_reduction = current_orders * params['order_reduction']
            
            savings_analysis[scenario] = {
                'potential_shipping_savings': round(potential_savings, 2),
                'orders_consolidated': int(order_reduction),
                'annual_savings_estimate': round(potential_savings * 12, 2)  # Annualized
            }
        
        return savings_analysis
    
    def generate_diversity_insights(self):
        """Generate comprehensive diversity metrics and insights"""
        
        diversity_analysis = {
            'current_diversity_breakdown': self.analyze_diversity_breakdown(),
            'diversity_performance_metrics': self.analyze_diversity_performance(),
            'diversity_trends': self.analyze_diversity_trends(),
            'compliance_status': self.check_diversity_compliance(),
            'improvement_recommendations': self.generate_diversity_recommendations()
        }
        
        return diversity_analysis
    
    def analyze_diversity_breakdown(self):
        """Detailed breakdown of diversity spending"""
        
        diversity_breakdown = self.df.groupby('diversity_category').agg({
            'total_amount': ['sum', 'count', 'mean'],
            'shipping_cost': 'sum',
            'supplier_name': 'nunique'
        }).round(2)
        
        diversity_breakdown.columns = ['total_spend', 'order_count', 'avg_order_size', 'shipping_cost', 'unique_suppliers']
        
        # Calculate percentages
        total_spend = self.df['total_amount'].sum()
        diversity_breakdown['spend_percentage'] = (diversity_breakdown['total_spend'] / total_spend * 100).round(2)
        
        return diversity_breakdown.to_dict('index')
    
    def analyze_diversity_performance(self):
        """Analyze performance metrics by diversity category"""
        
        performance_metrics = self.df.groupby('diversity_category').agg({
            'lead_time_days': ['mean', 'std'],
            'shipping_cost': 'mean',
            'total_amount': 'mean'
        }).round(2)
        
        performance_metrics.columns = ['avg_lead_time', 'lead_time_std', 'avg_shipping_cost', 'avg_order_value']
        
        return performance_metrics.to_dict('index')
    
    def analyze_diversity_trends(self):
        """Analyze diversity spending trends over time"""
        
        if 'PO_Date' in self.df.columns:
            monthly_diversity = self.df.groupby([
                self.df['PO_Date'].dt.to_period('M'), 
                'diversity_category'
            ])['total_amount'].sum().unstack(fill_value=0)
            
            return monthly_diversity.to_dict('index')
        
        return {'message': 'Date data not available for trend analysis'}
    
    def check_diversity_compliance(self):
        """Check compliance with diversity spending targets"""
        
        total_spend = self.df['total_amount'].sum()
        diversity_spend = self.df[self.df['diversity_category'].isin(['DVBE', 'OSB'])]['total_amount'].sum()
        diversity_percentage = (diversity_spend / total_spend * 100) if total_spend > 0 else 0
        
        # Common diversity targets
        targets = {
            'overall_diversity': 25,  # 25% target
            'dvbe_target': 3,         # 3% DVBE target
            'small_business': 23      # 23% small business target
        }
        
        compliance_status = {
            'current_diversity_percentage': round(diversity_percentage, 2),
            'meets_overall_target': diversity_percentage >= targets['overall_diversity'],
            'gap_to_target': round(targets['overall_diversity'] - diversity_percentage, 2),
            'targets': targets
        }
        
        return compliance_status
    
    def generate_diversity_recommendations(self):
        """Generate actionable diversity improvement recommendations"""
        
        recommendations = []
        
        # Analyze current state
        diversity_breakdown = self.analyze_diversity_breakdown()
        compliance = self.check_diversity_compliance()
        
        if not compliance['meets_overall_target']:
            gap = compliance['gap_to_target']
            recommendations.append({
                'priority': 'High',
                'action': f'Increase diversity spending by {gap}% to meet targets',
                'estimated_impact': f'${(self.df["total_amount"].sum() * gap / 100):,.2f} additional diversity spend needed'
            })
        
        # Identify underperforming categories
        for category, metrics in diversity_breakdown.items():
            if metrics['spend_percentage'] < 5:  # Less than 5% spend
                recommendations.append({
                    'priority': 'Medium',
                    'action': f'Increase engagement with {category} suppliers',
                    'estimated_impact': f'Currently only {metrics["spend_percentage"]}% of total spend'
                })
        
        return recommendations
    
    def generate_executive_summary(self):
        """Generate executive summary dashboard"""
        
        consolidation_insights = self.generate_consolidation_insights()
        diversity_insights = self.generate_diversity_insights()
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'key_metrics': {
                'total_spend': self.df['total_amount'].sum(),
                'total_suppliers': self.df['supplier_name'].nunique(),
                'diversity_percentage': diversity_insights['compliance_status']['current_diversity_percentage'],
                'potential_consolidation_savings': consolidation_insights['cost_impact_analysis']['moderate']['potential_shipping_savings']
            },
            'consolidation_opportunities': consolidation_insights,
            'diversity_metrics': diversity_insights,
            'action_items': self.generate_action_items()
        }
        
        return summary
    
    def generate_action_items(self):
        """Generate prioritized action items"""
        
        actions = [
            {
                'priority': 1,
                'category': 'Consolidation',
                'action': 'Implement supplier consolidation program',
                'timeline': '30 days',
                'expected_savings': '$5,000-15,000 annually'
            },
            {
                'priority': 2,
                'category': 'Diversity',
                'action': 'Increase DVBE supplier engagement',
                'timeline': '60 days',
                'expected_impact': 'Meet compliance targets'
            },
            {
                'priority': 3,
                'category': 'Optimization',
                'action': 'Implement carrier optimization',
                'timeline': '45 days',
                'expected_savings': '$3,000-8,000 annually'
            }
        ]
        
        return actions

def main():
    """Generate comprehensive visibility dashboard"""
    
    # Load data
    dashboard = VisibilityDashboard('master_shipping_dataset_20250807_002133.csv')
    
    # Generate executive summary
    summary = dashboard.generate_executive_summary()
    
    # Save dashboard
    with open('visibility_dashboard_report.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("📊 ENHANCED VISIBILITY DASHBOARD GENERATED")
    print(f"💰 Total Spend: ${summary['key_metrics']['total_spend']:,.2f}")
    print(f"🏢 Suppliers: {summary['key_metrics']['total_suppliers']}")
    print(f"🎯 Diversity %: {summary['key_metrics']['diversity_percentage']}%")
    print(f"💡 Consolidation Savings: ${summary['key_metrics']['potential_consolidation_savings']:,.2f}")
    
    return summary

if __name__ == "__main__":
    main()