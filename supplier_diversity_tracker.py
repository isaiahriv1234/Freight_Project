#!/usr/bin/env python3
"""
Supplier Diversity Tracking and Performance Monitor
Automatically identifies diverse suppliers and tracks real-time performance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class SupplierDiversityTracker:
    def __init__(self, data_path: str = 'Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv'):
        """Initialize with procurement data"""
        self.df = pd.read_csv(data_path)
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        
        # Define diversity categories
        self.diversity_categories = {
            'DVBE': 'Disabled Veteran Business Enterprise',
            'OSB': 'Other Small Business',
            'WBE': 'Women Business Enterprise',
            'MBE': 'Minority Business Enterprise',
            'SBE': 'Small Business Enterprise'
        }
        
    def get_diversity_performance_summary(self) -> Dict:
        """Get overall diversity performance metrics"""
        total_spend = self.df['Total_Amount'].sum()
        total_orders = len(self.df)
        
        # Calculate diversity metrics
        diversity_breakdown = self.df.groupby('Supplier_Diversity_Category').agg({
            'Total_Amount': ['sum', 'count'],
            'Supplier_Name': 'nunique'
        }).round(2)
        
        diversity_summary = {}
        for category in self.df['Supplier_Diversity_Category'].unique():
            category_data = self.df[self.df['Supplier_Diversity_Category'] == category]
            spend = category_data['Total_Amount'].sum()
            orders = len(category_data)
            suppliers = category_data['Supplier_Name'].nunique()
            
            diversity_summary[category] = {
                'category_name': self.diversity_categories.get(category, category),
                'total_spend': spend,
                'spend_percentage': (spend / total_spend * 100) if total_spend > 0 else 0,
                'order_count': orders,
                'order_percentage': (orders / total_orders * 100) if total_orders > 0 else 0,
                'supplier_count': suppliers,
                'avg_order_value': spend / orders if orders > 0 else 0
            }
        
        return {
            'total_spend': total_spend,
            'total_orders': total_orders,
            'diversity_breakdown': diversity_summary,
            'diversity_spend_percentage': sum(s['spend_percentage'] for s in diversity_summary.values())
        }
    
    def identify_diverse_suppliers(self) -> List[Dict]:
        """Identify and rank diverse suppliers by performance"""
        diverse_suppliers = []
        
        for supplier in self.df['Supplier_Name'].unique():
            supplier_data = self.df[self.df['Supplier_Name'] == supplier]
            diversity_category = supplier_data['Supplier_Diversity_Category'].iloc[0]
            
            # Calculate supplier metrics
            total_spend = supplier_data['Total_Amount'].sum()
            order_count = len(supplier_data)
            avg_order_value = total_spend / order_count if order_count > 0 else 0
            avg_lead_time = supplier_data['Lead_Time_Days'].mean()
            
            # Calculate performance score
            performance_score = self._calculate_supplier_performance_score(supplier_data)
            
            diverse_suppliers.append({
                'supplier_name': supplier,
                'diversity_category': diversity_category,
                'category_description': self.diversity_categories.get(diversity_category, diversity_category),
                'total_spend': total_spend,
                'order_count': order_count,
                'avg_order_value': avg_order_value,
                'avg_lead_time': avg_lead_time,
                'performance_score': performance_score,
                'last_order_date': supplier_data['PO_Date'].max().strftime('%Y-%m-%d')
            })
        
        return sorted(diverse_suppliers, key=lambda x: x['total_spend'], reverse=True)
    
    def _calculate_supplier_performance_score(self, supplier_data: pd.DataFrame) -> float:
        """Calculate performance score for a supplier"""
        score = 50  # Base score
        
        # Order frequency bonus
        order_count = len(supplier_data)
        if order_count > 10:
            score += 20
        elif order_count > 5:
            score += 10
        
        # Consistency bonus (regular orders)
        date_range = (supplier_data['PO_Date'].max() - supplier_data['PO_Date'].min()).days
        if date_range > 0:
            order_frequency = order_count / (date_range / 30)  # Orders per month
            if order_frequency > 2:
                score += 15
            elif order_frequency > 1:
                score += 10
        
        # Lead time performance
        avg_lead_time = supplier_data['Lead_Time_Days'].mean()
        if avg_lead_time < 10:
            score += 15
        elif avg_lead_time < 20:
            score += 10
        
        return min(100, score)
    
    def track_diversity_goals(self, target_percentage: float = 25.0) -> Dict:
        """Track progress against diversity spending goals"""
        summary = self.get_diversity_performance_summary()
        current_percentage = summary['diversity_spend_percentage']
        
        # Calculate gap analysis
        total_spend = summary['total_spend']
        current_diverse_spend = sum(cat['total_spend'] for cat in summary['diversity_breakdown'].values())
        target_spend = total_spend * (target_percentage / 100)
        gap = target_spend - current_diverse_spend
        
        return {
            'target_percentage': target_percentage,
            'current_percentage': current_percentage,
            'gap_percentage': target_percentage - current_percentage,
            'target_spend': target_spend,
            'current_diverse_spend': current_diverse_spend,
            'spend_gap': gap,
            'goal_status': 'Met' if current_percentage >= target_percentage else 'Not Met',
            'recommendations': self._generate_diversity_recommendations(gap, summary)
        }
    
    def _generate_diversity_recommendations(self, gap: float, summary: Dict) -> List[str]:
        """Generate recommendations to improve diversity performance"""
        recommendations = []
        
        if gap > 0:
            recommendations.append(f"Increase diverse supplier spending by ${gap:,.2f} to meet goals")
            
            # Identify underutilized categories
            breakdown = summary['diversity_breakdown']
            if 'DVBE' in breakdown and breakdown['DVBE']['spend_percentage'] < 10:
                recommendations.append("Increase DVBE (Disabled Veteran) supplier utilization")
            
            if 'OSB' in breakdown and breakdown['OSB']['spend_percentage'] < 15:
                recommendations.append("Expand Other Small Business supplier base")
            
            recommendations.append("Review procurement processes to identify more diverse supplier opportunities")
        else:
            recommendations.append("Diversity goals are being met - maintain current performance")
        
        return recommendations
    
    def get_monthly_diversity_trends(self) -> Dict:
        """Track diversity performance trends over time"""
        monthly_data = self.df.groupby([
            self.df['PO_Date'].dt.to_period('M'),
            'Supplier_Diversity_Category'
        ])['Total_Amount'].sum().unstack(fill_value=0)
        
        # Calculate monthly percentages
        monthly_totals = monthly_data.sum(axis=1)
        monthly_percentages = monthly_data.div(monthly_totals, axis=0) * 100
        
        return {
            'monthly_spend': monthly_data.to_dict(),
            'monthly_percentages': monthly_percentages.to_dict(),
            'trend_analysis': self._analyze_diversity_trends(monthly_percentages)
        }
    
    def _analyze_diversity_trends(self, monthly_percentages: pd.DataFrame) -> Dict:
        """Analyze trends in diversity performance"""
        trends = {}
        
        for category in monthly_percentages.columns:
            values = monthly_percentages[category].values
            if len(values) > 1:
                # Simple trend calculation
                trend = 'Increasing' if values[-1] > values[0] else 'Decreasing'
                change = values[-1] - values[0]
                trends[category] = {
                    'trend': trend,
                    'change_percentage': change,
                    'current_level': values[-1]
                }
        
        return trends

def main():
    """Demo supplier diversity tracker"""
    print("🏢 Supplier Diversity Tracker Demo")
    print("=" * 40)
    
    tracker = SupplierDiversityTracker()
    
    # Get diversity performance summary
    summary = tracker.get_diversity_performance_summary()
    print(f"\n📊 Diversity Performance Summary:")
    print(f"Total Spend: ${summary['total_spend']:,.2f}")
    print(f"Diversity Spend: {summary['diversity_spend_percentage']:.1f}%")
    
    print(f"\nBreakdown by Category:")
    for category, data in summary['diversity_breakdown'].items():
        print(f"• {data['category_name']}: ${data['total_spend']:,.2f} ({data['spend_percentage']:.1f}%)")
    
    # Track diversity goals
    goals = tracker.track_diversity_goals(25.0)
    print(f"\n🎯 Diversity Goals (25% target):")
    print(f"Current: {goals['current_percentage']:.1f}%")
    print(f"Status: {goals['goal_status']}")
    if goals['spend_gap'] > 0:
        print(f"Gap: ${goals['spend_gap']:,.2f}")
    
    # Show top diverse suppliers
    suppliers = tracker.identify_diverse_suppliers()
    print(f"\n🏆 Top Diverse Suppliers:")
    for supplier in suppliers[:5]:
        print(f"• {supplier['supplier_name']} ({supplier['diversity_category']}): ${supplier['total_spend']:,.2f}")

if __name__ == "__main__":
    main()