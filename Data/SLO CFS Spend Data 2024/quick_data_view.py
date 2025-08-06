#!/usr/bin/env python3
"""
Quick Data View
Simple table view of the optimized data for team presentation
"""

import pandas as pd

def show_quick_table():
    """Show a clean, simple table of the optimized data"""
    
    print("📊 QUICK DATA VIEW - OPTIMIZED PROCUREMENT DATA")
    print("=" * 100)
    
    try:
        # Load data
        df = pd.read_csv('Cleaned_Procurement_Data.csv')
        df['PO_Date'] = pd.to_datetime(df['PO_Date'])
        
        # Create a clean display table
        display_df = df[['PO_Date', 'Supplier_Name', 'Total_Amount', 'Shipping_Cost', 'Carrier', 'Supplier_Diversity_Category']].copy()
        
        # Format the data for display
        display_df['PO_Date'] = display_df['PO_Date'].dt.strftime('%Y-%m-%d')
        display_df['Total_Amount'] = display_df['Total_Amount'].apply(lambda x: f"${x:,.2f}")
        display_df['Shipping_Cost'] = display_df['Shipping_Cost'].apply(lambda x: f"${x:,.2f}")
        
        # Rename columns for clarity
        display_df.columns = ['Date', 'Supplier', 'Total Amount', 'Shipping Cost', 'Carrier', 'Diversity']
        
        print(f"📈 Total Records: {len(df)}")
        print(f"💰 Total Spend: ${df['Total_Amount'].sum():,.2f}")
        print(f"🚚 Total Shipping: ${df['Shipping_Cost'].sum():,.2f}")
        print(f"🏢 Suppliers: {df['Supplier_Name'].nunique()}")
        print(f"📦 Carriers: {df['Carrier'].nunique()}")
        print()
        
        # Show first 15 records in a clean table
        print("📋 SAMPLE DATA (First 15 Records):")
        print("-" * 100)
        print(display_df.head(15).to_string(index=False))
        
        print("\n" + "=" * 100)
        print("📊 SUMMARY BY SUPPLIER:")
        print("-" * 100)
        
        # Supplier summary
        supplier_summary = df.groupby('Supplier_Name').agg({
            'Total_Amount': 'sum',
            'Shipping_Cost': 'sum',
            'PO_Date': 'count'
        }).round(2)
        supplier_summary.columns = ['Total Spend', 'Total Shipping', 'Orders']
        supplier_summary['Total Spend'] = supplier_summary['Total Spend'].apply(lambda x: f"${x:,.2f}")
        supplier_summary['Total Shipping'] = supplier_summary['Total Shipping'].apply(lambda x: f"${x:,.2f}")
        print(supplier_summary.to_string())
        
        print("\n" + "=" * 100)
        print("🚚 SUMMARY BY CARRIER:")
        print("-" * 100)
        
        # Carrier summary
        carrier_summary = df.groupby('Carrier').agg({
            'Total_Amount': 'sum',
            'Shipping_Cost': 'sum',
            'PO_Date': 'count'
        }).round(2)
        carrier_summary.columns = ['Total Spend', 'Total Shipping', 'Orders']
        carrier_summary['Total Spend'] = carrier_summary['Total Spend'].apply(lambda x: f"${x:,.2f}")
        carrier_summary['Total Shipping'] = carrier_summary['Total Shipping'].apply(lambda x: f"${x:,.2f}")
        print(carrier_summary.to_string())
        
        print("\n" + "=" * 100)
        print("🏢 DIVERSITY SUMMARY:")
        print("-" * 100)
        
        # Diversity summary
        diversity_summary = df.groupby('Supplier_Diversity_Category').agg({
            'Total_Amount': 'sum',
            'PO_Date': 'count'
        }).round(2)
        diversity_summary.columns = ['Total Spend', 'Orders']
        diversity_summary['Total Spend'] = diversity_summary['Total Spend'].apply(lambda x: f"${x:,.2f}")
        print(diversity_summary.to_string())
        
        print("\n" + "=" * 100)
        print("✅ DATA READY FOR:")
        print("   • Historical spend analysis")
        print("   • Shipping cost optimization") 
        print("   • Consolidation recommendations")
        print("   • Supplier diversity tracking")
        print("   • Real-time dashboard development")
        print("   • Automated procurement system")
        print("=" * 100)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    show_quick_table() 