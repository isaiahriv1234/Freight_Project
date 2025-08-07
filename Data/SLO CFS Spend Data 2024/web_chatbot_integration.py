#!/usr/bin/env python3
"""
Web-based Procurement Chatbot Integration
Flask app that integrates chatbot with your existing systems
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from procurement_chatbot import ProcurementChatbot

app = Flask(__name__)
chatbot = ProcurementChatbot()

@app.route('/')
def index():
    """Main chatbot interface"""
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chat messages"""
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Handle data queries
        if user_message.startswith('/data'):
            query_type = user_message.split()[-1] if len(user_message.split()) > 1 else ""
            response = chatbot.get_data_insights(query_type)
            return jsonify({'response': response, 'type': 'data'})
        
        # Get AI response
        if chatbot.bedrock:
            response = chatbot.query_bedrock(user_message)
        else:
            response = chatbot.get_local_response(user_message)
        
        return jsonify({'response': response, 'type': 'ai'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/summary')
def data_summary():
    """Get procurement data summary"""
    
    try:
        df = chatbot.df
        
        summary = {
            'total_orders': len(df),
            'total_value': float(df['order_value'].sum()),
            'total_shipping': float(df['current_shipping_cost'].sum()),
            'potential_savings': float(df['potential_savings'].sum()),
            'optimization_rate': f"{len(df[df['optimization_opportunity']==1])}/{len(df)}"
        }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)