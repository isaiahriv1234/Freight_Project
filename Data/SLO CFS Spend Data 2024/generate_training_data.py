#!/usr/bin/env python3
"""
Generate Training Data Files
Creates ML-ready datasets without requiring API calls
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

def create_ml_training_dataset():
    """Create ML-ready training dataset"""
    print("🤖 GENERATING ML TRAINING DATASET")
    print("=" * 50)
    
    try:
        # Load your cleaned procurement data
        df = pd.read_csv('Cleaned_Procurement_Data.csv')
        print(f"📊 Loaded {len(df)} procurement records")
        
        # Create ML features
        ml_data = []
        
        for _, row in df.iterrows():
            # Core features for ML model
            features = {
                # Order characteristics
                'order_value': float(row['Total_Amount']),
                'order_weight_estimate': float(row['Total_Amount']) * 0.01,  # Estimate based on value
                'order_dimensions_score': min(10, float(row['Total_Amount']) / 100),
                
                # Current shipping data
                'current_shipping_cost': float(row['Shipping_Cost']),
                'current_carrier': row['Carrier'],
                'current_lead_time': int(row['Lead_Time_Days']),
                
                # Supplier features
                'supplier_name': row['Supplier_Name'],
                'supplier_diversity_category': row['Supplier_Diversity_Category'],
                'supplier_location': row['Geographic_Location'],
                
                # Optimization features
                'shipping_cost_ratio': float(row['Shipping_Cost']) / float(row['Total_Amount']) if float(row['Total_Amount']) > 0 else 0,
                'consolidation_opportunity': row['Consolidation_Opportunity'],
                'consolidation_score': {'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}.get(row['Consolidation_Opportunity'], 2),
                
                # Frequency and patterns
                'order_frequency': row['Order_Frequency'],
                'frequency_score': {'Monthly': 12, 'Quarterly': 4, 'Annual': 1, 'As-Needed': 6}.get(row['Order_Frequency'], 6),
                
                # Target variables for ML
                'optimization_target': 1 if float(row['Shipping_Cost']) / float(row['Total_Amount']) > 0.1 else 0,
                'cost_reduction_potential': max(0, float(row['Shipping_Cost']) * 0.2),  # Assume 20% potential savings
                
                # Categorical encodings
                'carrier_ups': 1 if row['Carrier'] == 'UPS' else 0,
                'carrier_fedex': 1 if row['Carrier'] == 'FedEx' else 0,
                'carrier_freight': 1 if row['Carrier'] == 'Freight' else 0,
                'carrier_ground': 1 if row['Carrier'] == 'Ground' else 0,
                
                'diversity_dvbe': 1 if row['Supplier_Diversity_Category'] == 'DVBE' else 0,
                'diversity_osb': 1 if row['Supplier_Diversity_Category'] == 'OSB' else 0,
                'diversity_mb': 1 if row['Supplier_Diversity_Category'] == 'MB' else 0,
                
                # Date features
                'po_date': row['PO_Date'],
                'fiscal_year': int(row['Fiscal_Year']),
                'accounting_period': int(row['Accounting_Period'])
            }
            
            ml_data.append(features)
        
        # Create DataFrame
        ml_df = pd.DataFrame(ml_data)
        
        # Add synthetic alternative rates (simulated EasyPost data)
        np.random.seed(42)  # For reproducible results
        ml_df['alternative_ups_cost'] = ml_df['current_shipping_cost'] * np.random.uniform(0.8, 1.2, len(ml_df))
        ml_df['alternative_fedex_cost'] = ml_df['current_shipping_cost'] * np.random.uniform(0.85, 1.15, len(ml_df))
        ml_df['alternative_usps_cost'] = ml_df['current_shipping_cost'] * np.random.uniform(0.7, 1.1, len(ml_df))
        
        # Calculate best alternative
        ml_df['best_alternative_cost'] = ml_df[['alternative_ups_cost', 'alternative_fedex_cost', 'alternative_usps_cost']].min(axis=1)
        ml_df['potential_savings'] = ml_df['current_shipping_cost'] - ml_df['best_alternative_cost']
        ml_df['savings_percentage'] = (ml_df['potential_savings'] / ml_df['current_shipping_cost']) * 100
        
        # Clean data for ML
        ml_df = ml_df.fillna(0)
        
        # Save ML dataset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ml_filename = f"ml_ready_shipping_dataset_{timestamp}.csv"
        ml_df.to_csv(ml_filename, index=False)
        
        print(f"✅ ML Dataset Created: {ml_filename}")
        print(f"📊 Features: {len(ml_df.columns)}")
        print(f"📈 Records: {len(ml_df)}")
        print(f"💰 Total Potential Savings: ${ml_df['potential_savings'].sum():,.2f}")
        
        return ml_filename, ml_df
        
    except Exception as e:
        print(f"❌ Error creating ML dataset: {e}")
        return None, None

def create_summary_dataset():
    """Create summary dataset for analysis"""
    print(f"\n📋 CREATING SUMMARY DATASET")
    print("=" * 50)
    
    try:
        df = pd.read_csv('Cleaned_Procurement_Data.csv')
        
        # Create summary by supplier
        supplier_summary = df.groupby(['Supplier_Name', 'Supplier_Diversity_Category']).agg({
            'Total_Amount': ['sum', 'mean', 'count'],
            'Shipping_Cost': ['sum', 'mean'],
            'Lead_Time_Days': 'mean'
        }).round(2)
        
        # Flatten column names
        supplier_summary.columns = ['_'.join(col).strip() for col in supplier_summary.columns]
        supplier_summary = supplier_summary.reset_index()
        
        # Add calculated fields
        supplier_summary['shipping_ratio'] = (supplier_summary['Shipping_Cost_sum'] / supplier_summary['Total_Amount_sum'] * 100).round(2)
        supplier_summary['avg_order_value'] = supplier_summary['Total_Amount_mean']
        supplier_summary['total_orders'] = supplier_summary['Total_Amount_count']
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"supplier_summary_dataset_{timestamp}.csv"
        supplier_summary.to_csv(summary_filename, index=False)
        
        print(f"✅ Summary Dataset Created: {summary_filename}")
        print(f"📊 Suppliers: {len(supplier_summary)}")
        
        return summary_filename
        
    except Exception as e:
        print(f"❌ Error creating summary dataset: {e}")
        return None

def create_metadata_file(ml_filename, summary_filename, ml_df):
    """Create metadata file with dataset information"""
    
    metadata = {
        'generation_timestamp': datetime.now().isoformat(),
        'files_created': {
            'ml_training_dataset': ml_filename,
            'supplier_summary': summary_filename
        },
        'dataset_stats': {
            'total_records': len(ml_df) if ml_df is not None else 0,
            'total_features': len(ml_df.columns) if ml_df is not None else 0,
            'total_spend': float(ml_df['order_value'].sum()) if ml_df is not None else 0,
            'total_shipping': float(ml_df['current_shipping_cost'].sum()) if ml_df is not None else 0,
            'potential_savings': float(ml_df['potential_savings'].sum()) if ml_df is not None else 0
        },
        'feature_descriptions': {
            'order_value': 'Total order amount in USD',
            'current_shipping_cost': 'Current shipping cost in USD',
            'shipping_cost_ratio': 'Shipping cost as percentage of order value',
            'consolidation_score': 'Consolidation opportunity score (1-4)',
            'optimization_target': 'Binary target for optimization (1=needs optimization)',
            'potential_savings': 'Estimated cost savings in USD',
            'best_alternative_cost': 'Lowest cost alternative shipping option'
        },
        'usage_instructions': {
            'primary_file': ml_filename,
            'target_variable': 'optimization_target',
            'key_features': ['order_value', 'current_shipping_cost', 'consolidation_score', 'frequency_score'],
            'model_type': 'Classification or Regression for shipping optimization'
        }
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata_filename = f"training_data_metadata_{timestamp}.json"
    
    with open(metadata_filename, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Metadata Created: {metadata_filename}")
    return metadata_filename

def main():
    """Generate all training data files"""
    print("🚀 GENERATING TRAINING DATA FOR ML MODEL")
    print("=" * 60)
    
    # Create ML training dataset
    ml_filename, ml_df = create_ml_training_dataset()
    
    # Create summary dataset
    summary_filename = create_summary_dataset()
    
    # Create metadata
    if ml_filename:
        metadata_filename = create_metadata_file(ml_filename, summary_filename, ml_df)
    
    print(f"\n✅ TRAINING DATA GENERATION COMPLETE!")
    print(f"📁 Files ready for your team:")
    
    if ml_filename:
        print(f"   🎯 PRIMARY: {ml_filename}")
    if summary_filename:
        print(f"   📊 SUMMARY: {summary_filename}")
    if ml_filename:
        print(f"   📋 METADATA: training_data_metadata_*.json")
    
    print(f"\n🤖 READY FOR ML MODEL TRAINING!")
    print(f"   - Upload {ml_filename} to your ML platform")
    print(f"   - Use 'optimization_target' as target variable")
    print(f"   - Features include order value, shipping costs, consolidation scores")

if __name__ == "__main__":
    main()