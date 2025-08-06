#!/usr/bin/env python3
"""
Freight Optimization Web App - Step 1: Historical Spend Analysis
Clean, modern dashboard for procurement spend analysis
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
from datetime import datetime
import os
from shipping_optimizer import ShippingOptimizer
from ups_integration import get_ups_rates_for_order
from consolidation_optimizer import ConsolidationOptimizer
from supplier_diversity_tracker import SupplierDiversityTracker
from automated_shipping_optimizer import AutomatedShippingOptimizer
from executive_dashboard import ExecutiveDashboard
from shipment_analyzer import ShipmentAnalyzer
from delivery_time_tracker import DeliveryTimeTracker
from centralized_purchasing_system import CentralizedPurchasingSystem

app = Flask(__name__)
shipping_optimizer = ShippingOptimizer()
consolidation_optimizer = ConsolidationOptimizer()
diversity_tracker = SupplierDiversityTracker()
automated_optimizer = AutomatedShippingOptimizer()
executive_dashboard = ExecutiveDashboard()
shipment_analyzer = ShipmentAnalyzer()
delivery_tracker = DeliveryTimeTracker()
purchasing_system = CentralizedPurchasingSystem()

def load_data():
    """Load the cleaned procurement data"""
    data_path = 'Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv'
    df = pd.read_csv(data_path)
    df['PO_Date'] = pd.to_datetime(df['PO_Date'])
    return df

def get_spend_summary(df):
    """Get key spend metrics"""
    return {
        'total_spend': df['Total_Amount'].sum(),
        'total_orders': len(df),
        'avg_order_value': df['Total_Amount'].mean(),
        'unique_suppliers': df['Supplier_Name'].nunique(),
        'date_range': {
            'start': df['PO_Date'].min().strftime('%Y-%m-%d'),
            'end': df['PO_Date'].max().strftime('%Y-%m-%d')
        }
    }

def get_monthly_trends(df):
    """Get monthly spending trends"""
    monthly = df.groupby(df['PO_Date'].dt.to_period('M'))['Total_Amount'].sum()
    return {
        'months': [str(month) for month in monthly.index],
        'amounts': monthly.values.tolist()
    }

def get_top_suppliers(df, limit=5):
    """Get top suppliers by spend"""
    suppliers = df.groupby('Supplier_Name')['Total_Amount'].sum().sort_values(ascending=False).head(limit)
    return {
        'suppliers': suppliers.index.tolist(),
        'amounts': suppliers.values.tolist()
    }

def get_category_breakdown(df):
    """Get spending by category"""
    categories = df.groupby('Order_Type')['Total_Amount'].sum()
    return {
        'categories': categories.index.tolist(),
        'amounts': categories.values.tolist()
    }

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

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
    dashboard_data = purchasing_system.get_centralized_dashboard_data()
    return render_template('centralized_dashboard.html', dashboard=dashboard_data)

@app.route('/api/spend-summary')
def api_spend_summary():
    """API endpoint for spend summary"""
    df = load_data()
    return jsonify(get_spend_summary(df))

@app.route('/api/monthly-trends')
def api_monthly_trends():
    """API endpoint for monthly trends"""
    df = load_data()
    return jsonify(get_monthly_trends(df))

@app.route('/api/top-suppliers')
def api_top_suppliers():
    """API endpoint for top suppliers"""
    df = load_data()
    return jsonify(get_top_suppliers(df))

@app.route('/api/category-breakdown')
def api_category_breakdown():
    """API endpoint for category breakdown"""
    df = load_data()
    return jsonify(get_category_breakdown(df))

@app.route('/api/shipping-recommendations')
def api_shipping_recommendations():
    """API endpoint for shipping carrier recommendations"""
    order_value = float(request.args.get('order_value', 1000))
    weight_category = request.args.get('weight_category', 'medium')
    urgency = request.args.get('urgency', 'standard')
    
    recommendations = shipping_optimizer.get_carrier_recommendations(
        order_value, weight_category, urgency
    )
    return jsonify(recommendations)

@app.route('/api/carrier-performance')
def api_carrier_performance():
    """API endpoint for carrier performance summary"""
    return jsonify(shipping_optimizer.get_carrier_performance_summary())

@app.route('/api/shipping-savings')
def api_shipping_savings():
    """API endpoint for cost savings analysis"""
    return jsonify(shipping_optimizer.get_cost_savings_analysis())

@app.route('/api/ups-rates')
def api_ups_rates():
    """API endpoint for real-time UPS shipping rates"""
    order_value = float(request.args.get('order_value', 1000))
    weight = float(request.args.get('weight', 5.0))
    dest_city = request.args.get('dest_city', 'Los Angeles')
    dest_state = request.args.get('dest_state', 'CA')
    dest_zip = request.args.get('dest_zip', '90210')
    
    ups_rates = get_ups_rates_for_order(order_value, weight, dest_city, dest_state, dest_zip)
    return jsonify(ups_rates)

@app.route('/api/consolidation-opportunities')
def api_consolidation_opportunities():
    """API endpoint for consolidation opportunities"""
    days_window = int(request.args.get('days_window', 7))
    opportunities = consolidation_optimizer.find_consolidation_opportunities(days_window)
    return jsonify(opportunities)

@app.route('/api/consolidation-summary')
def api_consolidation_summary():
    """API endpoint for consolidation summary"""
    return jsonify(consolidation_optimizer.get_consolidation_summary())

@app.route('/api/consolidation-strategy')
def api_consolidation_strategy():
    """API endpoint for consolidation strategy recommendations"""
    supplier = request.args.get('supplier')
    return jsonify(consolidation_optimizer.recommend_consolidation_strategy(supplier))

@app.route('/api/diversity-summary')
def api_diversity_summary():
    """API endpoint for supplier diversity performance summary"""
    return jsonify(diversity_tracker.get_diversity_performance_summary())

@app.route('/api/diverse-suppliers')
def api_diverse_suppliers():
    """API endpoint for diverse supplier identification"""
    return jsonify(diversity_tracker.identify_diverse_suppliers())

@app.route('/api/diversity-goals')
def api_diversity_goals():
    """API endpoint for diversity goal tracking"""
    target = float(request.args.get('target', 25.0))
    return jsonify(diversity_tracker.track_diversity_goals(target))

@app.route('/api/diversity-trends')
def api_diversity_trends():
    """API endpoint for diversity performance trends"""
    return jsonify(diversity_tracker.get_monthly_diversity_trends())

@app.route('/api/auto-carrier-select', methods=['POST'])
def api_auto_carrier_select():
    """API endpoint for automated carrier selection"""
    order_details = request.get_json()
    return jsonify(automated_optimizer.auto_select_carrier(order_details))

@app.route('/api/automation-alerts')
def api_automation_alerts():
    """API endpoint for automation alerts"""
    return jsonify(automated_optimizer.generate_automation_alerts())

@app.route('/api/shipping-rules')
def api_shipping_rules():
    """API endpoint for automated shipping rules"""
    return jsonify(automated_optimizer.create_shipping_rules())

@app.route('/api/automation-dashboard')
def api_automation_dashboard():
    """API endpoint for automation dashboard data"""
    return jsonify(automated_optimizer.get_automation_dashboard_data())

@app.route('/api/executive-report')
def api_executive_report():
    """API endpoint for executive dashboard report"""
    return jsonify(executive_dashboard.generate_executive_report())

@app.route('/api/consolidation-visibility')
def api_consolidation_visibility():
    """API endpoint for enhanced consolidation visibility"""
    return jsonify(executive_dashboard.get_consolidation_visibility())

@app.route('/api/diversity-visibility')
def api_diversity_visibility():
    """API endpoint for enhanced diversity visibility"""
    return jsonify(executive_dashboard.get_diversity_visibility())

@app.route('/api/challenge-readiness')
def api_challenge_readiness():
    """API endpoint for challenge readiness analysis"""
    return jsonify(shipment_analyzer.generate_challenge_readiness_report())

@app.route('/api/cost-comparison')
def api_cost_comparison():
    """API endpoint for cost calculator comparison"""
    return jsonify(shipment_analyzer.cost_calculator_comparison())

@app.route('/api/data-completeness')
def api_data_completeness():
    """API endpoint for data completeness analysis"""
    return jsonify(shipment_analyzer.analyze_current_data_completeness())

@app.route('/api/delivery-dashboard')
def api_delivery_dashboard():
    """API endpoint for delivery tracking dashboard data"""
    return jsonify(delivery_tracker.get_delivery_dashboard_data())

@app.route('/api/delivery-performance')
def api_delivery_performance():
    """API endpoint for delivery performance summary"""
    return jsonify(delivery_tracker.get_delivery_performance_summary())

@app.route('/api/predict-delivery')
def api_predict_delivery():
    """API endpoint for delivery time prediction"""
    carrier = request.args.get('carrier', 'UPS')
    order_value = float(request.args.get('order_value', 1000))
    supplier = request.args.get('supplier')
    return jsonify(delivery_tracker.predict_delivery_times(carrier, order_value, supplier))

@app.route('/api/delivery-alerts')
def api_delivery_alerts():
    """API endpoint for delivery alerts"""
    return jsonify(delivery_tracker.generate_delivery_alerts())

@app.route('/api/submit-purchase-request', methods=['POST'])
def api_submit_purchase_request():
    """API endpoint for submitting purchase requests"""
    request_data = request.get_json()
    result = purchasing_system.submit_purchase_request(request_data)
    return jsonify(result)

@app.route('/api/approve-request', methods=['POST'])
def api_approve_request():
    """API endpoint for approving purchase requests"""
    approval_data = request.get_json()
    result = purchasing_system.process_approval(
        approval_data['request_id'],
        approval_data['approver'],
        approval_data['decision'],
        approval_data.get('notes', '')
    )
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Starting Freight Optimization Dashboard...")
    print("📊 Open your browser to: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)