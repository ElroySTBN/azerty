"""
Dashboard Admin Ultra-Simple - Reputalys
Gestion des conversations et réponses aux clients
"""
from flask import Flask, render_template_string, request, redirect, session, jsonify
from functools import wraps
import sqlite3
from datetime import datetime
import asyncio
import os

# Importer DB_PATH et fonctions de connexion depuis bot_simple
from bot_simple import DB_PATH, USE_SUPABASE, _connect, _execute, get_pricing, reload_pricing

# Import conditionnel pour RealDictCursor (seulement si Supabase disponible)
try:
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    RealDictCursor = None

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'lebonmot-secret-key-2024')

def _connect_db():
    """Connexion à la base de données (Supabase PostgreSQL ou SQLite)"""
    return _connect()

# Référence au bot pour envoyer des messages
bot_app = None
bot_loop = None

def set_bot(application, loop):
    """Configure le bot pour pouvoir envoyer des messages"""
    global bot_app, bot_loop
    bot_app = application
    bot_loop = loop

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health')
def health():
    """Endpoint de santé pour Railway"""
    return jsonify({'status': 'healthy', 'service': 'Reputalys'}), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        if request.form.get('password') == admin_password:
            session['logged_in'] = True
            return redirect('/')
        return render_template_string(LOGIN_TEMPLATE, error="Mot de passe incorrect")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
@login_required
def dashboard():
    """Dashboard principal - Vue d'ensemble avec onglets"""
    view = request.args.get('view', 'overview')  # overview, conversations, orders, pricing
    
    # Si vue pricing, charger les prix directement
    if view == 'pricing':
        pricing_data = get_pricing()
        stats = {
            'total_orders': 0,
            'total_clients': 0,
            'total_messages': 0
        }
        return render_template_string(
            DASHBOARD_TEMPLATE, 
            conversations=[],
            orders=[],
            stats=stats,
            view=view,
            pricing=pricing_data
        )
    
    # Connexion optimisée pour autres vues
    conn = _connect_db()
    # Détecter le type de DB depuis la connexion
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    if is_postgres and PSYCOPG2_AVAILABLE:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Stats globales optimisées (une seule requête au lieu de 3)
    _execute(cursor, '''
        SELECT 
            COUNT(CASE WHEN service_type IS NOT NULL THEN 1 END) as total_orders,
            COUNT(DISTINCT telegram_id) as total_clients,
            (SELECT COUNT(*) FROM messages WHERE sender = 'client') as total_messages
        FROM conversations
    ''')
    stats_row = cursor.fetchone()
    total_orders = stats_row['total_orders'] or 0
    total_clients = stats_row['total_clients'] or 0
    total_messages = stats_row['total_messages'] or 0
    
    # Requête optimisée pour conversations avec LEFT JOIN au lieu de sous-requêtes
    _execute(cursor, '''
        SELECT 
            c.*,
            COUNT(m.id) as message_count,
            MAX(m.created_at) as last_message_time,
               (SELECT message FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message
        FROM conversations c
        LEFT JOIN messages m ON m.conversation_id = c.id
        GROUP BY c.id
        ORDER BY c.created_at DESC
    ''')
    conversations = cursor.fetchall()
    
    # Requête simple pour les commandes
    _execute(cursor, '''
        SELECT *
        FROM conversations
        WHERE service_type IS NOT NULL
        ORDER BY created_at DESC
    ''')
    orders = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'total_orders': total_orders,
        'total_clients': total_clients,
        'total_messages': total_messages
    }
    
    return render_template_string(
        DASHBOARD_TEMPLATE, 
        conversations=conversations,
        orders=orders,
        stats=stats,
        view=view,
        pricing=None
    )

@app.route('/conversation/<int:conv_id>')
@login_required
def conversation(conv_id):
    """Affiche une conversation spécifique"""
    conn = _connect_db()
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    if is_postgres and PSYCOPG2_AVAILABLE:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Infos de la conversation
    _execute(cursor, 'SELECT * FROM conversations WHERE id = ?', (conv_id,))
    conv = cursor.fetchone()
    
    if not conv:
        return "Conversation introuvable", 404
    
    # Messages de la conversation
    _execute(cursor, '''
        SELECT * FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at ASC
    ''', (conv_id,))
    
    messages = cursor.fetchall()
    conn.close()
    
    return render_template_string(CONVERSATION_TEMPLATE, conv=conv, messages=messages)

