#!/usr/bin/env python3
"""
Test the chatbot with local responses (no AWS needed)
"""

from procurement_chatbot import ProcurementChatbot

def test_chatbot():
    print("🧪 Testing Chatbot with Local Responses")
    print("=" * 50)
    
    # Create chatbot (will use local responses if AWS unavailable)
    chatbot = ProcurementChatbot()
    
    # Test questions
    test_questions = [
        "What are my biggest cost savings opportunities?",
        "How are my carriers performing?",
        "Tell me about supplier diversity",
        "/data savings",
        "/data carriers",
        "/data diversity"
    ]
    
    for question in test_questions:
        print(f"\n💬 Question: {question}")
        
        if question.startswith('/data'):
            query_type = question.split()[-1] if len(question.split()) > 1 else ""
            response = chatbot.get_data_insights(query_type)
            print(f"📊 Response: {response}")
        else:
            response = chatbot.get_local_response(question)
            print(f"🤖 Response: {response}")

if __name__ == "__main__":
    test_chatbot()