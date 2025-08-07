#!/usr/bin/env python3
"""
Quick test of the web chatbot with fixed model
"""

from flask import Flask, render_template, request, jsonify
from procurement_chatbot import ProcurementChatbot

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Procurement Chatbot Test</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .chat { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #e3f2fd; text-align: right; }
            .bot { background: #f5f5f5; }
            input { width: 70%; padding: 10px; }
            button { padding: 10px 20px; }
        </style>
    </head>
    <body>
        <h1>🤖 Procurement Optimization Chatbot</h1>
        <div id="chat" class="chat"></div>
        <input type="text" id="messageInput" placeholder="Ask about your $17,452 savings potential..." onkeypress="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()">Send</button>
        
        <script>
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, 'user');
                input.value = '';
                addMessage('Thinking...', 'bot');
                
                fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('chat').lastElementChild.remove();
                    addMessage(data.response || data.error, 'bot');
                });
            }
            
            function addMessage(text, type) {
                const chat = document.getElementById('chat');
                const div = document.createElement('div');
                div.className = 'message ' + type;
                div.innerHTML = '<strong>' + (type === 'user' ? 'You' : 'Assistant') + ':</strong> ' + text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }
            
            // Welcome message
            addMessage('Hello! I have access to your 72 procurement orders with $17,452 in potential savings. Ask me about cost optimization, carrier performance, or supplier diversity!', 'bot');
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    try:
        chatbot = ProcurementChatbot()
        data = request.get_json()
        message = data.get('message', '')
        
        if message.startswith('/data'):
            query_type = message.split()[-1] if len(message.split()) > 1 else ""
            response = chatbot.get_data_insights(query_type)
        else:
            response = chatbot.query_bedrock(message)
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5003)