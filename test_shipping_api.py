#!/usr/bin/env python3
"""
Test script for shipping optimization API endpoints
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread

def test_api_endpoints():
    """Test the shipping optimization API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Test shipping recommendations
        print("🧪 Testing shipping recommendations...")
        response = requests.get(f"{base_url}/api/shipping-recommendations?order_value=5000&weight_category=medium&urgency=standard")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {len(data)} carrier recommendations")
            if data:
                print(f"   Top recommendation: {data[0]['carrier']} - ${data[0]['predicted_cost']}")
        else:
            print(f"❌ Failed: {response.status_code}")
        
        # Test carrier performance
        print("\n🧪 Testing carrier performance...")
        response = requests.get(f"{base_url}/api/carrier-performance")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got performance data for {len(data)} carriers")
        else:
            print(f"❌ Failed: {response.status_code}")
        
        # Test shipping savings
        print("\n🧪 Testing shipping savings...")
        response = requests.get(f"{base_url}/api/shipping-savings")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Potential savings: ${data['potential_savings']:.2f} ({data['savings_percentage']:.1f}%)")
        else:
            print(f"❌ Failed: {response.status_code}")
        
        # Test consolidation opportunities
        print("\n🧪 Testing consolidation opportunities...")
        response = requests.get(f"{base_url}/api/consolidation-summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_opportunities']} consolidation opportunities")
            print(f"   Potential savings: ${data['total_potential_savings']:.2f}")
        else:
            print(f"❌ Failed: {response.status_code}")
        
        # Test consolidation strategy
        print("\n🧪 Testing consolidation strategy...")
        response = requests.get(f"{base_url}/api/consolidation-strategy")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {len(data['recommendations'])} strategy recommendations")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Shipping Optimization API")
    print("=" * 40)
    test_api_endpoints()