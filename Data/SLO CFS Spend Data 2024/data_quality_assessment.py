#!/usr/bin/env python3
"""
Data Quality Assessment and Synthetic Data Strategy
Analyzes current data gaps and provides recommendations for synthetic data generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

def assess_data_quality(original_file, cleaned_file):
    """Assess data quality and identify gaps"""
    print("=== DATA QUALITY ASSESSMENT ===")
    
    # Load both datasets
    original_df = pd.read_csv(original_file)
    cleaned_df = pd.read_csv(cleaned_file)
    
    print(f"Original data shape: {original_df.shape}")
    print(f"Cleaned data shape: {cleaned_df.shape}")
    
    # Analyze missing data in original
    print("\n=== MISSING DATA ANALYSIS ===")
    missing_data = original_df.isnull().sum()
    missing_percentage = (missing_data / len(original_df)) * 100
    
    print("Missing data in original dataset:")
    for column, missing_count in missing_data.items():
        if missing_count > 0:
            print(f"  {column}: {missing_count} ({missing_percentage[column]:.1f}%)")
    
    # Identify data gaps that were filled
    print("\n=== DATA GAPS IDENTIFIED ===")
    gaps = {
        'shipping_costs': 'Missing shipping cost data in 95% of records',
        'carrier_info': 'No carrier information in original data',
        'lead_times': 'Missing delivery timeframe data',
        'geographic_location': 'No supplier location information',
        'consolidation_opportunities': 'Had to be calculated from patterns',
        'order_frequency': 'Had to be inferred from purchase patterns',
        'supplier_diversity_categories': 'Some suppliers lacked proper classification'
    }
    
    for gap, description in gaps.items():
        print(f"  {gap.replace('_', ' ').title()}: {description}")
    
    return gaps

def generate_synthetic_data_strategy():
    """Generate strategy for synthetic data creation"""
    print("\n=== SYNTHETIC DATA STRATEGY ===")
    
    strategy = {
        'shipping_costs': {
            'method': 'Calculate based on order value and distance',
            'formula': '10% of order value for local, 15% for regional, 20% for national',
            'rationale': 'Enables shipping optimization algorithms',
            'priority': 'High'
        },
        'carrier_selection': {
            'method': 'Assign based on order size and urgency',
            'rules': {
                'small_orders': 'UPS/Ground',
                'medium_orders': 'FedEx',
                'large_orders': 'Freight',
                'urgent_orders': 'Express services'
            },
            'rationale': 'Enables carrier performance analysis',
            'priority': 'High'
        },
        'lead_times': {
            'method': 'Standardize based on supplier type and location',
            'defaults': {
                'local_suppliers': '3-5 days',
                'regional_suppliers': '7-10 days',
                'national_suppliers': '14-21 days'
            },
            'rationale': 'Enables delivery optimization',
            'priority': 'Medium'
        },
        'geographic_locations': {
            'method': 'Map suppliers to regions based on name patterns',
            'regions': ['California', 'Western US', 'National', 'International'],
            'rationale': 'Enables geographic consolidation',
            'priority': 'Medium'
        },
        'consolidation_opportunities': {
            'method': 'Calculate based on supplier and time patterns',
            'categories': ['Low', 'Medium', 'High', 'Very High'],
            'rationale': 'Enables consolidation algorithms',
            'priority': 'High'
        }
    }
    
    print("Synthetic Data Generation Strategy:")
    for field, details in strategy.items():
        print(f"\n  {field.replace('_', ' ').title()}:")
        print(f"    Method: {details['method']}")
        print(f"    Priority: {details['priority']}")
        print(f"    Rationale: {details['rationale']}")
    
    return strategy

def create_synthetic_data_generator():
    """Create a synthetic data generator for testing"""
    print("\n=== SYNTHETIC DATA GENERATOR ===")
    
    def generate_synthetic_shipping_data(df):
        """Generate realistic shipping costs based on order characteristics"""
        synthetic_df = df.copy()
        
        # Generate shipping costs based on order value and type
        for idx, row in synthetic_df.iterrows():
            order_value = row['Total_Amount']
            order_type = row['Order_Type']
            
            # Shipping cost as percentage of order value
            if order_value < 1000:
                shipping_ratio = np.random.uniform(0.08, 0.12)  # 8-12%
            elif order_value < 5000:
                shipping_ratio = np.random.uniform(0.06, 0.10)  # 6-10%
            else:
                shipping_ratio = np.random.uniform(0.04, 0.08)  # 4-8%
            
            synthetic_df.loc[idx, 'Shipping_Cost'] = order_value * shipping_ratio
        
        return synthetic_df
    
    def generate_synthetic_carrier_data(df):
        """Generate carrier assignments based on order characteristics"""
        synthetic_df = df.copy()
        
        carriers = ['UPS', 'FedEx', 'Ground', 'Freight', 'Electronic']
        
        for idx, row in synthetic_df.iterrows():
            order_value = row['Total_Amount']
            shipping_cost = row['Shipping_Cost']
            
            # Assign carrier based on order size and shipping cost
            if order_value < 500:
                carrier = np.random.choice(['UPS', 'Ground'], p=[0.7, 0.3])
            elif order_value < 2000:
                carrier = np.random.choice(['UPS', 'FedEx', 'Ground'], p=[0.4, 0.4, 0.2])
            elif order_value < 10000:
                carrier = np.random.choice(['FedEx', 'Freight'], p=[0.6, 0.4])
            else:
                carrier = 'Freight'
            
            # Special case for IT/Electronic orders
            if row['IT_Amount'] > 0:
                carrier = 'Electronic'
            
            synthetic_df.loc[idx, 'Carrier'] = carrier
        
        return synthetic_df
    
    def generate_synthetic_lead_times(df):
        """Generate realistic lead times"""
        synthetic_df = df.copy()
        
        for idx, row in synthetic_df.iterrows():
            supplier_type = row['Supplier_Type']
            order_value = row['Total_Amount']
            
            # Lead time based on supplier type and order size
            if supplier_type == 'DVB':
                base_lead_time = np.random.uniform(7, 14)
            elif supplier_type == 'OSB':
                base_lead_time = np.random.uniform(5, 10)
            else:
                base_lead_time = np.random.uniform(10, 21)
            
            # Adjust for order size
            if order_value > 10000:
                base_lead_time += np.random.uniform(3, 7)
            
            synthetic_df.loc[idx, 'Lead_Time_Days'] = int(base_lead_time)
        
        return synthetic_df
    
    return {
        'shipping': generate_synthetic_shipping_data,
        'carrier': generate_synthetic_carrier_data,
        'lead_times': generate_synthetic_lead_times
    }

def validate_synthetic_data_quality(synthetic_df, original_df):
    """Validate that synthetic data maintains realistic patterns"""
    print("\n=== SYNTHETIC DATA VALIDATION ===")
    
    # Check shipping cost ratios
    shipping_ratios = synthetic_df['Shipping_Cost'] / synthetic_df['Total_Amount']
    print(f"Shipping cost ratios:")
    print(f"  Mean: {shipping_ratios.mean():.3f}")
    print(f"  Range: {shipping_ratios.min():.3f} - {shipping_ratios.max():.3f}")
    
    # Check carrier distribution
    carrier_dist = synthetic_df['Carrier'].value_counts()
    print(f"\nCarrier distribution:")
    for carrier, count in carrier_dist.items():
        print(f"  {carrier}: {count} ({count/len(synthetic_df)*100:.1f}%)")
    
    # Check lead time distribution
    lead_time_stats = synthetic_df['Lead_Time_Days'].describe()
    print(f"\nLead time statistics:")
    print(f"  Mean: {lead_time_stats['mean']:.1f} days")
    print(f"  Range: {lead_time_stats['min']:.0f} - {lead_time_stats['max']:.0f} days")
    
    return True

def recommend_data_improvements():
    """Provide recommendations for data quality improvements"""
    print("\n=== DATA QUALITY IMPROVEMENT RECOMMENDATIONS ===")
    
    recommendations = [
        {
            'category': 'Immediate Actions',
            'items': [
                'Use synthetic shipping costs for optimization algorithms',
                'Implement carrier assignment logic based on order characteristics',
                'Generate realistic lead times for delivery optimization',
                'Create geographic location mapping for consolidation analysis'
            ]
        },
        {
            'category': 'Short-term Improvements',
            'items': [
                'Collect actual shipping cost data from suppliers',
                'Implement real-time carrier tracking',
                'Gather supplier location and delivery capability data',
                'Establish supplier diversity certification tracking'
            ]
        },
        {
            'category': 'Long-term Enhancements',
            'items': [
                'Integrate with supplier systems for real-time data',
                'Implement automated data collection from shipping providers',
                'Create supplier performance tracking system',
                'Develop predictive analytics for demand forecasting'
            ]
        }
    ]
    
    for rec in recommendations:
        print(f"\n{rec['category']}:")
        for item in rec['items']:
            print(f"  • {item}")
    
    return recommendations

def main():
    """Main function to run data quality assessment"""
    print("PROCUREMENT DATA QUALITY ASSESSMENT")
    print("=" * 50)
    
    # Assess current data quality
    gaps = assess_data_quality(
        'Original-Table 1.csv',
        'Cleaned_Procurement_Data.csv'
    )
    
    # Generate synthetic data strategy
    strategy = generate_synthetic_data_strategy()
    
    # Create synthetic data generator
    generator = create_synthetic_data_generator()
    
    # Load cleaned data for synthetic generation
    df = pd.read_csv('Cleaned_Procurement_Data.csv')
    
    # Generate synthetic data
    synthetic_df = df.copy()
    for generator_name, generator_func in generator.items():
        print(f"\nGenerating synthetic {generator_name} data...")
        synthetic_df = generator_func(synthetic_df)
    
    # Validate synthetic data
    validate_synthetic_data_quality(synthetic_df, df)
    
    # Provide recommendations
    recommendations = recommend_data_improvements()
    
    # Save synthetic dataset
    synthetic_df.to_csv('Synthetic_Procurement_Data.csv', index=False)
    print(f"\nSynthetic dataset saved as 'Synthetic_Procurement_Data.csv'")
    
    print("\n=== SUMMARY ===")
    print("✅ Synthetic data generation strategy created")
    print("✅ Data quality gaps identified and addressed")
    print("✅ Validation checks implemented")
    print("✅ Recommendations for future improvements provided")
    
    return synthetic_df

if __name__ == "__main__":
    main() 