@app.route('/conversation/<int:conv_id>/reply', methods=['POST'])
@login_required
def reply(conv_id):
    """Envoie une réponse au client"""
    message = request.form.get('message')
    
    if not message:
        return jsonify({'error': 'Message vide'}), 400
    
    # Récupérer le telegram_id
    conn = _connect_db()
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    if is_postgres and PSYCOPG2_AVAILABLE:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
    cursor = conn.cursor()
    _execute(cursor, 'SELECT telegram_id FROM conversations WHERE id = ?', (conv_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Conversation introuvable'}), 404
    
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    telegram_id = result['telegram_id'] if (is_postgres and isinstance(result, dict)) else result[0]
    
    # Sauvegarder le message en DB
    _execute(cursor, '''
        INSERT INTO messages (conversation_id, telegram_id, message, sender)
        VALUES (?, ?, ?, ?)
    ''', (conv_id, telegram_id, message, 'admin'))
    conn.commit()
    conn.close()
    
    # Envoyer via Telegram
    if bot_app and bot_loop:
        formatted_message = f"Support 👨‍💼 : {message}"
        
        async def send_message():
            try:
                await bot_app.bot.send_message(
                    chat_id=telegram_id,
                    text=formatted_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Erreur envoi message: {e}")
        
        asyncio.run_coroutine_threadsafe(send_message(), bot_loop)
    
    return redirect(f'/conversation/{conv_id}')

@app.route('/conversation/<int:conv_id>/template', methods=['POST'])
@login_required
def send_template(conv_id):
    """Envoie un template de message"""
    template_id = request.form.get('template_id')
    
    # Templates de messages
    templates = {
        'payment_crypto': '''💰 *Informations de paiement*

Veuillez effectuer le paiement à l'adresse suivante :

*Adresse crypto :* [VOTRE_ADRESSE_CRYPTO]

*Montant :* [MONTANT]
*Réseau :* [RESEAU]

Une fois le paiement effectué, merci de m'envoyer la confirmation de transaction (hash).''',
        'payment_received': '''✅ *Paiement reçu !*

Merci pour votre paiement. Votre commande est maintenant en cours de traitement.

*Délai estimé :* 48-72h

Je vous tiendrai informé dès que la commande sera livrée. N'hésitez pas si vous avez des questions !''',
        'order_confirmed': '''✅ *Commande confirmée !*

Votre commande a été bien reçue et est en cours de traitement.

*Récapitulatif :*
• Service : [SERVICE]
• Quantité : [QUANTITE]
• Prix : [PRIX]

*Délai estimé :* 48-72h

Je vous tiendrai informé de l'avancement !''',
        'follow_up': '''👋 Bonjour,

Souhaitez-vous un point sur l'avancement de votre commande ?

N'hésitez pas si vous avez des questions !'''
    }
    
    if template_id not in templates:
        return jsonify({'error': 'Template introuvable'}), 400
    
    message = templates[template_id]
    
    # Récupérer le telegram_id et infos commande pour remplacer les variables
    conn = _connect_db()
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    if is_postgres and PSYCOPG2_AVAILABLE:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    _execute(cursor, 'SELECT * FROM conversations WHERE id = ?', (conv_id,))
    conv = cursor.fetchone()
    
    if not conv:
        conn.close()
        return jsonify({'error': 'Conversation introuvable'}), 404
    
    telegram_id = conv['telegram_id']
    
    # Remplacer les variables [VARIABLE] par les valeurs réelles
    message = message.replace('[SERVICE]', conv.get('service_type', 'Service'))
    message = message.replace('[QUANTITE]', str(conv.get('quantity', '?')))
    message = message.replace('[PRIX]', conv.get('estimated_price', 'À calculer'))
    message = message.replace('[MONTANT]', conv.get('estimated_price', 'À calculer'))
    message = message.replace('[VOTRE_ADRESSE_CRYPTO]', 'VOTRE_ADRESSE_ICI')  # À configurer
    message = message.replace('[RESEAU]', 'Bitcoin / Ethereum / USDT')
    
    # Sauvegarder le message en DB
    _execute(cursor, '''
        INSERT INTO messages (conversation_id, telegram_id, message, sender)
        VALUES (?, ?, ?, ?)
    ''', (conv_id, telegram_id, message, 'admin'))
    conn.commit()
    conn.close()
    
    # Envoyer via Telegram
    if bot_app and bot_loop:
        formatted_message = f"Support 👨‍💼 : {message}"
        
        async def send_message():
            try:
                await bot_app.bot.send_message(
                    chat_id=telegram_id,
                    text=formatted_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Erreur envoi message: {e}")
        
        asyncio.run_coroutine_threadsafe(send_message(), bot_loop)
    
    return redirect(f'/conversation/{conv_id}')

# Templates HTML
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - Reputalys Admin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        h1 { text-align: center; margin-bottom: 30px; color: #333; }
        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 20px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover { background: #5568d3; }
        .error { color: red; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🔐 Reputalys Admin</h1>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="Mot de passe" required autofocus>
            <button type="submit">Se connecter</button>
        </form>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Reputalys</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            display: block;
            margin-bottom: 8px;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            text-decoration: none;
        }
        .tab:hover { color: #667eea; }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: 600;
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.2s;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .card-title {
            font-weight: 600;
            font-size: 16px;
        }
        .badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            background: #667eea;
            color: white;
        }
        .badge-success { background: #28a745; }
        .badge-warning { background: #ffc107; color: #333; }
        .card-body { color: #666; font-size: 14px; line-height: 1.6; }
        .card-meta {
            display: flex;
            gap: 15px;
            margin-top: 10px;
            font-size: 13px;
            color: #999;
        }
        .telegram-id {
            font-family: monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }
        .btn-logout {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            transition: background 0.3s;
        }
        .btn-logout:hover { background: rgba(255,255,255,0.3); }
        .empty {
            text-align: center;
            padding: 60px 20px;
            color: #999;
            background: white;
            border-radius: 8px;
        }
        .section-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>📊 Reputalys - Admin Dashboard</h1>
            <a href="/logout" class="btn-logout">Déconnexion</a>
        </div>
    </div>
    
    <div class="container">
        <!-- Stats Overview -->
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-value">{{ stats.total_orders }}</span>
                <span class="stat-label">Commandes</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{{ stats.total_clients }}</span>
                <span class="stat-label">Clients</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{{ stats.total_messages }}</span>
                <span class="stat-label">Messages</span>
            </div>
        </div>
        
        <!-- Tabs -->
        <div class="tabs">
            <a href="/?view=overview" class="tab {% if view == 'overview' %}active{% endif %}">
                📋 Vue d'ensemble
            </a>
            <a href="/?view=orders" class="tab {% if view == 'orders' %}active{% endif %}">
                🛒 Commandes ({{ stats.total_orders }})
            </a>
            <a href="/?view=conversations" class="tab {% if view == 'conversations' %}active{% endif %}">
                💬 Conversations
            </a>
            <a href="/?view=pricing" class="tab {% if view == 'pricing' %}active{% endif %}">
                💰 Prix
            </a>
        </div>
        
        <!-- Content based on view -->
        {% if view == 'overview' %}
            <h2 class="section-title">📋 Dernières Commandes</h2>
            {% if orders %}
                {% for order in orders[:5] %}
                <div class="card" onclick="window.location.href='/conversation/{{ order.id }}'">
                    <div class="card-header">
                        <div class="card-title">
                            👤 {{ order.first_name or 'Client' }}
                            {% if order.username %}<small>@{{ order.username }}</small>{% endif %}
                        </div>
                        <span class="badge badge-success">{{ order.service_type }}</span>
                    </div>
                    <div class="card-body">
                        📦 <strong>{{ order.quantity }}</strong> • 💰 {{ order.estimated_price or 'À calculer' }}
                    </div>
                    <div class="card-meta">
                        <span>🆔 <span class="telegram-id">{{ order.telegram_id }}</span></span>
                        <span>🕐 {{ order.created_at }}</span>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">📭 Aucune commande pour le moment</div>
            {% endif %}
            
            <h2 class="section-title" style="margin-top: 40px;">💬 Dernières Conversations</h2>
            {% if conversations %}
                {% for conv in conversations[:5] %}
                <div class="card" onclick="window.location.href='/conversation/{{ conv.id }}'">
                    <div class="card-header">
                        <div class="card-title">
                            👤 {{ conv.first_name or 'Client' }}
                            {% if conv.username %}<small>@{{ conv.username }}</small>{% endif %}
                        </div>
                        <span class="badge">{{ conv.message_count }} messages</span>
                    </div>
                    <div class="card-body">
                        {% if conv.last_message %}
                        💬 "{{ conv.last_message[:80] }}..."
                        {% endif %}
                    </div>
                    <div class="card-meta">
                        <span>🆔 <span class="telegram-id">{{ conv.telegram_id }}</span></span>
                        <span>🕐 {{ conv.created_at }}</span>
                    </div>
                </div>
                {% endfor %}
            {% endif %}
        
        {% elif view == 'orders' %}
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 class="section-title" style="margin: 0;">🛒 Toutes les Commandes</h2>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="searchOrders" placeholder="🔍 Rechercher..." style="padding: 8px 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 14px;" onkeyup="filterOrders()">
                    <select id="filterService" onchange="filterOrders()" style="padding: 8px 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 14px;">
                        <option value="">Tous les services</option>
                        <option value="google">Avis Google</option>
                        <option value="trustpilot">Trustpilot</option>
                        <option value="forum">Forum</option>
                        <option value="autre_plateforme">Autre plateforme</option>
                        <option value="suppression">Suppression</option>
                    </select>
                </div>
            </div>
            {% if orders %}
                <div id="ordersList">
                {% for order in orders %}
                    <div class="card order-card" onclick="window.location.href='/conversation/{{ order.id }}'" data-service="{{ order.service_type }}" data-search="{{ (order.first_name or '') + ' ' + (order.username or '') + ' ' + (order.service_type or '') + ' ' + (order.quantity or '') + ' ' + (order.estimated_price or '') }}">
                    <div class="card-header">
                        <div class="card-title">
                            👤 {{ order.first_name or 'Client' }}
                            {% if order.username %}<small>@{{ order.username }}</small>{% endif %}
                        </div>
                        <span class="badge badge-success">{{ order.service_type }}</span>
                    </div>
                    <div class="card-body">
                        📦 Quantité : <strong>{{ order.quantity }}</strong><br>
                        💰 Prix estimé : {{ order.estimated_price or 'À calculer' }}<br>
                            {% if order.link and order.link != 'Aucun' %}🔗 <a href="{{ order.link }}" target="_blank" onclick="event.stopPropagation();">{{ order.link[:50] }}...</a>{% endif %}
                    </div>
                    <div class="card-meta">
                        <span>🆔 <span class="telegram-id">{{ order.telegram_id }}</span></span>
                        <span>🕐 {{ order.created_at }}</span>
                    </div>
                </div>
                {% endfor %}
                </div>
            {% else %}
                <div class="empty">📭 Aucune commande pour le moment</div>
            {% endif %}
            
            <script>
                function filterOrders() {
                    const search = document.getElementById('searchOrders').value.toLowerCase();
                    const filter = document.getElementById('filterService').value.toLowerCase();
                    const cards = document.querySelectorAll('.order-card');
                    
                    cards.forEach(card => {
                        const serviceMatch = !filter || card.dataset.service?.toLowerCase() === filter;
                        const searchMatch = !search || card.dataset.search?.toLowerCase().includes(search);
                        
                        if (serviceMatch && searchMatch) {
                            card.style.display = 'block';
                        } else {
                            card.style.display = 'none';
                        }
                    });
                }
            </script>
        
        {% elif view == 'conversations' %}
            <h2 class="section-title">💬 Toutes les Conversations</h2>
            {% if conversations %}
                {% for conv in conversations %}
                <div class="card" onclick="window.location.href='/conversation/{{ conv.id }}'">
                    <div class="card-header">
                        <div class="card-title">
                            👤 {{ conv.first_name or 'Client' }}
                            {% if conv.username %}<small>@{{ conv.username }}</small>{% endif %}
                        </div>
                        <span class="badge">{{ conv.message_count }} messages</span>
                    </div>
                    <div class="card-body">
                        {% if conv.service_type %}
                        📋 Service : <strong>{{ conv.service_type }}</strong> • Quantité : {{ conv.quantity }}<br>
                        {% endif %}
                        {% if conv.last_message %}
                        💬 "{{ conv.last_message[:80] }}..."
                        {% endif %}
                    </div>
                    <div class="card-meta">
                        <span>🆔 <span class="telegram-id">{{ conv.telegram_id }}</span></span>
                        <span>🕐 {{ conv.created_at }}</span>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">📭 Aucune conversation pour le moment</div>
            {% endif %}
        
        {% elif view == 'pricing' %}
            <h2 class="section-title">💰 Gestion des Prix</h2>
            {% if request.args.get('success') %}
            <div style="margin-bottom: 20px; padding: 15px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 4px; color: #155724;">
                ✅ <strong>Prix enregistrés avec succès !</strong> Les modifications sont actives immédiatement.
            </div>
            {% endif %}
            <p style="margin-bottom: 20px; color: #666;">Modifiez les prix de vos services. Les modifications sont enregistrées immédiatement et persistent même après redéploiement.</p>
            
            <form method="POST" action="/pricing/update" style="background: white; padding: 20px; border-radius: 8px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 2px solid #e0e0e0;">
                            <th style="text-align: left; padding: 12px; font-weight: 600;">Service</th>
                            <th style="text-align: left; padding: 12px; font-weight: 600;">Nom Affiché</th>
                            <th style="text-align: left; padding: 12px; font-weight: 600;">Prix</th>
                            <th style="text-align: left; padding: 12px; font-weight: 600;">Devise</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if pricing %}
                            {% for service_key, service_info in pricing.items() %}
                            <tr style="border-bottom: 1px solid #f0f0f0;">
                                <td style="padding: 12px; font-weight: 500;">{{ service_key }}</td>
                                <td style="padding: 12px;">
                                    <input type="text" name="name_{{ service_key }}" value="{{ service_info.name }}" 
                                           style="width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 4px;" required>
                                </td>
                                <td style="padding: 12px;">
                                    <input type="text" name="price_{{ service_key }}" value="{{ service_info.price }}" 
                                           placeholder="18 ou Sur devis" 
                                           style="width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 4px;" required>
                                </td>
                                <td style="padding: 12px;">
                                    <input type="text" name="currency_{{ service_key }}" value="{{ service_info.currency or 'EUR' }}" 
                                           style="width: 80px; padding: 8px; border: 2px solid #ddd; border-radius: 4px;">
                                </td>
                            </tr>
                            {% endfor %}
                        {% endif %}
                    </tbody>
                </table>
                
                <div style="margin-top: 20px; text-align: right;">
                    <button type="submit" style="background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: 600;">
                        💾 Enregistrer les Modifications
                    </button>
                </div>
            </form>
            
            <div style="margin-top: 20px; padding: 15px; background: #fffbea; border-left: 4px solid #ffd700; border-radius: 4px;">
                <strong>💡 Note :</strong> Les prix sont stockés dans la base de données (Supabase ou SQLite). 
                Ils persistent même après redéploiement et sont utilisés immédiatement par le bot.
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

CONVERSATION_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Conversation - Reputalys</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .header {
            background: #667eea;
            color: white;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .back-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
        }
        .info-panel {
            background: white;
            padding: 20px;
            border-bottom: 1px solid #ddd;
        }
        .info-row { margin: 8px 0; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            word-wrap: break-word;
        }
        .message-client {
            background: #e5e5ea;
            align-self: flex-start;
        }
        .message-admin {
            background: #667eea;
            color: white;
            align-self: flex-end;
        }
        .message-system {
            background: #fffbea;
            border: 1px solid #ffd700;
            align-self: center;
            font-size: 13px;
            color: #666;
        }
        .reply-form {
            background: white;
            padding: 20px;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        .reply-form {
            background: white;
            padding: 20px;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        .reply-form textarea {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            resize: none;
            font-family: inherit;
            font-size: 14px;
        }
        .reply-form button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            white-space: nowrap;
        }
        .reply-form button:hover {
            background: #5568d3;
        }
        .template-buttons {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .template-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }
        .template-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="back-btn">← Retour</a>
        <h2>💬 {{ conv.first_name or 'Client' }} {% if conv.username %}(@{{ conv.username }}){% endif %}</h2>
    </div>
    
    {% if conv.service_type %}
    <div class="info-panel">
        <div class="info-row">📋 <strong>Service :</strong> {{ conv.service_type }}</div>
        <div class="info-row">🔢 <strong>Quantité :</strong> {{ conv.quantity }}</div>
        {% if conv.link %}<div class="info-row">🔗 <strong>Lien :</strong> {{ conv.link }}</div>{% endif %}
        {% if conv.details %}<div class="info-row">📝 <strong>Détails :</strong> {{ conv.details }}</div>{% endif %}
        {% if conv.estimated_price %}<div class="info-row">💰 <strong>Prix estimé :</strong> {{ conv.estimated_price }}</div>{% endif %}
    </div>
    {% endif %}
    
    <div class="messages" id="messages">
        {% for msg in messages %}
        <div class="message message-{{ msg.sender }}">
            {{ msg.message }}
            <div style="font-size: 11px; opacity: 0.7; margin-top: 5px;">
                {{ msg.created_at }}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div style="background: white; padding: 15px; border-top: 1px solid #ddd;">
        <div style="margin-bottom: 15px;">
            <div style="font-weight: 600; margin-bottom: 10px; color: #667eea;">📝 Templates rapides :</div>
            <div class="template-buttons">
                <button type="button" onclick="insertTemplate('payment_crypto')" class="template-btn" style="background: #667eea; color: white;">💰 Paiement Crypto</button>
                <button type="button" onclick="insertTemplate('payment_received')" class="template-btn" style="background: #28a745; color: white;">✅ Paiement reçu</button>
                <button type="button" onclick="insertTemplate('order_confirmed')" class="template-btn" style="background: #17a2b8; color: white;">✅ Commande confirmée</button>
                <button type="button" onclick="insertTemplate('follow_up')" class="template-btn" style="background: #ffc107; color: #333;">👋 Suivi</button>
            </div>
        </div>
    </div>
    
    <form class="reply-form" method="POST" action="/conversation/{{ conv.id }}/reply">
        <textarea name="message" id="messageTextarea" rows="4" placeholder="Votre réponse..." required></textarea>
        <button type="submit">Envoyer ➤</button>
    </form>
    
    <script>
        // Auto-scroll vers le bas
        const messages = document.getElementById('messages');
        messages.scrollTop = messages.scrollHeight;
        
        // Templates de messages avec valeurs réelles (rendues côté serveur)
        const convData = {
            service: '{{ conv.service_type or "Service" }}',
            quantity: '{{ conv.quantity or "?" }}',
            price: '{{ conv.estimated_price or "À calculer" }}'
        };
        
        const templates = {
            'payment_crypto': `💰 *Informations de paiement*

Veuillez effectuer le paiement à l'adresse suivante :

*Adresse crypto :* [VOTRE_ADRESSE_CRYPTO]

*Montant :* ` + convData.price + `
*Réseau :* Bitcoin / Ethereum / USDT

Une fois le paiement effectué, merci de m'envoyer la confirmation de transaction (hash).`,
            'payment_received': `✅ *Paiement reçu !*

Merci pour votre paiement. Votre commande est maintenant en cours de traitement.

*Délai estimé :* 48-72h

Je vous tiendrai informé dès que la commande sera livrée. N'hésitez pas si vous avez des questions !`,
            'order_confirmed': `✅ *Commande confirmée !*

Votre commande a été bien reçue et est en cours de traitement.

*Récapitulatif :*
• Service : ` + convData.service + `
• Quantité : ` + convData.quantity + `
• Prix : ` + convData.price + `

*Délai estimé :* 48-72h

Je vous tiendrai informé de l'avancement !`,
            'follow_up': `👋 Bonjour,

Souhaitez-vous un point sur l'avancement de votre commande ?

N'hésitez pas si vous avez des questions !`
        };
        
        function insertTemplate(templateId) {
            const textarea = document.getElementById('messageTextarea');
            let template = templates[templateId];
            textarea.value = template;
            textarea.focus();
        }
    </script>
</body>
</html>
'''

def create_simple_dashboard():
    """Retourne l'app Flask"""
    return app

