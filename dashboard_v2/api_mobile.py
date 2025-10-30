"""
API Backend pour le Dashboard Mobile
"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from functools import wraps
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.database import (
    get_all_orders,
    get_order_by_id,
    get_client_by_id,
    get_support_messages,
    save_support_message,
    get_order_reviews,
    get_db
)

mobile = Blueprint('mobile', __name__, 
                   template_folder='templates',
                   static_folder='static',
                   url_prefix='/mobile')

# Login simple (optionnel, pour protéger l'accès)
def mobile_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Pour le MVP, on peut simplifier ou utiliser un PIN simple
        if not session.get('mobile_logged_in'):
            # Rediriger vers une page de login ou utiliser l'ancien système
            session['mobile_logged_in'] = True  # Auto-login pour le MVP
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# ROUTES PRINCIPALES (Pages HTML)
# ============================================

@mobile.route('/')
@mobile_login_required
def dashboard():
    """Dashboard principal mobile"""
    return render_template('mobile_dashboard.html')

@mobile.route('/order/<order_id>')
@mobile_login_required
def order_details(order_id):
    """Détails d'une commande"""
    order = get_order_by_id(order_id)
    if not order:
        return "Commande introuvable", 404
    
    client = get_client_by_id(order['client_id'])
    reviews = get_order_reviews(order_id)
    
    return render_template('mobile_order.html', 
                         order=order, 
                         client=client,
                         reviews=reviews)

@mobile.route('/chat/<client_id>')
@mobile_login_required
def chat(client_id):
    """Page de chat avec un client"""
    client = get_client_by_id(client_id)
    if not client:
        return "Client introuvable", 404
    
    messages = get_support_messages(client_id)
    
    return render_template('mobile_chat.html', 
                         client=client,
                         messages=messages)

# ============================================
# API ENDPOINTS (JSON)
# ============================================

@mobile.route('/api/orders')
def api_orders():
    """Liste de toutes les commandes (API JSON)"""
    try:
        orders = get_all_orders()
        return jsonify({
            'success': True,
            'orders': orders
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile.route('/api/orders/<status>')
def api_orders_by_status(status):
    """Commandes filtrées par statut"""
    try:
        orders = get_all_orders()
        filtered = [o for o in orders if o['status'] == status]
        return jsonify({
            'success': True,
            'orders': filtered
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile.route('/api/messages')
def api_messages():
    """Liste des conversations (clients avec messages)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Récupérer les clients qui ont des messages
        cursor.execute('''
            SELECT 
                c.client_id,
                c.telegram_username,
                MAX(sm.created_at) as last_message_time,
                (SELECT message FROM support_messages 
                 WHERE client_id = c.client_id 
                 ORDER BY created_at DESC LIMIT 1) as last_message,
                COUNT(CASE WHEN sm.sender = 'client' AND sm.read = 0 THEN 1 END) as unread_count
            FROM clients c
            INNER JOIN support_messages sm ON c.client_id = sm.client_id
            GROUP BY c.client_id
            ORDER BY last_message_time DESC
        ''')
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'client_id': row[0],
                'telegram_username': row[1],
                'last_message_time': row[2],
                'last_message': row[3],
                'unread_count': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile.route('/api/order/<order_id>/status', methods=['POST'])
def update_order_status(order_id):
    """Mettre à jour le statut d'une commande"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                'success': False,
                'error': 'Status requis'
            }), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE orders SET status = ? WHERE order_id = ?',
            (new_status, order_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Statut mis à jour'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile.route('/api/order/<order_id>/deliver', methods=['POST'])
def deliver_order(order_id):
    """Livrer une commande au client (via Telegram)"""
    try:
        # Mettre à jour le statut
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE orders SET status = ? WHERE order_id = ?',
            ('delivered', order_id)
        )
        conn.commit()
        conn.close()
        
        # TODO: Envoyer une notification au client via Telegram
        # (nécessite l'accès au bot Telegram)
        
        return jsonify({
            'success': True,
            'message': 'Commande livrée'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile.route('/api/chat/<client_id>/send', methods=['POST'])
def send_chat_message(client_id):
    """Envoyer un message à un client"""
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message requis'
            }), 400
        
        # Sauvegarder dans la DB
        save_support_message(client_id, message, 'admin')
        
        # TODO: Envoyer via Telegram Bot
        # (nécessite l'accès au bot Telegram avec client_bot_app)
        
        return jsonify({
            'success': True,
            'message': 'Message envoyé'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile.route('/api/subscribe', methods=['POST'])
def subscribe_push():
    """Enregistrer une subscription push"""
    try:
        subscription = request.json
        # TODO: Sauvegarder la subscription en DB pour envoyer des notifications
        # Pour l'instant, on retourne juste success
        return jsonify({
            'success': True,
            'message': 'Subscription enregistrée'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# FONCTION D'EXPORT (pour l'intégrer à main.py)
# ============================================

def setup_mobile_dashboard(app):
    """
    Intégrer le dashboard mobile à l'application Flask principale
    
    Usage dans main.py:
        from dashboard_v2.api_mobile import setup_mobile_dashboard, mobile
        app.register_blueprint(mobile)
    """
    app.register_blueprint(mobile)
    return mobile

