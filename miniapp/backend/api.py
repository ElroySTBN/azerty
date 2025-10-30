"""
API Flask pour la Telegram Mini App Le Bon Mot
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import hmac
import json
import urllib.parse
import sys
import os

# Ajouter le répertoire parent au PYTHONPATH pour importer la database existante
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.database import (
    init_database, 
    get_or_create_client, 
    create_order,
    get_client_orders,
    save_support_message,
    update_client_username
)

app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

# Token du bot (pour valider initData)
BOT_TOKEN = os.getenv('CLIENT_BOT_TOKEN', '')

def validate_telegram_data(init_data: str) -> dict:
    """
    Valide les données Telegram WebApp initData
    Retourne les données utilisateur si valides, None sinon
    """
    try:
        # Parser initData
        parsed_data = urllib.parse.parse_qs(init_data)
        
        # Extraire hash et créer data_check_string
        received_hash = parsed_data.get('hash', [''])[0]
        data_check_arr = []
        
        for key, value in parsed_data.items():
            if key != 'hash':
                data_check_arr.append(f"{key}={value[0]}")
        
        data_check_arr.sort()
        data_check_string = '\n'.join(data_check_arr)
        
        # Calculer le hash attendu
        secret_key = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Vérifier
        if received_hash == expected_hash:
            user_data = json.loads(parsed_data.get('user', ['{}'])[0])
            return user_data
        
        return None
    except Exception as e:
        print(f"Validation error: {e}")
        return None

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Authentifie un utilisateur Telegram"""
    data = request.json
    init_data = data.get('initData', '')
    user_data = data.get('user', {})
    
    # En développement, accepter sans validation stricte
    if not BOT_TOKEN or os.getenv('ENV') == 'development':
        telegram_id = user_data.get('id')
        if not telegram_id:
            return jsonify({'success': False, 'error': 'No user ID'}), 400
    else:
        # En production, valider initData
        validated_user = validate_telegram_data(init_data)
        if not validated_user:
            return jsonify({'success': False, 'error': 'Invalid initData'}), 403
        telegram_id = validated_user['id']
        user_data = validated_user
    
    # Créer ou récupérer le client
    client = get_or_create_client(telegram_id)
    
    # Mettre à jour le username si fourni
    if user_data.get('username'):
        update_client_username(telegram_id, user_data['username'])
    
    return jsonify({
        'success': True,
        'user': {
            'telegram_id': telegram_id,
            'client_id': client['client_id'],
            'username': user_data.get('username', ''),
            'first_name': user_data.get('first_name', '')
        }
    })

@app.route('/api/orders', methods=['POST'])
def create_new_order():
    """Crée une nouvelle commande"""
    data = request.json
    
    try:
        user_id = data['user_id']
        order_type = data.get('order_type', 'reviews')
        platform = data['platform']
        quantity = int(data['quantity'])
        target_link = data['target_link']
        content_generation = data.get('content_generation', False)
        instructions = data.get('instructions', '')
        forum_subject = data.get('forum_subject', '')
        
        # Récupérer le client
        client = get_or_create_client(user_id)
        
        # Préparer le brief
        if order_type == 'forum' and forum_subject:
            brief = f"Sujet: {forum_subject}\n\nInstructions: {instructions}"
        else:
            brief = instructions
        
        # Créer la commande
        order_id = create_order(
            client['client_id'],
            platform,
            quantity,
            target_link,
            brief,
            order_type=order_type
        )
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Commande créée avec succès'
        })
        
    except Exception as e:
        print(f"Order creation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/orders/<client_id>', methods=['GET'])
def get_orders(client_id):
    """Récupère les commandes d'un client"""
    try:
        orders = get_client_orders(client_id)
        return jsonify({
            'success': True,
            'orders': orders
        })
    except Exception as e:
        print(f"Fetch orders error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/support', methods=['POST'])
def contact_support():
    """Envoie un message au support"""
    data = request.json
    
    try:
        client_id = data['client_id']
        message = data['message']
        telegram_username = data.get('telegram_username', '')
        
        save_support_message(client_id, message, 'client', telegram_username)
        
        return jsonify({
            'success': True,
            'message': 'Message envoyé au support'
        })
        
    except Exception as e:
        print(f"Support message error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'LeBonMot Mini App API'})

if __name__ == '__main__':
    # Initialiser la base de données
    init_database()
    
    # Démarrer le serveur
    port = int(os.getenv('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=True)

