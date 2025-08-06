#!/usr/bin/env python3
"""
Shipment Consolidation Strategy Optimizer
Analyzes orders to recommend consolidation opportunities for cost savings
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class ConsolidationOptimizer:
    def __init__(self, data_path: str = 'Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv'):
        """Initialize with procurement data"""
        self.df = pd.read_csv(data_path)
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        
    def find_consolidation_opportunities(self, days_window: int = 7) -> List[Dict]:
        """Find orders that can be consolidated within time window"""
        opportunities = []
        
        # Group by supplier and date proximity
        for supplier in self.df['Supplier_Name'].unique():
            supplier_orders = self.df[self.df['Supplier_Name'] == supplier].copy()
            supplier_orders = supplier_orders.sort_values('PO_Date')
            
            # Find orders within consolidation window
            for i, order in supplier_orders.iterrows():
                date_window = supplier_orders[
                    (supplier_orders['PO_Date'] >= order['PO_Date']) &
                    (supplier_orders['PO_Date'] <= order['PO_Date'] + timedelta(days=days_window))
                ]
                
                if len(date_window) > 1:
                    total_shipping = date_window['Shipping_Cost'].sum()
                    total_value = date_window['Total_Amount'].sum()
                    
                    # Estimate consolidated shipping cost (typically 60-80% of individual costs)
                    consolidated_shipping = total_shipping * 0.7
                    potential_savings = total_shipping - consolidated_shipping
                    
                    if potential_savings > 50:  # Only significant savings
                        opportunities.append({
                            'supplier': supplier,
                            'order_count': len(date_window),
                            'date_range': f"{date_window['PO_Date'].min().strftime('%Y-%m-%d')} to {date_window['PO_Date'].max().strftime('%Y-%m-%d')}",
                            'total_value': total_value,
                            'current_shipping': total_shipping,
                            'consolidated_shipping': consolidated_shipping,
                            'potential_savings': potential_savings,
                            'savings_percentage': (potential_savings / total_shipping * 100),
                            'po_ids': date_window['PO_ID'].tolist()
                        })
        
        return sorted(opportunities, key=lambda x: x['potential_savings'], reverse=True)
    
    def get_consolidation_summary(self) -> Dict:
        """Get overall consolidation analysis"""
        opportunities = self.find_consolidation_opportunities()
        
        total_savings = sum(opp['potential_savings'] for opp in opportunities)
        total_current_shipping = sum(opp['current_shipping'] for opp in opportunities)
        
        # Analyze by consolidation opportunity level
        consolidation_levels = self.df['Consolidation_Opportunity'].value_counts()
        
        return {
            'total_opportunities': len(opportunities),
            'total_potential_savings': total_savings,
            'total_affected_shipping': total_current_shipping,
            'average_savings_per_opportunity': total_savings / len(opportunities) if opportunities else 0,
            'consolidation_levels': consolidation_levels.to_dict(),
            'top_opportunities': opportunities[:5]
        }
    
    def recommend_consolidation_strategy(self, supplier: str = None) -> Dict:
        """Recommend specific consolidation strategies"""
        if supplier:
            supplier_data = self.df[self.df['Supplier_Name'] == supplier]
        else:
            supplier_data = self.df
        
        # Analyze order patterns
        order_frequency = supplier_data.groupby('Order_Frequency').agg({
            'Total_Amount': 'sum',
            'Shipping_Cost': 'sum',
            'PO_ID': 'count'
        })
        
        # Analyze consolidation opportunities by level
        consolidation_analysis = supplier_data.groupby('Consolidation_Opportunity').agg({
            'Shipping_Cost': ['sum', 'mean', 'count'],
            'Total_Amount': 'sum'
        })
        
        recommendations = []
        
        # High consolidation opportunity items
        high_consolidation = supplier_data[supplier_data['Consolidation_Opportunity'] == 'High']
        if not high_consolidation.empty:
            recommendations.append({
                'strategy': 'Batch High-Consolidation Orders',
                'description': f'Combine {len(high_consolidation)} high-consolidation orders',
                'potential_savings': high_consolidation['Shipping_Cost'].sum() * 0.4,
                'implementation': 'Schedule weekly batch orders for high-consolidation items'
            })
        
        # Frequent small orders
        frequent_orders = supplier_data[supplier_data['Order_Frequency'].isin(['Weekly', 'Monthly'])]
        if not frequent_orders.empty and frequent_orders['Total_Amount'].mean() < 1000:
            recommendations.append({
                'strategy': 'Consolidate Frequent Small Orders',
                'description': f'Combine {len(frequent_orders)} frequent small orders',
                'potential_savings': frequent_orders['Shipping_Cost'].sum() * 0.3,
                'implementation': 'Move to bi-weekly or monthly ordering cycles'
            })
        
        return {
            'supplier': supplier or 'All Suppliers',
            'recommendations': recommendations,
            'order_frequency_analysis': order_frequency.to_dict(),
            'consolidation_level_analysis': consolidation_analysis.to_dict()
        }

def main():
    """Demo consolidation optimizer"""
    print("📦 Shipment Consolidation Optimizer Demo")
    print("=" * 45)
    
    optimizer = ConsolidationOptimizer()
    
    # Get consolidation summary
    summary = optimizer.get_consolidation_summary()
    print(f"\n💰 Consolidation Summary:")
    print(f"Total Opportunities: {summary['total_opportunities']}")
    print(f"Potential Savings: ${summary['total_potential_savings']:,.2f}")
    print(f"Average per Opportunity: ${summary['average_savings_per_opportunity']:,.2f}")
    
    # Show top opportunities
    print(f"\n🎯 Top Consolidation Opportunities:")
    for i, opp in enumerate(summary['top_opportunities'][:3], 1):
        print(f"{i}. {opp['supplier']}")
        print(f"   Orders: {opp['order_count']} | Savings: ${opp['potential_savings']:,.2f}")
        print(f"   Date Range: {opp['date_range']}")
    
    # Get strategy recommendations
    strategy = optimizer.recommend_consolidation_strategy()
    print(f"\n📋 Recommended Strategies:")
    for rec in strategy['recommendations'][:2]:
        print(f"• {rec['strategy']}: ${rec['potential_savings']:,.2f} savings")
        print(f"  {rec['implementation']}")

if __name__ == "__main__":
    main()