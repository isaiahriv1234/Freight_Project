#!/usr/bin/env python3
"""
Automatic Diverse Supplier Identification and Matching System
"""

import pandas as pd
import requests
import re
from fuzzywuzzy import fuzz

class DiverseSupplierMatcher:
    def __init__(self):
        # Government diversity databases (examples)
        self.diversity_databases = {
            'sba_certify': 'https://certify.sba.gov/api/search',
            'sam_gov': 'https://api.sam.gov/entity-information/v3/entities',
            'california_dgs': 'https://www.dgs.ca.gov/PD/Resources/Supplier-Diversity-Program'
        }
        
        # Diversity keywords for name matching
        self.diversity_keywords = {
            'DVBE': ['veteran', 'disabled', 'dvbe', 'service disabled'],
            'WOB': ['women', 'woman', 'female', 'wob', 'wbe'],
            'MBE': ['minority', 'hispanic', 'latino', 'african', 'asian', 'mbe'],
            'SDB': ['small', 'disadvantaged', 'sdb', 'small business'],
            'HUB': ['hub', 'historically underutilized']
        }
    
    def identify_supplier_diversity(self, supplier_name, tax_id=None):
        """Automatically identify supplier diversity status"""
        
        # Method 1: Database lookup
        diversity_status = self.lookup_government_databases(supplier_name, tax_id)
        if diversity_status:
            return diversity_status
        
        # Method 2: Name pattern matching
        diversity_status = self.match_diversity_keywords(supplier_name)
        if diversity_status:
            return diversity_status
        
        # Method 3: Business registration analysis
        diversity_status = self.analyze_business_registration(supplier_name)
        if diversity_status:
            return diversity_status
        
        return 'Unknown'
    
    def lookup_government_databases(self, supplier_name, tax_id=None):
        """Check government diversity certification databases"""
        try:
            # SBA Certify database lookup
            if tax_id:
                response = requests.get(f"https://certify.sba.gov/api/search?duns={tax_id}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('certifications'):
                        return self.parse_certifications(data['certifications'])
            
            # SAM.gov lookup by name
            response = requests.get(f"https://api.sam.gov/entity-information/v3/entities?entityName={supplier_name}")
            if response.status_code == 200:
                data = response.json()
                return self.parse_sam_data(data)
                
        except Exception as e:
            print(f"Database lookup failed: {e}")
        
        return None
    
    def match_diversity_keywords(self, supplier_name):
        """Match supplier name against diversity keywords"""
        name_lower = supplier_name.lower()
        
        for category, keywords in self.diversity_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category
        
        return None
    
    def analyze_business_registration(self, supplier_name):
        """Analyze business name patterns for diversity indicators"""
        
        # Common diversity business name patterns
        patterns = {
            'DVBE': r'(veteran|disabled|dvbe)',
            'WOB': r'(women|woman|female)',
            'MBE': r'(minority|hispanic|latino|african|asian)',
            'SDB': r'(small.*business|disadvantaged)'
        }
        
        for category, pattern in patterns.items():
            if re.search(pattern, supplier_name, re.IGNORECASE):
                return category
        
        return None
    
    def match_similar_suppliers(self, new_supplier, existing_suppliers_df):
        """Find similar suppliers for diversity matching"""
        
        matches = []
        for _, row in existing_suppliers_df.iterrows():
            similarity = fuzz.ratio(new_supplier.lower(), row['supplier_name'].lower())
            if similarity > 80:  # 80% similarity threshold
                matches.append({
                    'supplier': row['supplier_name'],
                    'diversity_category': row['diversity_category'],
                    'similarity': similarity
                })
        
        return sorted(matches, key=lambda x: x['similarity'], reverse=True)
    
    def update_supplier_diversity(self, df):
        """Update entire dataset with automatic diversity identification"""
        
        updated_df = df.copy()
        
        for idx, row in updated_df.iterrows():
            if pd.isna(row['diversity_category']) or row['diversity_category'] == 'Unknown':
                # Automatically identify diversity status
                diversity_status = self.identify_supplier_diversity(row['supplier_name'])
                updated_df.at[idx, 'diversity_category'] = diversity_status
                updated_df.at[idx, 'identification_method'] = 'automatic'
        
        return updated_df
    
    def generate_diversity_recommendations(self, df):
        """Generate recommendations for increasing diversity spend"""
        
        recommendations = []
        
        # Analyze current diversity distribution
        diversity_summary = df.groupby('diversity_category').agg({
            'total_amount': 'sum',
            'supplier_name': 'nunique'
        }).reset_index()
        
        total_spend = df['total_amount'].sum()
        
        for _, row in diversity_summary.iterrows():
            category = row['diversity_category']
            spend = row['total_amount']
            percentage = (spend / total_spend) * 100
            
            if percentage < 10:  # Less than 10% spend
                recommendations.append({
                    'category': category,
                    'current_spend': spend,
                    'current_percentage': percentage,
                    'recommendation': f'Increase {category} supplier engagement',
                    'target_percentage': 15
                })
        
        return recommendations

def main():
    """Demonstrate automatic diverse supplier matching"""
    
    # Load existing data
    df = pd.read_csv('master_shipping_dataset_20250807_002133.csv')
    
    # Initialize matcher
    matcher = DiverseSupplierMatcher()
    
    # Update diversity classifications
    updated_df = matcher.update_supplier_diversity(df)
    
    # Generate recommendations
    recommendations = matcher.generate_diversity_recommendations(updated_df)
    
    # Save results
    updated_df.to_csv('suppliers_with_auto_diversity.csv', index=False)
    
    print("🎯 AUTOMATIC DIVERSE SUPPLIER MATCHING COMPLETE")
    print(f"📊 Updated {len(updated_df)} supplier records")
    print(f"💡 Generated {len(recommendations)} diversity recommendations")
    
    return updated_df, recommendations

if __name__ == "__main__":
    main()