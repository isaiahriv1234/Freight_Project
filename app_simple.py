#!/usr/bin/env python3
"""
Simplified Freight Optimization Web App for Frontend Testing
"""

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
import random

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/shipping')
def shipping_home():
    """Shipping homepage"""
    return render_template('shipping_home.html')

@app.route('/ship-now')
def ship_now():
    """Ship now form page"""
    return render_template('ship_now.html')

@app.route('/tracking')
def tracking():
    """Tracking page"""
    return render_template('tracking.html')

@app.route('/get-quote')
def get_quote():
    """Get quote page"""
    return render_template('get_quote.html')

@app.route('/payment')
def payment():
    """Payment page"""
    return render_template('payment.html')

@app.route('/payment-success')
def payment_success():
    """Payment success page"""
    return render_template('payment_success.html')

@app.route('/automation')
def automation_dashboard():
    """Automation dashboard page"""
    return render_template('automation_dashboard.html')

@app.route('/executive')
def executive_dashboard_page():
    """Executive dashboard page"""
    return render_template('executive_dashboard.html')

@app.route('/challenge')
def challenge_dashboard_page():
    """Challenge readiness dashboard page"""
    return render_template('challenge_dashboard.html')

@app.route('/delivery')
def delivery_dashboard_page():
    """Delivery tracking dashboard page"""
    return render_template('delivery_dashboard.html')

@app.route('/centralized-purchasing')
def centralized_purchasing():
    """Centralized purchasing dashboard page"""
    return render_template('centralized_dashboard.html')

# API Endpoints
@app.route('/api/spend-summary')
def api_spend_summary():
    """API endpoint for spend summary"""
    return jsonify({
        'total_spend': 2500000,
        'total_orders': 1500,
        'avg_order_value': 1667,
        'unique_suppliers': 45,
        'date_range': {
            'start': '2024-01-01',
            'end': '2024-12-31'
        }
    })

@app.route('/api/monthly-trends')
def api_monthly_trends():
    """API endpoint for monthly trends"""
    return jsonify({
        'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'amounts': [200000, 220000, 240000, 260000, 280000, 300000]
    })

@app.route('/api/top-suppliers')
def api_top_suppliers():
    """API endpoint for top suppliers"""
    return jsonify({
        'suppliers': ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E'],
        'amounts': [500000, 400000, 300000, 250000, 200000]
    })

@app.route('/api/category-breakdown')
def api_category_breakdown():
    """API endpoint for category breakdown"""
    return jsonify({
        'categories': ['IT', 'Construction', 'Services', 'Equipment'],
        'amounts': [800000, 600000, 500000, 600000]
    })

@app.route('/api/calculate-quote', methods=['POST'])
def api_calculate_quote():
    """API endpoint for calculating shipping quotes"""
    data = request.get_json()
    
    # Extract shipment data
    dropoff = data.get('dropoff', {})
    pickup = data.get('pickup', {})
    items = data.get('items', [])
    insurance = data.get('insurance', 'basic')
    
    # Calculate quote using shipping optimizer
    quote_data = {
        'dropoff_location': f"{dropoff.get('location', '')} - {dropoff.get('specific', '')}",
        'pickup_location': f"{pickup.get('location', '')} - {pickup.get('specific', '')}",
        'items': items,
        'insurance': insurance,
        'total_weight': sum(item.get('weight', 0) for item in items),
        'total_items': len(items),
        'estimated_cost': calculate_shipping_cost(items, dropoff, pickup, insurance),
        'carrier_options': get_carrier_options(items, dropoff, pickup),
        'delivery_estimates': get_delivery_estimates(dropoff, pickup)
    }
    
    return jsonify({
        'success': True,
        'quote': quote_data
    })

@app.route('/api/track-shipment', methods=['POST'])
def api_track_shipment():
    """API endpoint for tracking shipments"""
    data = request.get_json()
    tracking_number = data.get('tracking_number')
    
    # Mock tracking data
    tracking_info = {
        'tracking_number': tracking_number,
        'carrier': 'FedEx',
        'status': 'In Transit',
        'estimated_delivery': '2024-08-12',
        'events': [
            {
                'type': 'in_transit',
                'title': 'Package in transit',
                'location': 'Memphis, TN',
                'timestamp': '2024-08-10T14:30:00Z'
            },
            {
                'type': 'pickup',
                'title': 'Package picked up',
                'location': 'San Luis Obispo, CA',
                'timestamp': '2024-08-09T10:15:00Z'
            },
            {
                'type': 'pending',
                'title': 'Shipment created',
                'location': 'Cal Poly Campus',
                'timestamp': '2024-08-09T09:00:00Z'
            }
        ]
    }
    
    return jsonify({
        'success': True,
        'tracking_info': tracking_info
    })

@app.route('/api/process-payment', methods=['POST'])
def api_process_payment():
    """API endpoint for processing payments"""
    data = request.get_json()
    
    # Extract payment data
    payment_method = data.get('payment_method')
    shipping_option = data.get('shipping_option')
    quote_data = data.get('quote_data')
    card_data = data.get('card_data', {})
    
    # Simulate payment processing
    try:
        # Validate payment data
        if payment_method == 'credit-card':
            if not card_data.get('card_number') or not card_data.get('expiration_date'):
                return jsonify({
                    'success': False,
                    'message': 'Invalid card information'
                })
        
        # Simulate processing delay
        import time
        time.sleep(1)
        
        # Generate tracking number
        tracking_number = f"{random.randint(1000000000000000, 9999999999999999)}"
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'tracking_number': tracking_number,
            'order_id': f"ORDER-{random.randint(10000, 99999)}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Payment processing failed: {str(e)}'
        })

def calculate_shipping_cost(items, dropoff, pickup, insurance):
    """Calculate estimated shipping cost"""
    base_cost = 50  # Base shipping cost
    weight_cost = sum(item.get('weight', 0) for item in items) * 2  # $2 per lb
    distance_cost = 25  # Estimated distance cost
    insurance_cost = get_insurance_cost(insurance)
    
    return base_cost + weight_cost + distance_cost + insurance_cost

def get_insurance_cost(insurance_type):
    """Get insurance cost based on type"""
    insurance_costs = {
        'basic': 5,
        'standard': 15,
        'premium': 30,
        'custom': 20  # Default for custom
    }
    return insurance_costs.get(insurance_type, 5)

def get_carrier_options(items, dropoff, pickup):
    """Get available carrier options"""
    total_weight = sum(item.get('weight', 0) for item in items)
    
    carriers = []
    if total_weight <= 50:
        carriers.extend(['FedEx', 'UPS', 'USPS'])
    elif total_weight <= 150:
        carriers.extend(['FedEx', 'UPS'])
    else:
        carriers.append('DHL')
    
    return carriers

def get_delivery_estimates(dropoff, pickup):
    """Get delivery time estimates"""
    return {
        'standard': '3-5 business days',
        'express': '1-2 business days',
        'overnight': 'Next business day'
    }

if __name__ == '__main__':
    print("🚀 Starting Simplified Freight Optimization Dashboard...")
    print("📊 Open your browser to: http://127.0.0.1:5000")
    print("🎯 Test the shipping interface at: http://127.0.0.1:5000/shipping")
    app.run(debug=True, port=5000) 