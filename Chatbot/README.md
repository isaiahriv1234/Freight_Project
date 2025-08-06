# AWS Bedrock Freight Data Chatbot

A sophisticated chatbot powered by AWS Bedrock that can understand natural language queries about Cal Poly's freight and procurement data.

## Features

- 🤖 **AI-Powered**: Uses AWS Bedrock with Claude 3 Sonnet for natural language understanding
- 📊 **Data Analysis**: Queries procurement data from Original-Table 1.csv
- 💬 **Conversational**: Natural language interface for complex data queries
- 🔍 **Smart Queries**: Handles questions about spending, suppliers, trends, and more

## Prerequisites

1. **AWS Account** with access to AWS Bedrock
2. **AWS Credentials** configured (AWS CLI, environment variables, or IAM roles)
3. **Bedrock Model Access** - Request access to Claude 3 Sonnet in AWS Console
4. **Python 3.8+**

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials
Choose one method:

**Option A: AWS CLI**
```bash
aws configure
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Request Bedrock Model Access
1. Go to AWS Bedrock Console
2. Navigate to "Model access" in the left menu
3. Request access to "Claude 3 Sonnet"
4. Wait for approval (usually instant for most accounts)

### 4. Test Setup
```bash
python setup_aws.py
```

### 5. Run the Chatbot
```bash
python bot.py
```

## Usage Examples

Once running, you can ask questions like:

- "What's the total spend across all suppliers?"
- "Who are the top 10 suppliers by spending?"
- "Show me monthly spending trends"
- "What's the average order value?"
- "How much did we spend on services vs goods?"
- "Which supplier type has the highest spending?"

## Creating a Knowledge Base (Optional)

For even better performance, create an AWS Bedrock Knowledge Base:

1. **Go to Bedrock Console** → Knowledge bases → Create knowledge base
2. **Upload Data**: Add your Original-Table 1.csv to an S3 bucket
3. **Configure Embedding**: Use Amazon Titan Embeddings
4. **Set Vector Store**: Use OpenSearch Serverless
5. **Test**: Query the knowledge base with sample questions

Then modify `bot.py` to use the knowledge base:
```python
# Replace generate_bedrock_response with knowledge base queries
bedrock_agent = boto3.client('bedrock-agent-runtime')
response = bedrock_agent.retrieve_and_generate(
    input={'text': user_query},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'your-kb-id',
            'modelArn': 'your-model-arn'
        }
    }
)
```

## Data Structure

The chatbot works with procurement data containing:
- Supplier information (name, type, ID)
- Purchase order details (ID, date, amounts)
- Spending categories (goods, services, construction, IT)
- Time periods and fiscal years

## Troubleshooting

### "No AWS credentials found"
- Run `aws configure` or set environment variables
- Check IAM permissions for Bedrock access

### "Access denied to Bedrock model"
- Request model access in AWS Bedrock Console
- Ensure IAM user/role has `bedrock:InvokeModel` permission

### "Model not available in this region"
- Try `us-east-1` or `us-west-2` regions
- Check model availability in AWS documentation

### Data loading errors
- Ensure `Original-Table 1.csv` is in the correct path
- Check CSV format and encoding

## Architecture

```
User Input → Natural Language Processing → Data Query → AWS Bedrock → AI Response
     ↓              ↓                        ↓            ↓           ↓
   "Who are     Extract intent         Query pandas    Generate      Formatted
   top          (suppliers, top,       DataFrame       contextual    response
   suppliers?"   ranking)              for results     response      with data
```

## Cost Considerations

- AWS Bedrock charges per token (input + output)
- Claude 3 Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Typical query costs: $0.01-0.05 per interaction
- Knowledge Base: Additional charges for vector storage and retrieval

## Security

- Never commit AWS credentials to version control
- Use IAM roles with minimal required permissions
- Consider VPC endpoints for private network access
- Implement input validation for production use

## Next Steps

1. **Enhanced Queries**: Add more sophisticated data analysis
2. **Visualization**: Generate charts and graphs
3. **Export Features**: Save query results to files
4. **Web Interface**: Create a web-based chat interface
5. **Real-time Data**: Connect to live procurement systems