#!/usr/bin/env python3
"""
How to Use This Optimized Data
Demonstrates all the ways we can leverage the cleaned data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_data():
    """Load the optimized data"""
    df = pd.read_csv('Cleaned_Procurement_Data.csv')
    df['PO_Date'] = pd.to_datetime(df['PO_Date'])
    return df

def demonstrate_historical_spend_analysis(df):
    """Show historical spend analysis capabilities"""
    print("\n📊 HISTORICAL SPEND ANALYSIS:")
    print("=" * 50)
    
    # Total spend analysis
    total_spend = df['Total_Amount'].sum()
    avg_order = df['Total_Amount'].mean()
    print(f"💰 Total Spend: ${total_spend:,.2f}")
    print(f"📦 Average Order: ${avg_order:,.2f}")
    print(f"📈 Number of Orders: {len(df)}")
    
    # Monthly trends
    monthly_spend = df.groupby(df['PO_Date'].dt.to_period('M'))['Total_Amount'].sum()
    print(f"\n📅 Monthly Spend Trends:")
    for month, spend in monthly_spend.items():
        print(f"  {month}: ${spend:,.2f}")
    
    # Top suppliers
    top_suppliers = df.groupby('Supplier_Name')['Total_Amount'].sum().sort_values(ascending=False)
    print(f"\n🏆 Top Suppliers by Spend:")
    for supplier, spend in top_suppliers.head(3).items():
        print(f"  {supplier}: ${spend:,.2f}")

def demonstrate_shipping_optimization(df):
    """Show shipping optimization capabilities"""
    print("\n🚚 SHIPPING OPTIMIZATION:")
    print("=" * 50)
    
    # Shipping cost analysis
    total_shipping = df['Shipping_Cost'].sum()
    shipping_ratio = (total_shipping / df['Total_Amount'].sum()) * 100
    print(f"📦 Total Shipping Cost: ${total_shipping:,.2f}")
    print(f"📊 Shipping Cost Ratio: {shipping_ratio:.1f}%")
    
    # Carrier performance
    carrier_analysis = df.groupby('Carrier').agg({
        'Shipping_Cost': ['count', 'sum', 'mean'],
        'Total_Amount': 'sum'
    }).round(2)
    print(f"\n🚛 Carrier Performance:")
    for carrier in carrier_analysis.index:
        count = carrier_analysis.loc[carrier, ('Shipping_Cost', 'count')]
        total_cost = carrier_analysis.loc[carrier, ('Shipping_Cost', 'sum')]
        avg_cost = carrier_analysis.loc[carrier, ('Shipping_Cost', 'mean')]
        print(f"  {carrier}: {count} orders, ${total_cost:,.2f} total, ${avg_cost:,.2f} avg")

def demonstrate_consolidation_opportunities(df):
    """Show consolidation opportunities"""
    print("\n📦 CONSOLIDATION OPPORTUNITIES:")
    print("=" * 50)
    
    # Find orders that could be consolidated
    df['Week'] = df['PO_Date'].dt.to_period('W')
    weekly_orders = df.groupby('Week').agg({
        'Total_Amount': 'sum',
        'Shipping_Cost': 'sum',
        'Supplier_Name': 'count'
    }).rename(columns={'Supplier_Name': 'Order_Count'})
    
    # Identify consolidation opportunities
    consolidation_opportunities = weekly_orders[weekly_orders['Order_Count'] > 1]
    print(f"📅 Weekly Consolidation Opportunities:")
    for week, data in consolidation_opportunities.head(5).iterrows():
        potential_savings = data['Shipping_Cost'] * 0.3  # 30% savings estimate
        print(f"  Week {week}: {data['Order_Count']} orders, ${data['Total_Amount']:,.2f} spend")
        print(f"    Potential savings: ${potential_savings:,.2f}")
    
    # Geographic consolidation
    geo_consolidation = df.groupby('Geographic_Location').agg({
        'Total_Amount': 'sum',
        'Shipping_Cost': 'sum',
        'Supplier_Name': 'nunique'
    })
    print(f"\n🌍 Geographic Consolidation:")
    for location, data in geo_consolidation.iterrows():
        print(f"  {location}: ${data['Total_Amount']:,.2f} spend, {data['Supplier_Name']} suppliers")

def demonstrate_supplier_diversity_tracking(df):
    """Show supplier diversity tracking"""
    print("\n🏢 SUPPLIER DIVERSITY TRACKING:")
    print("=" * 50)
    
    # Diversity metrics
    diversity_counts = df['Supplier_Diversity_Category'].value_counts()
    total_orders = len(df)
    
    print(f"📊 Diversity Distribution:")
    for category, count in diversity_counts.items():
        percentage = (count / total_orders) * 100
        print(f"  {category}: {count} orders ({percentage:.1f}%)")
    
    # Spend by diversity category
    diversity_spend = df.groupby('Supplier_Diversity_Category')['Total_Amount'].sum()
    print(f"\n💰 Spend by Diversity Category:")
    for category, spend in diversity_spend.items():
        percentage = (spend / df['Total_Amount'].sum()) * 100
        print(f"  {category}: ${spend:,.2f} ({percentage:.1f}%)")

def demonstrate_real_time_dashboard(df):
    """Show real-time dashboard capabilities"""
    print("\n📊 REAL-TIME DASHBOARD CAPABILITIES:")
    print("=" * 50)
    
    # KPIs
    current_month = datetime.now().replace(day=1)
    recent_orders = df[df['PO_Date'] >= current_month - timedelta(days=30)]
    
    print(f"📈 Key Performance Indicators:")
    print(f"  Monthly Spend: ${recent_orders['Total_Amount'].sum():,.2f}")
    print(f"  Orders This Month: {len(recent_orders)}")
    print(f"  Average Order Value: ${recent_orders['Total_Amount'].mean():,.2f}")
    print(f"  Shipping Cost Ratio: {(recent_orders['Shipping_Cost'].sum() / recent_orders['Total_Amount'].sum()) * 100:.1f}%")
    
    # Alerts
    print(f"\n🚨 Automated Alerts:")
    high_cost_orders = df[df['Shipping_Cost'] / df['Total_Amount'] > 0.15]
    if len(high_cost_orders) > 0:
        print(f"  ⚠️  {len(high_cost_orders)} orders with >15% shipping cost ratio")
    
    consolidation_alerts = df.groupby('Week').filter(lambda x: len(x) > 2)
    if len(consolidation_alerts) > 0:
        print(f"  📦 {len(consolidation_alerts)} orders eligible for consolidation")

def demonstrate_predictive_analytics(df):
    """Show predictive analytics capabilities"""
    print("\n🔮 PREDICTIVE ANALYTICS:")
    print("=" * 50)
    
    # Predict future spend based on trends
    monthly_trend = df.groupby(df['PO_Date'].dt.to_period('M'))['Total_Amount'].sum()
    if len(monthly_trend) >= 2:
        growth_rate = (monthly_trend.iloc[-1] - monthly_trend.iloc[-2]) / monthly_trend.iloc[-2] * 100
        predicted_next_month = monthly_trend.iloc[-1] * (1 + growth_rate/100)
        print(f"📈 Predicted Next Month Spend: ${predicted_next_month:,.2f}")
    
    # Predict optimal shipping costs
    avg_shipping_ratio = (df['Shipping_Cost'].sum() / df['Total_Amount'].sum()) * 100
    print(f"📦 Optimal Shipping Cost Ratio: {avg_shipping_ratio:.1f}%")
    
    # Predict consolidation savings
    weekly_orders = df.groupby(df['PO_Date'].dt.to_period('W')).size()
    consolidation_weeks = weekly_orders[weekly_orders > 1]
    potential_savings = consolidation_weeks.sum() * 50  # $50 per consolidated order
    print(f"💰 Predicted Consolidation Savings: ${potential_savings:,.2f}")

def main():
    """Main function to demonstrate all capabilities"""
    print("🚀 HOW TO USE THIS OPTIMIZED DATA")
    print("=" * 60)
    
    # Load data
    df = load_data()
    
    # Demonstrate all capabilities
    demonstrate_historical_spend_analysis(df)
    demonstrate_shipping_optimization(df)
    demonstrate_consolidation_opportunities(df)
    demonstrate_supplier_diversity_tracking(df)
    demonstrate_real_time_dashboard(df)
    demonstrate_predictive_analytics(df)
    
    print("\n🎯 SUMMARY OF USAGE OPTIONS:")
    print("=" * 60)
    print("1. 📊 Run the real-time dashboard: python dashboard_config.py")
    print("2. 🔍 Analyze historical trends and patterns")
    print("3. 🚚 Optimize shipping costs and carrier selection")
    print("4. 📦 Identify consolidation opportunities")
    print("5. 🏢 Track supplier diversity performance")
    print("6. 🔮 Predict future costs and savings")
    print("7. 📈 Generate automated reports and alerts")
    print("8. 💰 Calculate ROI and cost savings")

if __name__ == "__main__":
    main() 