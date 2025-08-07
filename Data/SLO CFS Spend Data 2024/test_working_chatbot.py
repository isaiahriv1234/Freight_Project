#!/usr/bin/env python3
"""
Test the updated chatbot with your working Bedrock code
"""

from procurement_chatbot import ProcurementChatbot

def main():
    print("🤖 Testing Procurement Chatbot with Your Bedrock Code")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = ProcurementChatbot()
    
    # Test with actual procurement questions
    test_questions = [
        "What are my top 3 cost savings opportunities from the $17,452 potential?",
        "How should I optimize my carrier mix with 28 Ground, 13 UPS, and 12 Freight orders?",
        "Compare my DVBE vs OSB supplier performance"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 50)
        
        if chatbot.bedrock:
            response = chatbot.query_bedrock(question)
            print(f"🤖 AI Response: {response}")
        else:
            response = chatbot.get_local_response(question)
            print(f"💻 Local Response: {response}")
        
        print()

if __name__ == "__main__":
    main()