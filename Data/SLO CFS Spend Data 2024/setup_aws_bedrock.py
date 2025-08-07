#!/usr/bin/env python3
"""
AWS Bedrock Setup Helper
Helps configure AWS credentials and test Bedrock access
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            return False, "No AWS credentials found"
        
        return True, f"Credentials found for: {credentials.access_key[:8]}..."
    
    except Exception as e:
        return False, str(e)

def test_bedrock_access():
    """Test AWS Bedrock access and model availability"""
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Test with a simple prompt
        test_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [{"role": "user", "content": "Hello, can you respond?"}],
            "temperature": 0.1
        }
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(test_body)
        )
        
        return True, "Bedrock access successful"
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            return False, "Access denied - check Bedrock permissions and model access"
        elif error_code == 'ValidationException':
            return False, "Model not available - enable Claude in Bedrock console"
        else:
            return False, f"AWS Error: {error_code}"
    
    except NoCredentialsError:
        return False, "No AWS credentials configured"
    
    except Exception as e:
        return False, str(e)

def main():
    print("🔧 AWS Bedrock Setup Check")
    print("=" * 40)
    
    # Check credentials
    creds_ok, creds_msg = check_aws_credentials()
    print(f"AWS Credentials: {'✅' if creds_ok else '❌'} {creds_msg}")
    
    if not creds_ok:
        print("\n📋 To configure AWS credentials:")
        print("1. Install AWS CLI: pip install awscli")
        print("2. Run: aws configure")
        print("3. Enter your Access Key ID and Secret Access Key")
        return
    
    # Test Bedrock access
    bedrock_ok, bedrock_msg = test_bedrock_access()
    print(f"Bedrock Access: {'✅' if bedrock_ok else '❌'} {bedrock_msg}")
    
    if not bedrock_ok:
        print("\n📋 To enable Bedrock access:")
        print("1. Go to AWS Bedrock console: https://us-west-2.console.aws.amazon.com/bedrock/")
        print("2. Navigate to 'Model access' in left sidebar")
        print("3. Click 'Enable specific models'")
        print("4. Enable 'Claude 3 Sonnet' by Anthropic")
        print("5. Wait for approval (usually instant)")
        return
    
    print("\n🎉 Setup complete! You can now run the Bedrock analyzer.")

if __name__ == "__main__":
    main()