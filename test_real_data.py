#!/usr/bin/env python3
"""
Test script to verify all components work with real data
"""

from shipping_optimizer import ShippingOptimizer
from consolidation_optimizer import ConsolidationOptimizer
from supplier_diversity_tracker import SupplierDiversityTracker
import pandas as pd

def test_shipping_optimizer():
    print("=== SHIPPING OPTIMIZER REAL DATA TEST ===")
    optimizer = ShippingOptimizer()
    print(f"Data loaded: {len(optimizer.df)} records")
    print(f"Carriers in data: {list(optimizer.df['Carrier'].unique())}")
    print(f"Shipping costs range: ${optimizer.df['Shipping_Cost'].min():.2f} - ${optimizer.df['Shipping_Cost'].max():.2f}")
    
    # Test carrier performance with real data
    performance = optimizer.get_carrier_performance_summary()
    print(f"\nReal carrier performance:")
    for carrier, stats in performance.items():
        print(f"  {carrier}: {stats['total_shipments']} shipments, avg ${stats['avg_cost']:.2f}")
    
    # Test recommendations with real data
    recommendations = optimizer.get_carrier_recommendations(5000)
    print(f"\nReal recommendations for $5000 order:")
    for rec in recommendations[:3]:
        print(f"  {rec['carrier']}: ${rec['predicted_cost']:.2f}")
    
    return len(optimizer.df) > 0

def test_consolidation_optimizer():
    print("\n=== CONSOLIDATION OPTIMIZER REAL DATA TEST ===")
    optimizer = ConsolidationOptimizer()
    print(f"Data loaded: {len(optimizer.df)} records")
    
    # Check consolidation opportunity field
    consolidation_levels = optimizer.df['Consolidation_Opportunity'].value_counts()
    print(f"Consolidation levels in data: {consolidation_levels.to_dict()}")
    
    # Test real consolidation opportunities
    opportunities = optimizer.find_consolidation_opportunities()
    print(f"Real consolidation opportunities found: {len(opportunities)}")
    
    if opportunities:
        print("Top 3 real opportunities:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"  {i}. {opp['supplier']}: ${opp['potential_savings']:.2f} savings")
    
    return len(opportunities) > 0

def test_diversity_tracker():
    print("\n=== SUPPLIER DIVERSITY TRACKER REAL DATA TEST ===")
    tracker = SupplierDiversityTracker()
    print(f"Data loaded: {len(tracker.df)} records")
    
    # Test diversity performance
    summary = tracker.get_diversity_performance_summary()
    print(f"Diversity categories: {list(summary['diversity_breakdown'].keys())}")
    print(f"Total diversity spend: {summary['diversity_spend_percentage']:.1f}%")
    
    # Test diverse supplier identification
    suppliers = tracker.identify_diverse_suppliers()
    print(f"Diverse suppliers identified: {len(suppliers)}")
    
    if suppliers:
        print("Top 3 diverse suppliers:")
        for i, supplier in enumerate(suppliers[:3], 1):
            print(f"  {i}. {supplier['supplier_name']} ({supplier['diversity_category']}): ${supplier['total_spend']:,.2f}")
    
    # Test goal tracking
    goals = tracker.track_diversity_goals(25.0)
    print(f"Diversity goal status: {goals['goal_status']} ({goals['current_percentage']:.1f}% vs 25% target)")
    
    return len(suppliers) > 0

def test_data_fields():
    print("\n=== DATA FIELD VERIFICATION ===")
    df = pd.read_csv('Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv')
    
    required_fields = [
        'Shipping_Cost', 'Carrier', 'Consolidation_Opportunity', 
        'Supplier_Diversity_Category', 'Total_Amount', 'Lead_Time_Days'
    ]
    
    for field in required_fields:
        if field in df.columns:
            non_null = df[field].notna().sum()
            unique_vals = df[field].nunique()
            print(f"✅ {field}: {non_null}/{len(df)} non-null values, {unique_vals} unique")
        else:
            print(f"❌ {field}: MISSING")
    
    return all(field in df.columns for field in required_fields)

if __name__ == "__main__":
    print("🧪 TESTING ALL COMPONENTS WITH REAL DATA")
    print("=" * 50)
    
    # Test each component
    shipping_works = test_shipping_optimizer()
    consolidation_works = test_consolidation_optimizer()
    diversity_works = test_diversity_tracker()
    data_complete = test_data_fields()
    
    print(f"\n📊 RESULTS:")
    print(f"Shipping Optimizer: {'✅ WORKING' if shipping_works else '❌ FAILED'}")
    print(f"Consolidation Optimizer: {'✅ WORKING' if consolidation_works else '❌ FAILED'}")
    print(f"Diversity Tracker: {'✅ WORKING' if diversity_works else '❌ FAILED'}")
    print(f"Data Fields Complete: {'✅ YES' if data_complete else '❌ NO'}")
    
    all_working = shipping_works and consolidation_works and diversity_works and data_complete
    print(f"\n🎯 ALL CORE FEATURES: {'✅ COMPLETE' if all_working else '❌ INCOMPLETE'}")