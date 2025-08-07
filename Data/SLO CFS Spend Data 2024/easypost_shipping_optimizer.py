#!/usr/bin/env python3
"""
EasyPost Shipping Optimizer for Procurement System
Integrates real shipping rates and optimization
"""

import pandas as pd
import easypost
import os
from dotenv import load_dotenv

class ShippingOptimizer:
    def __init__(self):
        load_dotenv()  # Load .env file
        self.api_key = os.getenv('EASYPOST_API_KEY')
        if not self.api_key:
            raise ValueError("EASYPOST_API_KEY not found in environment")
        easypost.api_key = self.api_key
        
    def get_real_shipping_rates(self, order_data):
        """Get actual shipping rates from EasyPost"""
        try:
            shipment = easypost.Shipment.create(
                to_address={
                    "name": order_data.get('recipient_name', 'Cal Poly SLO'),
                    "street1": order_data.get('address', '1 Grand Ave'),
                    "city": order_data.get('city', 'San Luis Obispo'),
                    "state": order_data.get('state', 'CA'),
                    "zip": order_data.get('zip', '93407'),
                    "country": "US"
                },
                from_address={
                    "name": order_data['supplier_name'],
                    "street1": "123 Supplier St",
                    "city": "San Luis Obispo",
                    "state": "CA",
                    "zip": "93401",
                    "country": "US"
                },
                parcel={
                    "length": order_data.get('length', 12),
                    "width": order_data.get('width', 8),
                    "height": order_data.get('height', 6),
                    "weight": order_data.get('weight', 16)
                }
            )
            
            rates = []
            for rate in shipment.rates:
                rates.append({
                    'carrier': rate.carrier,
                    'service': rate.service,
                    'cost': float(rate.rate),
                    'delivery_days': rate.delivery_days,
                    'rate_id': rate.id
                })
            
            return sorted(rates, key=lambda x: x['cost'])
            
        except Exception as e:
            print(f"EasyPost API Error: {e}")
            return self._get_fallback_rates(order_data)
    
    def _get_fallback_rates(self, order_data):
        """Fallback rates if API fails"""
        base_cost = order_data.get('total_amount', 100) * 0.08
        return [
            {'carrier': 'UPS', 'service': 'Ground', 'cost': base_cost, 'delivery_days': 3},
            {'carrier': 'FedEx', 'service': 'Ground', 'cost': base_cost * 1.1, 'delivery_days': 3},
            {'carrier': 'USPS', 'service': 'Priority', 'cost': base_cost * 0.9, 'delivery_days': 2}
        ]
    
    def optimize_procurement_shipping(self, df):
        """Optimize shipping for entire procurement dataset"""
        print("🚚 OPTIMIZING SHIPPING WITH EASYPOST API")
        print("=" * 50)
        
        optimized_orders = []
        total_savings = 0
        
        for _, order in df.iterrows():
            order_data = {
                'supplier_name': order['Supplier_Name'],
                'total_amount': order['Total_Amount'],
                'current_shipping': order['Shipping_Cost']
            }
            
            # Get real rates
            rates = self.get_real_shipping_rates(order_data)
            best_rate = rates[0] if rates else {'cost': order['Shipping_Cost'], 'carrier': 'Current'}
            
            # Calculate savings
            current_cost = order['Shipping_Cost']
            optimized_cost = best_rate['cost']
            savings = current_cost - optimized_cost
            total_savings += max(0, savings)
            
            optimized_orders.append({
                'PO_ID': order['PO_ID'],
                'Supplier': order['Supplier_Name'],
                'Current_Shipping': current_cost,
                'Optimized_Shipping': optimized_cost,
                'Best_Carrier': best_rate['carrier'],
                'Savings': max(0, savings),
                'Order_Value': order['Total_Amount']
            })
        
        # Create results DataFrame
        results_df = pd.DataFrame(optimized_orders)
        
        print(f"💰 Total Potential Savings: ${total_savings:,.2f}")
        print(f"📊 Average Savings per Order: ${total_savings/len(results_df):,.2f}")
        print(f"📈 Savings Percentage: {(total_savings/df['Shipping_Cost'].sum())*100:.1f}%")
        
        # Show top savings opportunities
        top_savings = results_df.nlargest(10, 'Savings')
        print(f"\n🎯 TOP 10 SAVINGS OPPORTUNITIES:")
        for _, row in top_savings.iterrows():
            print(f"  {row['Supplier']}: ${row['Savings']:.2f} savings ({row['Best_Carrier']})")
        
        return results_df
    
    def create_consolidation_shipments(self, df):
        """Create consolidated shipments using EasyPost"""
        print(f"\n📦 CONSOLIDATION ANALYSIS")
        print("=" * 50)
        
        # Group by supplier and week
        df['Week'] = pd.to_datetime(df['PO_Date']).dt.to_period('W')
        consolidation_groups = df.groupby(['Supplier_Name', 'Week'])
        
        consolidation_opportunities = []
        
        for (supplier, week), group in consolidation_groups:
            if len(group) > 1:  # Multiple orders same supplier/week
                total_weight = len(group) * 2  # Estimate 2 lbs per order
                total_value = group['Total_Amount'].sum()
                
                # Get consolidated shipping rate
                consolidated_data = {
                    'supplier_name': supplier,
                    'total_amount': total_value,
                    'weight': total_weight
                }
                
                rates = self.get_real_shipping_rates(consolidated_data)
                consolidated_cost = rates[0]['cost'] if rates else total_value * 0.05
                
                individual_shipping = group['Shipping_Cost'].sum()
                savings = individual_shipping - consolidated_cost
                
                if savings > 0:
                    consolidation_opportunities.append({
                        'Supplier': supplier,
                        'Week': str(week),
                        'Orders': len(group),
                        'Individual_Shipping': individual_shipping,
                        'Consolidated_Shipping': consolidated_cost,
                        'Savings': savings,
                        'Total_Value': total_value
                    })
        
        if consolidation_opportunities:
            consol_df = pd.DataFrame(consolidation_opportunities)
            total_consol_savings = consol_df['Savings'].sum()
            
            print(f"💰 Total Consolidation Savings: ${total_consol_savings:,.2f}")
            print(f"📊 Consolidation Opportunities: {len(consol_df)}")
            
            # Show top consolidation opportunities
            top_consol = consol_df.nlargest(5, 'Savings')
            print(f"\n🎯 TOP CONSOLIDATION OPPORTUNITIES:")
            for _, row in top_consol.iterrows():
                print(f"  {row['Supplier']} (Week {row['Week']}): ${row['Savings']:.2f} savings")
            
            return consol_df
        else:
            print("No consolidation opportunities found")
            return pd.DataFrame()

def main():
    """Main optimization function"""
    print("🚀 EASYPOST SHIPPING OPTIMIZATION")
    print("=" * 50)
    
    # Load procurement data
    try:
        df = pd.read_csv('/Users/isaiahrivera/Desktop/Summer_Camp/Freight_Project/Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv')
        print(f"📊 Loaded {len(df)} procurement records")
        
        # Initialize optimizer
        optimizer = ShippingOptimizer()
        
        # Run shipping optimization
        shipping_results = optimizer.optimize_procurement_shipping(df)
        
        # Run consolidation analysis
        consolidation_results = optimizer.create_consolidation_shipments(df)
        
        # Save results
        shipping_results.to_csv('shipping_optimization_results.csv', index=False)
        if not consolidation_results.empty:
            consolidation_results.to_csv('consolidation_opportunities.csv', index=False)
        
        print(f"\n✅ OPTIMIZATION COMPLETE")
        print(f"📁 Results saved to:")
        print(f"   - shipping_optimization_results.csv")
        print(f"   - consolidation_opportunities.csv")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()