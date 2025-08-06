#!/usr/bin/env python3
"""
Check All Data
Shows all data files and what each contains
"""

import pandas as pd
import os

def check_all_data_files():
    """Check all data files and show what each contains"""
    
    print("📁 ALL DATA FILES WE HAVE:")
    print("=" * 60)
    
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    for file in csv_files:
        size = os.path.getsize(file)
        print(f"\n📄 {file} ({size:,} bytes)")
        
        try:
            df = pd.read_csv(file)
            print(f"   📊 Records: {len(df):,}")
            print(f"   📋 Columns: {len(df.columns)}")
            print(f"   📅 Sample columns: {list(df.columns[:5])}")
            
            if 'Amount' in df.columns or 'Total_Amount' in df.columns:
                if 'Total_Amount' in df.columns:
                    total = df['Total_Amount'].sum()
                elif 'Amount' in df.columns:
                    total = df['Amount'].sum()
                print(f"   💰 Total Amount: ${total:,.2f}")
                
        except Exception as e:
            print(f"   ❌ Error reading: {e}")

def show_original_vs_cleaned():
    """Compare original vs cleaned data"""
    
    print("\n" + "=" * 60)
    print("🔄 ORIGINAL vs CLEANED DATA COMPARISON:")
    print("=" * 60)
    
    try:
        # Original data
        original_df = pd.read_csv('Original-Table 1.csv')
        print(f"\n📄 Original-Table 1.csv:")
        print(f"   📊 Records: {len(original_df):,}")
        print(f"   📋 Columns: {len(original_df.columns)}")
        print(f"   📅 Sample columns: {list(original_df.columns[:5])}")
        
        # Cleaned data
        cleaned_df = pd.read_csv('Cleaned_Procurement_Data.csv')
        print(f"\n📄 Cleaned_Procurement_Data.csv:")
        print(f"   📊 Records: {len(cleaned_df):,}")
        print(f"   📋 Columns: {len(cleaned_df.columns)}")
        print(f"   📅 Sample columns: {list(cleaned_df.columns[:5])}")
        print(f"   💰 Total Amount: ${cleaned_df['Total_Amount'].sum():,.2f}")
        
        # Synthetic data
        synthetic_df = pd.read_csv('Synthetic_Procurement_Data.csv')
        print(f"\n📄 Synthetic_Procurement_Data.csv:")
        print(f"   📊 Records: {len(synthetic_df):,}")
        print(f"   📋 Columns: {len(synthetic_df.columns)}")
        print(f"   📅 Sample columns: {list(synthetic_df.columns[:5])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_supporting_data():
    """Show what's in the supporting data files"""
    
    print("\n" + "=" * 60)
    print("📋 SUPPORTING DATA FILES:")
    print("=" * 60)
    
    supporting_files = [
        ('DVBE SB MB-Table 1.csv', 'Diversity certification data'),
        ('Sub Data-Table 1.csv', 'Subcontractor relationship data'),
        ('Totals-Table 1.csv', 'Spending totals by category')
    ]
    
    for filename, description in supporting_files:
        try:
            df = pd.read_csv(filename)
            print(f"\n📄 {filename}:")
            print(f"   📝 Description: {description}")
            print(f"   📊 Records: {len(df):,}")
            print(f"   📋 Columns: {len(df.columns)}")
            print(f"   📅 Columns: {list(df.columns)}")
            
        except Exception as e:
            print(f"\n📄 {filename}:")
            print(f"   ❌ Error reading: {e}")

def main():
    """Main function to show all data"""
    
    print("🎯 COMPLETE DATA INVENTORY")
    print("=" * 60)
    
    # Check all data files
    check_all_data_files()
    
    # Show original vs cleaned comparison
    show_original_vs_cleaned()
    
    # Show supporting data
    show_supporting_data()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print("=" * 60)
    print("✅ We have 6 data files total:")
    print("   • 1 main working dataset (Cleaned_Procurement_Data.csv)")
    print("   • 1 original source data (Original-Table 1.csv)")
    print("   • 1 enhanced testing data (Synthetic_Procurement_Data.csv)")
    print("   • 3 supporting data files (Sub, DVBE, Totals)")
    print()
    print("🎯 The 72 records you saw are the MAIN WORKING DATASET")
    print("📈 This is the optimized, analysis-ready data")
    print("📋 The other files contain additional context and original data")

if __name__ == "__main__":
    main() 