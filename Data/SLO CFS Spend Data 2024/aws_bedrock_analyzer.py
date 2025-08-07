#!/usr/bin/env python3
"""
AWS Bedrock LLM Analyzer for Shipping Dataset
Feeds ML-ready procurement data to AWS Bedrock for AI insights
"""

import boto3
import pandas as pd
import json
from datetime import datetime

class BedrockShippingAnalyzer:
    def __init__(self, data_file='ml_ready_shipping_dataset_20250807_002135.csv'):
        self.data_file = data_file
        self.df = pd.read_csv(data_file)
        
        # Initialize Bedrock client
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name='us-west-2'
        )
        
        # Model configuration
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def prepare_data_summary(self):
        """Create concise data summary for LLM analysis"""
        
        summary = {
            "dataset_overview": {
                "total_records": len(self.df),
                "total_order_value": f"${self.df['order_value'].sum():,.2f}",
                "total_shipping_cost": f"${self.df['current_shipping_cost'].sum():,.2f}",
                "potential_savings": f"${self.df['potential_savings'].sum():,.2f}"
            },
            "carrier_distribution": self.df['current_carrier'].value_counts().to_dict(),
            "diversity_breakdown": self.df['supplier_diversity'].value_counts().to_dict(),
            "optimization_opportunities": {
                "orders_with_savings": int(self.df[self.df['optimization_opportunity'] == 1].shape[0]),
                "orders_optimized": int(self.df[self.df['optimization_opportunity'] == 0].shape[0])
            },
            "key_metrics": {
                "avg_shipping_ratio": f"{self.df['shipping_ratio'].mean():.3f}",
                "avg_lead_time": f"{self.df['lead_time'].mean():.1f} days",
                "avg_consolidation_score": f"{self.df['consolidation_score'].mean():.1f}"
            }
        }
        
        return summary
    
    def create_analysis_prompt(self):
        """Generate comprehensive prompt for LLM analysis"""
        
        data_summary = self.prepare_data_summary()
        
        # Sample records for context
        sample_records = self.df.head(10).to_dict('records')
        
        prompt = f"""
You are a procurement and logistics optimization expert analyzing shipping data for Cal Poly SLO. 

DATASET SUMMARY:
{json.dumps(data_summary, indent=2)}

SAMPLE RECORDS (first 10):
{json.dumps(sample_records, indent=2)}

ANALYSIS REQUEST:
Please provide strategic insights on:

1. COST OPTIMIZATION OPPORTUNITIES
   - Identify the biggest savings potential
   - Recommend carrier consolidation strategies
   - Suggest volume discount negotiations

2. OPERATIONAL EFFICIENCY
   - Analyze lead time vs cost trade-offs
   - Recommend consolidation improvements
   - Identify shipping ratio optimization

3. SUPPLIER DIVERSITY IMPACT
   - Compare DVBE vs OSB performance
   - Recommend diversity-cost balance strategies

4. STRATEGIC RECOMMENDATIONS
   - Top 3 immediate actions for maximum ROI
   - Long-term procurement strategy improvements
   - Risk mitigation recommendations

Please provide actionable, data-driven recommendations with specific dollar amounts and percentages where possible.
"""
        
        return prompt
    
    def query_bedrock(self, prompt):
        """Send prompt to AWS Bedrock and get response"""
        
        try:
            # Prepare request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "top_p": 0.9
            }
            
            # Make API call
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            return f"Error querying Bedrock: {str(e)}"
    
    def analyze_shipping_data(self):
        """Main analysis function"""
        
        print("🚀 Starting AWS Bedrock Analysis...")
        print("=" * 50)
        
        # Create analysis prompt
        prompt = self.create_analysis_prompt()
        
        print("📊 Data Summary:")
        summary = self.prepare_data_summary()
        print(f"Total Records: {summary['dataset_overview']['total_records']}")
        print(f"Total Value: {summary['dataset_overview']['total_order_value']}")
        print(f"Potential Savings: {summary['dataset_overview']['potential_savings']}")
        print()
        
        print("🤖 Querying AWS Bedrock...")
        
        # Get AI analysis
        ai_response = self.query_bedrock(prompt)
        
        print("=" * 50)
        print("🎯 AI ANALYSIS RESULTS:")
        print("=" * 50)
        print(ai_response)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = {
            "timestamp": timestamp,
            "data_summary": summary,
            "ai_analysis": ai_response,
            "model_used": self.model_id
        }
        
        output_file = f"bedrock_analysis_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        return results

def main():
    """Run the Bedrock analysis"""
    
    try:
        analyzer = BedrockShippingAnalyzer()
        results = analyzer.analyze_shipping_data()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔧 Setup Requirements:")
        print("1. Install boto3: pip install boto3")
        print("2. Configure AWS credentials: aws configure")
        print("3. Ensure Bedrock access in us-west-2 region")
        print("4. Enable Claude model access in Bedrock console")

if __name__ == "__main__":
    main()