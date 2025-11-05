"""
Chatbot API with RAG Integration
File: api/chatbot.py
"""

from flask import Blueprint, request, jsonify
from utils.save_load import data_manager
from utils.rag_engine import RAGEngine, OpenAIRAGEngine
import pandas as pd
import uuid
import json
from datetime import datetime
import os

chatbot_bp = Blueprint('chatbot', __name__)

# Load data
chats_df = data_manager.load_chats()
programs_df = data_manager.load_programs()

# Initialize RAG engine
USE_OPENAI = os.getenv('OPENAI_API_KEY') is not None
if USE_OPENAI:
    rag_engine = OpenAIRAGEngine(programs_df)
else:
    rag_engine = RAGEngine(programs_df)

@chatbot_bp.route('/chat-instance', methods=['POST'])
def create_chat_instance():
    """Create a new chat instance"""
    global chats_df
    
    try:
        data = request.get_json() or {}
        
        # Create new chat
        chat = {
            'chat_id': str(uuid.uuid4()),
            'user_id': data.get('user_id', 'anonymous'),
            'messages': json.dumps([]),  # Store as JSON string
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add to DataFrame
        new_chat = pd.DataFrame([chat])
        chats_df = pd.concat([chats_df, new_chat], ignore_index=True)
        
        # Save
        data_manager.save_chats(chats_df)
        
        return jsonify({
            'message': 'Chat instance created',
            'chat_id': chat['chat_id'],
            'chat': chat
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/chat/<chat_id>', methods=['POST'])
def send_message(chat_id):
    """Send a message and get AI response"""
    global chats_df
    
    try:
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({'error': 'Message required'}), 400
        
        user_message = data['message']
        
        # Find chat
        chat_idx = chats_df[chats_df['chat_id'] == chat_id].index
        
        if len(chat_idx) == 0:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Get existing messages
        messages_str = chats_df.at[chat_idx[0], 'messages']
        messages = json.loads(messages_str) if messages_str else []
        
        # Add user message
        messages.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get RAG response
        rag_response = rag_engine.chat(user_message, history=messages)
        
        # Add bot response
        bot_message = {
            'role': 'assistant',
            'content': rag_response['response'],
            'programs': rag_response.get('programs', []),
            'timestamp': datetime.now().isoformat()
        }
        messages.append(bot_message)
        
        # Update chat
        chats_df.at[chat_idx[0], 'messages'] = json.dumps(messages)
        chats_df.at[chat_idx[0], 'updated_at'] = datetime.now().isoformat()
        
        # Save
        data_manager.save_chats(chats_df)
        
        return jsonify({
            'message': 'Response generated',
            'response': bot_message,
            'chat_id': chat_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/chat/<chat_id>', methods=['GET'])
def get_chat_history(chat_id):
    """Get chat history"""
    try:
        chat = chats_df[chats_df['chat_id'] == chat_id]
        
        if len(chat) == 0:
            return jsonify({'error': 'Chat not found'}), 404
        
        chat_data = chat.iloc[0].to_dict()
        
        # Parse messages
        messages = json.loads(chat_data['messages']) if chat_data['messages'] else []
        chat_data['messages'] = messages
        
        return jsonify({
            'chat': chat_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/chats', methods=['GET'])
def get_all_chats():
    """Get all chat instances"""
    try:
        user_id = request.args.get('user_id')
        
        filtered_chats = chats_df.copy()
        
        if user_id:
            filtered_chats = filtered_chats[filtered_chats['user_id'] == user_id]
        
        # Parse messages for each chat
        chats_list = []
        for _, chat in filtered_chats.iterrows():
            chat_dict = chat.to_dict()
            chat_dict['messages'] = json.loads(chat_dict['messages']) if chat_dict['messages'] else []
            chat_dict['message_count'] = len(chat_dict['messages'])
            chats_list.append(chat_dict)
        
        return jsonify({
            'chats': chats_list,
            'total': len(chats_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat instance"""
    global chats_df
    
    try:
        initial_len = len(chats_df)
        chats_df = chats_df[chats_df['chat_id'] != chat_id]
        
        if len(chats_df) == initial_len:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Save
        data_manager.save_chats(chats_df)
        
        return jsonify({
            'message': 'Chat deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/rag/retrain', methods=['POST'])
def retrain_rag():
    """Retrain RAG engine with latest program data"""
    global rag_engine, programs_df
    
    try:
        # Reload programs
        programs_df = data_manager.load_programs()
        
        # Update and retrain RAG engine
        rag_engine.update_programs(programs_df)
        
        return jsonify({
            'message': 'RAG engine retrained successfully',
            'programs_count': len(programs_df)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/rag/search', methods=['POST'])
def rag_search():
    """Direct RAG search without chat context"""
    try:
        data = request.get_json()
        
        if 'query' not in data:
            return jsonify({'error': 'Query required'}), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        # Search using RAG
        results = rag_engine.search(query, top_k=top_k)
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/chat/quick-ask', methods=['POST'])
def quick_ask():
    """Quick question without creating a chat instance"""
    try:
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({'error': 'Message required'}), 400
        
        # Get RAG response
        response = rag_engine.chat(data['message'])
        
        return jsonify({
            'response': response['response'],
            'programs': response.get('programs', []),
            'count': response.get('count', 0)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500