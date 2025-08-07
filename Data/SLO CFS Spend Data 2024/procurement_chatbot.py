#!/usr/bin/env python3
"""
Procurement Optimization Chatbot
Integrates with existing systems and uses AWS Bedrock for AI responses
"""

import boto3
import pandas as pd
import json
from datetime import datetime
import sys
import os

class ProcurementChatbot:
    def __init__(self):
        # Load procurement data
        self.df = pd.read_csv('ml_ready_shipping_dataset_20250807_002135.csv')
        self.cleaned_df = pd.read_csv('Cleaned_Procurement_Data.csv')
        
        # Initialize Bedrock client
        try:
            self.bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
            self.model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
            print("✅ AWS Bedrock connected successfully")
        except:
            print("⚠️  AWS Bedrock not configured. Using local responses.")
            self.bedrock = None
        
        # System context about the procurement data
        self.system_context = self.build_system_context()
        
    def build_system_context(self):
        """Build context about the procurement system"""
        
        total_value = self.df['order_value'].sum()
        total_shipping = self.df['current_shipping_cost'].sum()
        potential_savings = self.df['potential_savings'].sum()
        
        context = f"""
You are a procurement optimization assistant for Cal Poly SLO with access to real shipping data.

CURRENT SYSTEM DATA:
- Total Orders: {len(self.df)} records
- Total Value: ${total_value:,.2f}
- Current Shipping Costs: ${total_shipping:,.2f}
- Potential Annual Savings: ${potential_savings:,.2f}
- Optimization Rate: {len(self.df[self.df['optimization_opportunity']==1])}/{len(self.df)} orders

AVAILABLE SYSTEMS:
- Shipping optimization engine
- Consolidation analysis
- Supplier diversity tracking
- Automated purchasing decisions
- Real-time rate comparison (EasyPost API)

Answer questions about procurement optimization, shipping costs, supplier diversity, and provide actionable recommendations based on this data.
"""
        return context
    
    def call_bedrock_model(self, message: str):
        """Send message to AWS Bedrock using working configuration"""
        
        if not self.bedrock:
            return "AWS Bedrock not available. Please configure AWS credentials."
        
        try:
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": message}],
            }
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(payload)
            )
            
            response_body = json.loads(response["body"].read())
            return response_body["content"][0]["text"]
            
        except Exception as e:
            return f"Bedrock Error: {str(e)}"
    
    def query_bedrock(self, user_message):
        """Query with procurement context"""
        prompt = f"{self.system_context}\n\nUser Question: {user_message}"
        return self.call_bedrock_model(prompt)
    
    def get_data_insights(self, query_type):
        """Get specific data insights"""
        
        if query_type == "savings":
            high_savings = self.df.nlargest(5, 'potential_savings')[['order_value', 'current_shipping_cost', 'potential_savings']]
            return f"Top 5 savings opportunities:\n{high_savings.to_string()}"
        
        elif query_type == "carriers":
            carrier_stats = self.df.groupby('current_carrier').agg({
                'order_value': 'sum',
                'current_shipping_cost': 'sum',
                'potential_savings': 'sum'
            }).round(2)
            return f"Carrier performance:\n{carrier_stats.to_string()}"
        
        elif query_type == "diversity":
            diversity_stats = self.df.groupby('supplier_diversity').agg({
                'order_value': 'sum',
                'current_shipping_cost': 'mean',
                'potential_savings': 'sum'
            }).round(2)
            return f"Supplier diversity breakdown:\n{diversity_stats.to_string()}"
        
        return "Available queries: savings, carriers, diversity"
    
    def chat_loop(self):
        """Main chatbot interaction loop"""
        
        print("🤖 Procurement Optimization Chatbot")
        print("=" * 50)
        print("Ask me about:")
        print("• Shipping cost optimization")
        print("• Carrier performance")
        print("• Supplier diversity")
        print("• Consolidation opportunities")
        print("• Data insights (type: /data [savings|carriers|diversity])")
        print("• Type 'quit' to exit")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.startswith('/data'):
                    query_type = user_input.split()[-1] if len(user_input.split()) > 1 else ""
                    response = self.get_data_insights(query_type)
                    print(f"\n📊 Data: {response}")
                    continue
                
                if not user_input:
                    continue
                
                print("\n🤖 Assistant: Thinking...")
                
                # Get AI response
                if self.bedrock:
                    response = self.query_bedrock(user_input)
                else:
                    response = self.get_local_response(user_input)
                
                print(f"\n🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    def get_local_response(self, user_input):
        """Fallback responses when Bedrock unavailable"""
        
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['savings', 'save', 'cost']):
            total_savings = self.df['potential_savings'].sum()
            return f"Based on your data, you have ${total_savings:,.2f} in potential annual savings across {len(self.df)} orders. The biggest opportunities are in freight and electronic delivery optimization."
        
        elif any(word in user_lower for word in ['carrier', 'shipping', 'delivery']):
            return "Your current carriers include Ground (28 orders), UPS (13), Freight (12), FedEx (6), and Electronic (6). Consider consolidating to fewer carriers for volume discounts."
        
        elif any(word in user_lower for word in ['diversity', 'dvbe', 'osb']):
            return "Your supplier diversity: DVBE suppliers handle $248K (76% of spend), OSB suppliers handle $75K (24%). Both categories show good optimization potential."
        
        else:
            return "I can help with shipping optimization, cost savings, carrier analysis, and supplier diversity questions. Try asking about specific topics or use /data commands."

def main():
    """Run the chatbot"""
    
    try:
        chatbot = ProcurementChatbot()
        chatbot.chat_loop()
        
    except FileNotFoundError as e:
        print(f"❌ Data file not found: {e}")
        print("Make sure you're in the correct directory with the CSV files.")
    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")

if __name__ == "__main__":
    main()