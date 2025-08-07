#!/usr/bin/env python3
"""
Procurement Optimization Analysis Script with EasyPost Integration
Addresses: Manual decentralized purchasing, shipping cost optimization, 
consolidation opportunities, and supplier diversity tracking
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# EasyPost Integration
try:
    import easypost
    import os
    from dotenv import load_dotenv
    
    load_dotenv()  # Load .env file
    api_key = os.getenv('EASYPOST_API_KEY')
    if api_key:
        easypost.api_key = api_key
        EASYPOST_AVAILABLE = True
    else:
        EASYPOST_AVAILABLE = False
        print("⚠️  EASYPOST_API_KEY not found in .env file")
except ImportError:
    EASYPOST_AVAILABLE = False
    print("⚠️  EasyPost not installed. Run: pip install easypost python-dotenv")

def load_and_clean_data(file_path):
    """Load and clean the procurement data"""
    df = pd.read_csv(file_path)
    
    # Convert date columns
    df['PO_Date'] = pd.to_datetime(df['PO_Date'])
    
    # Fill any remaining null values
    df['Shipping_Cost'] = df['Shipping_Cost'].fillna(0)
    df['Carrier'] = df['Carrier'].fillna('Unknown')
    df['Lead_Time_Days'] = df['Lead_Time_Days'].fillna(14)  # Default 2 weeks
    df['Geographic_Location'] = df['Geographic_Location'].fillna('Unknown')
    
    return df

def analyze_historical_spend(df):
    """Analyze historical spend to identify savings opportunities"""
    print("=== HISTORICAL SPEND ANALYSIS ===")
    
    # Total spend by category
    spend_by_category = df.groupby('Supplier_Diversity_Category')['Total_Amount'].sum().sort_values(ascending=False)
    print(f"\nSpend by Supplier Category:")
    for category, amount in spend_by_category.items():
        print(f"  {category}: ${amount:,.2f}")
    
    # Top suppliers by spend
    top_suppliers = df.groupby('Supplier_Name')['Total_Amount'].sum().sort_values(ascending=False).head(10)
    print(f"\nTop 10 Suppliers by Spend:")
    for supplier, amount in top_suppliers.items():
        print(f"  {supplier}: ${amount:,.2f}")
    
    # Identify potential savings through consolidation
    supplier_counts = df.groupby('Description').agg({
        'Supplier_Name': 'nunique',
        'Total_Amount': 'sum'
    }).sort_values('Supplier_Name', ascending=False)
    
    consolidation_opportunities = supplier_counts[supplier_counts['Supplier_Name'] > 1]
    print(f"\nConsolidation Opportunities (Same items from multiple suppliers):")
    for item, data in consolidation_opportunities.head(10).iterrows():
        print(f"  {item}: {data['Supplier_Name']} suppliers, ${data['Total_Amount']:,.2f} total")
    
    return spend_by_category, top_suppliers, consolidation_opportunities

def predict_shipping_optimization(df):
    """Predict cost-effective shipping and carrier selections"""
    print("\n=== SHIPPING COST OPTIMIZATION ===")
    
    # Analyze shipping costs by carrier
    carrier_analysis = df.groupby('Carrier').agg({
        'Shipping_Cost': ['mean', 'sum', 'count'],
        'Total_Amount': 'sum',
        'Lead_Time_Days': 'mean'
    }).round(2)
    
    carrier_analysis.columns = ['Avg_Shipping_Cost', 'Total_Shipping_Cost', 'Order_Count', 'Total_Order_Value', 'Avg_Lead_Time']
    carrier_analysis['Shipping_Cost_Ratio'] = (carrier_analysis['Total_Shipping_Cost'] / carrier_analysis['Total_Order_Value'] * 100).round(2)
    
    print("Carrier Performance Analysis:")
    print(carrier_analysis.sort_values('Shipping_Cost_Ratio'))
    
    # Identify high shipping cost items
    high_shipping_items = df[df['Shipping_Cost'] > df['Shipping_Cost'].quantile(0.9)]
    print(f"\nHigh Shipping Cost Items (Top 10%):")
    for _, item in high_shipping_items.nlargest(10, 'Shipping_Cost').iterrows():
        print(f"  {item['Description']}: ${item['Shipping_Cost']:.2f} shipping on ${item['Total_Amount']:.2f} order")
    
    return carrier_analysis, high_shipping_items

def recommend_consolidation_strategies(df):
    """Recommend shipment consolidation strategies"""
    print("\n=== CONSOLIDATION RECOMMENDATIONS ===")
    
    # Group by supplier and date proximity for consolidation opportunities
    df['Week'] = df['PO_Date'].dt.to_period('W')
    
    consolidation_opps = df.groupby(['Supplier_Name', 'Week']).agg({
        'PO_ID': 'count',
        'Total_Amount': 'sum',
        'Shipping_Cost': 'sum'
    }).reset_index()
    
    # Find suppliers with multiple orders in same week
    multi_order_weeks = consolidation_opps[consolidation_opps['PO_ID'] > 1]
    
    print("Weekly Consolidation Opportunities:")
    for _, opp in multi_order_weeks.nlargest(10, 'Shipping_Cost').iterrows():
        potential_savings = opp['Shipping_Cost'] * 0.3  # Assume 30% savings from consolidation
        print(f"  {opp['Supplier_Name']} (Week {opp['Week']}): {opp['PO_ID']} orders, "
              f"${opp['Shipping_Cost']:.2f} shipping, potential savings: ${potential_savings:.2f}")
    
    # Geographic consolidation opportunities
    geo_consolidation = df.groupby(['Geographic_Location', 'Week']).agg({
        'Supplier_Name': 'nunique',
        'Total_Amount': 'sum',
        'Shipping_Cost': 'sum'
    }).reset_index()
    
    geo_opps = geo_consolidation[geo_consolidation['Supplier_Name'] > 1]
    print(f"\nGeographic Consolidation Opportunities:")
    for _, opp in geo_opps.nlargest(5, 'Shipping_Cost').iterrows():
        potential_savings = opp['Shipping_Cost'] * 0.25  # Assume 25% savings
        print(f"  {opp['Geographic_Location']} (Week {opp['Week']}): {opp['Supplier_Name']} suppliers, "
              f"${opp['Shipping_Cost']:.2f} shipping, potential savings: ${potential_savings:.2f}")
    
    return multi_order_weeks, geo_opps

def track_supplier_diversity(df):
    """Track real-time supplier diversity performance"""
    print("\n=== SUPPLIER DIVERSITY TRACKING ===")
    
    diversity_metrics = df.groupby('Supplier_Diversity_Category').agg({
        'Total_Amount': ['sum', 'count'],
        'Supplier_Name': 'nunique'
    }).round(2)
    
    diversity_metrics.columns = ['Total_Spend', 'Order_Count', 'Unique_Suppliers']
    total_spend = diversity_metrics['Total_Spend'].sum()
    diversity_metrics['Spend_Percentage'] = (diversity_metrics['Total_Spend'] / total_spend * 100).round(2)
    
    print("Supplier Diversity Metrics:")
    print(diversity_metrics.sort_values('Spend_Percentage', ascending=False))
    
    # Diversity goals tracking (example targets)
    diversity_goals = {
        'DVBE': 3.0,  # 3% goal for DVBE
        'OSB': 25.0,  # 25% goal for small business
        'MB': 5.0     # 5% goal for microbusiness
    }
    
    print(f"\nDiversity Goals Performance:")
    for category, goal in diversity_goals.items():
        if category in diversity_metrics.index:
            actual = diversity_metrics.loc[category, 'Spend_Percentage']
            status = "✓ MEETING" if actual >= goal else "✗ BELOW"
            print(f"  {category}: {actual:.1f}% (Goal: {goal:.1f}%) - {status}")
    
    return diversity_metrics

def identify_diverse_suppliers(df):
    """Automatically identify and match diverse suppliers"""
    print("\n=== DIVERSE SUPPLIER MATCHING ===")
    
    # Find diverse suppliers for common categories
    common_categories = df['NIGP_Code'].value_counts().head(10).index
    
    for category in common_categories:
        category_suppliers = df[df['NIGP_Code'] == category]
        diverse_suppliers = category_suppliers[category_suppliers['Supplier_Diversity_Category'].isin(['DVBE', 'OSB', 'MB'])]
        
        if not diverse_suppliers.empty:
            print(f"\nNIGP Code {category}:")
            supplier_summary = diverse_suppliers.groupby(['Supplier_Name', 'Supplier_Diversity_Category']).agg({
                'Total_Amount': 'sum',
                'Order_Frequency': 'first'
            }).sort_values('Total_Amount', ascending=False)
            
            for (supplier, category_type), data in supplier_summary.head(3).iterrows():
                print(f"  {supplier} ({category_type}): ${data['Total_Amount']:,.2f}, {data['Order_Frequency']} orders")

def generate_recommendations(df):
    """Generate actionable recommendations"""
    print("\n=== ACTIONABLE RECOMMENDATIONS ===")
    
    recommendations = []
    
    # Shipping optimization
    high_shipping_ratio = df[df['Shipping_Cost'] / df['Total_Amount'] > 0.15]
    if not high_shipping_ratio.empty:
        recommendations.append(f"1. SHIPPING OPTIMIZATION: {len(high_shipping_ratio)} orders have shipping costs >15% of order value. "
                             f"Consider consolidating or negotiating better rates.")
    
    # Supplier consolidation
    duplicate_items = df.groupby('Description')['Supplier_Name'].nunique()
    multi_supplier_items = duplicate_items[duplicate_items > 1]
    if not multi_supplier_items.empty:
        recommendations.append(f"2. SUPPLIER CONSOLIDATION: {len(multi_supplier_items)} items are purchased from multiple suppliers. "
                             f"Consolidate to preferred vendors for better pricing.")
    
    # Diversity improvement
    diversity_spend = df.groupby('Supplier_Diversity_Category')['Total_Amount'].sum()
    total_spend = diversity_spend.sum()
    diverse_percentage = (diversity_spend.get('DVBE', 0) + diversity_spend.get('OSB', 0) + diversity_spend.get('MB', 0)) / total_spend * 100
    
    if diverse_percentage < 30:
        recommendations.append(f"3. DIVERSITY ENHANCEMENT: Current diverse supplier spend is {diverse_percentage:.1f}%. "
                             f"Increase diverse supplier utilization to meet goals.")
    
    # Automation opportunities
    frequent_orders = df.groupby(['Supplier_Name', 'Description']).size()
    automation_candidates = frequent_orders[frequent_orders >= 4]  # Quarterly or more frequent
    if not automation_candidates.empty:
        recommendations.append(f"4. AUTOMATION OPPORTUNITY: {len(automation_candidates)} supplier-item combinations "
                             f"have 4+ orders annually. Consider automated reordering.")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{rec}")
    
    return recommendations

def get_real_shipping_rates(order_data):
    """Get real shipping rates using EasyPost API"""
    if not EASYPOST_AVAILABLE:
        return []
    
    try:
        shipment = easypost.Shipment.create(
            to_address={
                "name": "Cal Poly SLO",
                "street1": "1 Grand Ave",
                "city": "San Luis Obispo",
                "state": "CA",
                "zip": "93407",
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
                "length": 12,
                "width": 8,
                "height": 6,
                "weight": 16
            }
        )
        
        rates = []
        for rate in shipment.rates:
            rates.append({
                'carrier': rate.carrier,
                'service': rate.service,
                'cost': float(rate.rate),
                'delivery_days': rate.delivery_days
            })
        
        return sorted(rates, key=lambda x: x['cost'])
        
    except Exception as e:
        print(f"EasyPost API Error: {e}")
        return []

def analyze_with_real_rates(df):
    """Analyze shipping with real EasyPost rates"""
    if not EASYPOST_AVAILABLE:
        print("\n⚠️  EasyPost integration not available")
        return
    
    print("\n=== REAL-TIME SHIPPING RATE ANALYSIS ===")
    
    total_potential_savings = 0
    sample_orders = df.head(5)  # Test with first 5 orders
    
    for _, order in sample_orders.iterrows():
        order_data = {
            'supplier_name': order['Supplier_Name'],
            'total_amount': order['Total_Amount']
        }
        
        real_rates = get_real_shipping_rates(order_data)
        if real_rates:
            best_rate = real_rates[0]
            current_cost = order['Shipping_Cost']
            potential_savings = max(0, current_cost - best_rate['cost'])
            total_potential_savings += potential_savings
            
            print(f"\n{order['Supplier_Name']}:")
            print(f"  Current: ${current_cost:.2f}")
            print(f"  Best Rate: ${best_rate['cost']:.2f} ({best_rate['carrier']} {best_rate['service']})")
            print(f"  Potential Savings: ${potential_savings:.2f}")
    
    print(f"\n💰 Total Potential Savings (sample): ${total_potential_savings:.2f}")
    
    # Extrapolate to full dataset
    if len(sample_orders) > 0:
        avg_savings_per_order = total_potential_savings / len(sample_orders)
        estimated_total_savings = avg_savings_per_order * len(df)
        print(f"📊 Estimated Total Savings: ${estimated_total_savings:,.2f}")

def main():
    """Main analysis function with EasyPost integration"""
    print("🚀 PROCUREMENT OPTIMIZATION ANALYSIS WITH EASYPOST")
    print("=" * 60)
    
    # Load data
    df = load_and_clean_data('/Users/isaiahrivera/Desktop/Summer_Camp/Freight_Project/Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv')
    
    print(f"📊 Loaded {len(df)} procurement records")
    print(f"📅 Date range: {df['PO_Date'].min()} to {df['PO_Date'].max()}")
    print(f"💰 Total spend: ${df['Total_Amount'].sum():,.2f}")
    print(f"🚚 Total shipping: ${df['Shipping_Cost'].sum():,.2f}")
    
    # Run analyses
    spend_analysis = analyze_historical_spend(df)
    shipping_analysis = predict_shipping_optimization(df)
    consolidation_analysis = recommend_consolidation_strategies(df)
    diversity_tracking = track_supplier_diversity(df)
    diverse_matching = identify_diverse_suppliers(df)
    
    # NEW: Real-time shipping analysis with EasyPost
    analyze_with_real_rates(df)
    
    recommendations = generate_recommendations(df)
    
    print(f"\n{'='*60}")
    print("✅ ANALYSIS COMPLETE WITH EASYPOST INTEGRATION")
    print("🚀 Run 'python easypost_shipping_optimizer.py' for full optimization")

if __name__ == "__main__":
    main()