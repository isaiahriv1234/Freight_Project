#!/usr/bin/env python3
"""
Shipping Cost Optimization and Carrier Selection
Analyzes historical data to recommend cost-effective shipping options
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class ShippingOptimizer:
    def __init__(self, data_path: str = 'Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv'):
        """Initialize with procurement data"""
        self.df = pd.read_csv(data_path)
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        self._analyze_carrier_performance()
    
    def _analyze_carrier_performance(self):
        """Analyze historical carrier performance metrics"""
        # Calculate carrier efficiency metrics
        self.carrier_stats = self.df.groupby('Carrier').agg({
            'Shipping_Cost': ['mean', 'std', 'count'],
            'Lead_Time_Days': ['mean', 'std'],
            'Total_Amount': 'sum'
        }).round(2)
        
        # Flatten column names
        self.carrier_stats.columns = ['_'.join(col).strip() for col in self.carrier_stats.columns]
        
        # Calculate cost efficiency (shipping cost as % of order value)
        carrier_efficiency = self.df.groupby('Carrier').apply(
            lambda x: (x['Shipping_Cost'].sum() / x['Total_Amount'].sum() * 100).round(2)
        )
        self.carrier_stats['Cost_Efficiency_Pct'] = carrier_efficiency
    
    def get_carrier_recommendations(self, order_value: float, weight_category: str = 'medium', 
                                  urgency: str = 'standard') -> List[Dict]:
        """
        Recommend optimal carriers based on order characteristics
        
        Args:
            order_value: Dollar value of the order
            weight_category: 'light', 'medium', 'heavy'
            urgency: 'standard', 'expedited', 'overnight'
        """
        recommendations = []
        
        # Define carrier preferences based on characteristics
        carrier_profiles = {
            'UPS': {'strength': 'medium_packages', 'cost_tier': 'medium', 'speed': 'fast'},
            'FedEx': {'strength': 'expedited', 'cost_tier': 'high', 'speed': 'fastest'},
            'Freight': {'strength': 'heavy_items', 'cost_tier': 'low', 'speed': 'slow'},
            'Ground': {'strength': 'cost_effective', 'cost_tier': 'lowest', 'speed': 'slowest'},
            'Electronic': {'strength': 'digital', 'cost_tier': 'none', 'speed': 'instant'}
        }
        
        for carrier in self.carrier_stats.index:
            if carrier == 'N/A':
                continue
                
            stats = self.carrier_stats.loc[carrier]
            profile = carrier_profiles.get(carrier, {})
            
            # Calculate recommendation score
            score = self._calculate_carrier_score(
                carrier, order_value, weight_category, urgency, stats, profile
            )
            
            # Predict shipping cost
            predicted_cost = self._predict_shipping_cost(carrier, order_value, stats)
            
            recommendations.append({
                'carrier': carrier,
                'predicted_cost': predicted_cost,
                'avg_lead_time': stats['Lead_Time_Days_mean'],
                'cost_efficiency': stats['Cost_Efficiency_Pct'],
                'reliability_score': min(100, stats['Shipping_Cost_count'] / 10 * 100),
                'recommendation_score': score,
                'reasoning': self._get_recommendation_reasoning(carrier, profile, urgency, weight_category)
            })
        
        # Sort by recommendation score
        return sorted(recommendations, key=lambda x: x['recommendation_score'], reverse=True)
    
    def _calculate_carrier_score(self, carrier: str, order_value: float, weight_category: str, 
                               urgency: str, stats: pd.Series, profile: Dict) -> float:
        """Calculate recommendation score for a carrier"""
        score = 50  # Base score
        
        # Cost efficiency bonus
        if stats['Cost_Efficiency_Pct'] < 5:
            score += 20
        elif stats['Cost_Efficiency_Pct'] < 10:
            score += 10
        
        # Speed matching
        if urgency == 'overnight' and profile.get('speed') == 'fastest':
            score += 25
        elif urgency == 'expedited' and profile.get('speed') in ['fastest', 'fast']:
            score += 15
        elif urgency == 'standard' and profile.get('cost_tier') in ['low', 'lowest']:
            score += 15
        
        # Weight category matching
        if weight_category == 'heavy' and carrier == 'Freight':
            score += 20
        elif weight_category == 'light' and carrier in ['UPS', 'FedEx']:
            score += 10
        
        # Order value considerations
        if order_value > 10000 and carrier == 'Freight':
            score += 15
        elif order_value < 1000 and carrier == 'Ground':
            score += 10
        
        return min(100, score)
    
    def _predict_shipping_cost(self, carrier: str, order_value: float, stats: pd.Series) -> float:
        """Predict shipping cost based on historical data"""
        base_cost = stats['Shipping_Cost_mean']
        
        # Adjust based on order value (simple linear relationship)
        value_factor = order_value / 1000  # Per $1000
        
        if carrier == 'Freight':
            predicted_cost = base_cost + (value_factor * 50)  # $50 per $1000
        elif carrier in ['UPS', 'FedEx']:
            predicted_cost = base_cost + (value_factor * 25)  # $25 per $1000
        else:
            predicted_cost = base_cost + (value_factor * 10)  # $10 per $1000
        
        return round(max(predicted_cost, 5.0), 2)  # Minimum $5 shipping
    
    def _get_recommendation_reasoning(self, carrier: str, profile: Dict, urgency: str, weight_category: str) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasons = []
        
        if carrier == 'Freight' and weight_category == 'heavy':
            reasons.append("Best for heavy/bulk items")
        elif carrier == 'FedEx' and urgency == 'overnight':
            reasons.append("Fastest delivery option")
        elif carrier == 'Ground' and urgency == 'standard':
            reasons.append("Most cost-effective for standard delivery")
        elif carrier == 'UPS':
            reasons.append("Good balance of cost and speed")
        
        if profile.get('cost_tier') == 'lowest':
            reasons.append("Lowest cost option")
        elif profile.get('speed') == 'fastest':
            reasons.append("Fastest delivery")
        
        return "; ".join(reasons) if reasons else "Standard option"
    
    def get_cost_savings_analysis(self) -> Dict:
        """Analyze potential cost savings from carrier optimization"""
        # Current spending by carrier
        current_spend = self.df.groupby('Carrier')['Shipping_Cost'].sum()
        
        # Simulate optimal carrier selection
        total_orders = len(self.df)
        potential_savings = 0
        
        for _, row in self.df.iterrows():
            current_cost = row['Shipping_Cost']
            recommendations = self.get_carrier_recommendations(
                row['Total_Amount'], 'medium', 'standard'
            )
            
            if recommendations:
                optimal_cost = recommendations[0]['predicted_cost']
                potential_savings += max(0, current_cost - optimal_cost)
        
        return {
            'current_total_shipping': current_spend.sum(),
            'potential_savings': potential_savings,
            'savings_percentage': (potential_savings / current_spend.sum() * 100) if current_spend.sum() > 0 else 0,
            'carrier_breakdown': current_spend.to_dict()
        }
    
    def get_carrier_performance_summary(self) -> Dict:
        """Get summary of carrier performance metrics"""
        summary = {}
        
        for carrier in self.carrier_stats.index:
            if carrier == 'N/A':
                continue
                
            stats = self.carrier_stats.loc[carrier]
            summary[carrier] = {
                'avg_cost': stats['Shipping_Cost_mean'],
                'avg_lead_time': stats['Lead_Time_Days_mean'],
                'cost_efficiency': stats['Cost_Efficiency_Pct'],
                'total_shipments': int(stats['Shipping_Cost_count']),
                'reliability': 'High' if stats['Shipping_Cost_count'] > 20 else 'Medium' if stats['Shipping_Cost_count'] > 10 else 'Low'
            }
        
        return summary

def main():
    """Demo the shipping optimizer"""
    print("🚛 Shipping Cost Optimizer Demo")
    print("=" * 40)
    
    optimizer = ShippingOptimizer()
    
    # Example: Get recommendations for a $5000 order
    print("\n📦 Carrier Recommendations for $5,000 Order:")
    recommendations = optimizer.get_carrier_recommendations(5000, 'medium', 'standard')
    
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"{i}. {rec['carrier']}")
        print(f"   Predicted Cost: ${rec['predicted_cost']}")
        print(f"   Lead Time: {rec['avg_lead_time']:.1f} days")
        print(f"   Score: {rec['recommendation_score']:.0f}/100")
        print(f"   Reasoning: {rec['reasoning']}\n")
    
    # Cost savings analysis
    print("💰 Cost Savings Analysis:")
    savings = optimizer.get_cost_savings_analysis()
    print(f"Current Total Shipping: ${savings['current_total_shipping']:,.2f}")
    print(f"Potential Savings: ${savings['potential_savings']:,.2f}")
    print(f"Savings Percentage: {savings['savings_percentage']:.1f}%")

if __name__ == "__main__":
    main()