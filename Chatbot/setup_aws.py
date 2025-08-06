#!/usr/bin/env python3
"""
AWS Setup and Configuration Helper for Freight Chatbot
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_connection():
    """Test AWS connection and Bedrock access"""
    print("🔧 Testing AWS Connection...")
    
    try:
        # Test basic AWS connection
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Connection successful!")
        print(f"   Account: {identity.get('Account')}")
        print(f"   User/Role: {identity.get('Arn')}")
        
        # Test Bedrock access
        print("\n🧠 Testing AWS Bedrock access...")
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Try to list available models (this requires bedrock:ListFoundationModels permission)
        try:
            bedrock_models = boto3.client('bedrock', region_name='us-east-1')
            models = bedrock_models.list_foundation_models()
            print("✅ Bedrock access confirmed!")
            print(f"   Available models: {len(models.get('modelSummaries', []))}")
            
            # Check if Claude is available
            claude_models = [m for m in models.get('modelSummaries', []) if 'claude' in m.get('modelId', '').lower()]
            if claude_models:
                print(f"   Claude models available: {len(claude_models)}")
            else:
                print("⚠️  No Claude models found - you may need to request access")
                
        except ClientError as e:
            print(f"⚠️  Limited Bedrock access: {e}")
            print("   You may still be able to use the chatbot if you have invoke permissions")
        
        return True
        
    except NoCredentialsError:
        print("❌ No AWS credentials found!")
        print("   Please configure AWS credentials using one of these methods:")
        print("   1. AWS CLI: aws configure")
        print("   2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("   3. IAM roles (if running on EC2)")
        return False
        
    except ClientError as e:
        print(f"❌ AWS connection failed: {e}")
        return False

def create_sample_bedrock_request():
    """Create a sample request to test Bedrock"""
    print("\n🧪 Testing Bedrock with sample request...")
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Can you help me analyze freight data?"
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        print("✅ Bedrock test successful!")
        print(f"   Response: {response_body['content'][0]['text'][:100]}...")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Access denied to Bedrock model")
            print("   You need to request access to Claude models in the AWS Bedrock console")
        elif error_code == 'ValidationException':
            print("❌ Model not available in this region")
            print("   Try a different region or model")
        else:
            print(f"❌ Bedrock test failed: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def setup_knowledge_base_info():
    """Provide information about setting up a knowledge base"""
    print("\n📚 Knowledge Base Setup Information:")
    print("="*50)
    print("To create a knowledge base in AWS Bedrock:")
    print("1. Go to AWS Bedrock console")
    print("2. Navigate to 'Knowledge bases' in the left menu")
    print("3. Click 'Create knowledge base'")
    print("4. Upload your Original-Table 1.csv file")
    print("5. Configure the embedding model (Amazon Titan recommended)")
    print("6. Set up vector database (OpenSearch Serverless)")
    print("7. Configure data source (S3 bucket with your CSV)")
    print("8. Test the knowledge base with sample queries")
    print("\nOnce created, you can modify the chatbot to use:")
    print("- bedrock_agent_runtime.retrieve()")
    print("- bedrock_agent_runtime.retrieve_and_generate()")

def main():
    """Main setup function"""
    print("🚛 AWS Bedrock Freight Chatbot Setup")
    print("="*40)
    
    # Test AWS connection
    if not test_aws_connection():
        return
    
    # Test Bedrock
    if not create_sample_bedrock_request():
        print("\n💡 Next steps:")
        print("1. Request access to Claude models in AWS Bedrock console")
        print("2. Ensure you have bedrock:InvokeModel permissions")
        print("3. Try running the chatbot after access is granted")
        return
    
    # Show knowledge base info
    setup_knowledge_base_info()
    
    print("\n🎉 Setup complete! You can now run the chatbot with:")
    print("   python bot.py")

if __name__ == "__main__":
    main()