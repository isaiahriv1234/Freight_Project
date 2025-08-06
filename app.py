#!/usr/bin/env python3
"""
Freight Optimization Web App - Step 1: Historical Spend Analysis
Clean, modern dashboard for procurement spend analysis
"""

from flask import Flask, render_template, jsonify
import pandas as pd
import json
from datetime import datetime
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    print("🚀 Starting Freight Optimization Dashboard...")
    print("📊 Open your browser to: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)