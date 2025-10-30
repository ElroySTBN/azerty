"""
Application Flask unifiée pour Railway
Sert l'API, le frontend React compilé, ET le dashboard admin
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))
from src.database import (
    init_database, 
    get_or_create_client, 
    create_order,
    get_client_orders,
    save_support_message,
    update_client_username
)

# Créer l'app Flask qui sert TOUT
app = Flask(__name__, 
            static_folder='miniapp/frontend/dist',
            template_folder='templates')
CORS(app)

# Configuration pour les sessions (nécessaire pour le dashboard admin)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')

# Importer les routes du dashboard admin
from src.web_admin import (
    login_required, dashboard, login, logout,
    order_details, add_review, delete_review_route,
    import_reviews, delete_order_route, messages_list,
    client_messages, reply_to_client
)

# Enregistrer les routes admin avec le préfixe /admin
app.add_url_rule('/admin', 'admin_dashboard', dashboard)
app.add_url_rule('/admin/login', 'admin_login', login, methods=['GET', 'POST'])
app.add_url_rule('/admin/logout', 'admin_logout', logout)
app.add_url_rule('/admin/order/<order_id>', 'admin_order_details', order_details)
app.add_url_rule('/admin/order/<order_id>/add_review', 'admin_add_review', add_review, methods=['POST'])
app.add_url_rule('/admin/review/<int:review_id>/delete', 'admin_delete_review', delete_review_route, methods=['POST'])
app.add_url_rule('/admin/order/<order_id>/import', 'admin_import_reviews', import_reviews, methods=['POST'])
app.add_url_rule('/admin/order/<order_id>/delete', 'admin_delete_order', delete_order_route, methods=['POST'])
app.add_url_rule('/admin/messages', 'admin_messages_list', messages_list)
app.add_url_rule('/admin/messages/<client_id>', 'admin_client_messages', client_messages)
app.add_url_rule('/admin/messages/<client_id>/reply', 'admin_reply_to_client', reply_to_client, methods=['POST'])

BOT_TOKEN = os.getenv('CLIENT_BOT_TOKEN', '')

# ============================================
# ROUTES API (même que miniapp/backend/api.py)
# ============================================

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Authentifie un utilisateur Telegram"""
    data = request.json
    user_data = data.get('user', {})
    telegram_id = user_data.get('id')
    
    if not telegram_id:
        return jsonify({'success': False, 'error': 'No user ID'}), 400
    
    client = get_or_create_client(telegram_id)
    
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
        
        client = get_or_create_client(user_id)
        
        if order_type == 'forum' and forum_subject:
            brief = f"Sujet: {forum_subject}\n\nInstructions: {instructions}"
        else:
            brief = instructions
        
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders/<client_id>', methods=['GET'])
def get_orders(client_id):
    """Récupère les commandes d'un client"""
    try:
        orders = get_client_orders(client_id)
        return jsonify({'success': True, 'orders': orders})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/support', methods=['POST'])
def contact_support():
    """Envoie un message au support"""
    data = request.json
    
    try:
        client_id = data['client_id']
        message = data['message']
        telegram_username = data.get('telegram_username', '')
        
        save_support_message(client_id, message, 'client', telegram_username)
        
        return jsonify({'success': True, 'message': 'Message envoyé au support'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# SERVIR LE FRONTEND REACT (fichiers statiques)
# ============================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Sert le frontend React compilé"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'LeBonMot Full Stack'})

# NE PAS EXÉCUTER ICI - main.py s'en charge
# Le Flask sera intégré au démarrage principal

