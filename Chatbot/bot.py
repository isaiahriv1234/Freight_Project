#!/usr/bin/env python3
"""
AWS Bedrock-Powered Freight Data Chatbot
Handles natural language queries about procurement and freight data
"""

import boto3
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class FreightChatbot:
    def __init__(self):
        """Initialize the chatbot with AWS Bedrock client and data"""
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1'  # Adjust region as needed
        )
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.data_path = "../Data/SLO CFS Spend Data 2024/Original-Table 1.csv"
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess the freight data"""
        try:
            # Load the CSV data
            self.df = pd.read_csv(self.data_path, skiprows=4)  # Skip header rows
            
            # Clean column names
            self.df.columns = [
                'Supplier_Type', 'Supplier_ID', 'Supplier_Name', 'PO_ID', 'PO_Date',
                'Line_Schedule', 'Line_Description', 'NIGP', 'Order_Indicator',
                'Goods_Amount', 'Services_Amount', 'Construction_Amount', 
                'IT_Amount', 'Act_Period', 'Fiscal_Year'
            ]
            
            # Convert date column
            self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'], errors='coerce')
            
            # Convert amount columns to numeric
            amount_cols = ['Goods_Amount', 'Services_Amount', 'Construction_Amount', 'IT_Amount']
            for col in amount_cols:
                self.df[col] = pd.to_numeric(self.df[col].astype(str).str.replace(',', ''), errors='coerce')
            
            # Calculate total amount
            self.df['Total_Amount'] = self.df[amount_cols].sum(axis=1)
            
            print(f"Loaded {len(self.df)} records from freight data")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def get_data_summary(self) -> str:
        """Generate a summary of the available data"""
        if self.df.empty:
            return "No data available"
        
        summary = f"""
        Data Summary:
        - Total Records: {len(self.df):,}
        - Date Range: {self.df['PO_Date'].min()} to {self.df['PO_Date'].max()}
        - Total Spend: ${self.df['Total_Amount'].sum():,.2f}
        - Unique Suppliers: {self.df['Supplier_Name'].nunique()}
        - Supplier Types: {', '.join(self.df['Supplier_Type'].unique())}
        - Top 5 Suppliers by Spend:
        {self.df.groupby('Supplier_Name')['Total_Amount'].sum().sort_values(ascending=False).head().to_string()}
        """
        return summary
    
    def query_data(self, query: str) -> str:
        """Execute data queries based on natural language input"""
        query_lower = query.lower()
        
        try:
            # Handle different types of queries
            if 'total spend' in query_lower or 'total amount' in query_lower:
                total = self.df['Total_Amount'].sum()
                return f"Total spend across all records: ${total:,.2f}"
            
            elif 'supplier' in query_lower and 'top' in query_lower:
                top_suppliers = self.df.groupby('Supplier_Name')['Total_Amount'].sum().sort_values(ascending=False).head(10)
                result = "Top 10 Suppliers by Total Spend:\n"
                for supplier, amount in top_suppliers.items():
                    result += f"• {supplier}: ${amount:,.2f}\n"
                return result
            
            elif 'monthly' in query_lower or 'by month' in query_lower:
                monthly = self.df.groupby(self.df['PO_Date'].dt.to_period('M'))['Total_Amount'].sum()
                result = "Monthly Spend:\n"
                for month, amount in monthly.items():
                    result += f"• {month}: ${amount:,.2f}\n"
                return result
            
            elif 'supplier type' in query_lower:
                by_type = self.df.groupby('Supplier_Type')['Total_Amount'].sum().sort_values(ascending=False)
                result = "Spend by Supplier Type:\n"
                for stype, amount in by_type.items():
                    result += f"• {stype}: ${amount:,.2f}\n"
                return result
            
            elif 'average' in query_lower and 'order' in query_lower:
                avg_order = self.df['Total_Amount'].mean()
                return f"Average order value: ${avg_order:,.2f}"
            
            else:
                return "I can help you with queries about total spend, top suppliers, monthly trends, supplier types, and average order values. Please try rephrasing your question."
                
        except Exception as e:
            return f"Error processing query: {e}"
    
    def generate_bedrock_response(self, user_query: str) -> str:
        """Generate response using AWS Bedrock"""
        try:
            # Get relevant data context
            data_context = self.get_data_summary()
            data_query_result = self.query_data(user_query)
            
            # Create prompt for Bedrock
            prompt = f"""
            You are a helpful AI assistant specializing in freight and procurement data analysis for Cal Poly San Luis Obispo.
            
            Data Context:
            {data_context}
            
            Query Result:
            {data_query_result}
            
            User Question: {user_query}
            
            Please provide a comprehensive, helpful response based on the data available. If the user is asking about specific metrics or trends, use the query results above. Be conversational and explain the significance of the numbers when relevant.
            """
            
            # Prepare request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            return f"Error generating AI response: {e}. Here's the direct data result: {data_query_result}"
    
    def chat(self):
        """Main chat loop"""
        print("🚛 Freight Data Chatbot powered by AWS Bedrock")
        print("Ask me anything about Cal Poly's procurement and freight data!")
        print("Type 'quit' to exit, 'help' for examples\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye! 👋")
                break
            
            elif user_input.lower() == 'help':
                print("""
                Example questions you can ask:
                • What's the total spend?
                • Who are the top suppliers?
                • Show me monthly spending trends
                • What's the average order value?
                • Break down spending by supplier type
                • How much did we spend with [specific supplier]?
                """)
                continue
            
            elif not user_input:
                continue
            
            print("🤖 Thinking...")
            response = self.generate_bedrock_response(user_input)
            print(f"Bot: {response}\n")

def main():
    """Main function to run the chatbot"""
    try:
        chatbot = FreightChatbot()
        chatbot.chat()
    except Exception as e:
        print(f"Error starting chatbot: {e}")
        print("Make sure you have:")
        print("1. AWS credentials configured")
        print("2. Access to AWS Bedrock")
        print("3. The data file in the correct location")

if __name__ == "__main__":
    main()