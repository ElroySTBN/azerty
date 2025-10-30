"""
Dashboard Admin Ultra-Simple - Le Bon Mot
Gestion des conversations et réponses aux clients
"""
from flask import Flask, render_template_string, request, redirect, session, jsonify
from functools import wraps
import sqlite3
from datetime import datetime
import asyncio

app = Flask(__name__)
app.secret_key = 'lebonmot-secret-key-2024'

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
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
    """Dashboard principal - Liste des conversations"""
    conn = sqlite3.connect('lebonmot_simple.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupérer toutes les conversations
    cursor.execute('''
        SELECT c.*, 
               (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count,
               (SELECT message FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message
        FROM conversations c
        ORDER BY c.created_at DESC
    ''')
    
    conversations = cursor.fetchall()
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE, conversations=conversations)

@app.route('/conversation/<int:conv_id>')
@login_required
def conversation(conv_id):
    """Affiche une conversation spécifique"""
    conn = sqlite3.connect('lebonmot_simple.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Infos de la conversation
    cursor.execute('SELECT * FROM conversations WHERE id = ?', (conv_id,))
    conv = cursor.fetchone()
    
    if not conv:
        return "Conversation introuvable", 404
    
    # Messages de la conversation
    cursor.execute('''
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
    conn = sqlite3.connect('lebonmot_simple.db')
    cursor = conn.cursor()
    cursor.execute('SELECT telegram_id FROM conversations WHERE id = ?', (conv_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Conversation introuvable'}), 404
    
    telegram_id = result[0]
    
    # Sauvegarder le message en DB
    cursor.execute('''
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
    <title>Login - Le Bon Mot Admin</title>
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
        <h1>🔐 Le Bon Mot Admin</h1>
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
    <title>Dashboard - Le Bon Mot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
        }
        .header {
            background: #667eea;
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.2s;
        }
        .card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .card-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            background: #667eea;
            color: white;
        }
        .meta { color: #666; font-size: 14px; margin-top: 10px; }
        .btn-logout {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
        }
        .empty {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>💬 Conversations - Le Bon Mot</h1>
        <a href="/logout" class="btn-logout">Déconnexion</a>
    </div>
    
    <div class="container">
        {% if conversations %}
            {% for conv in conversations %}
            <div class="card" onclick="window.location.href='/conversation/{{ conv.id }}'">
                <div class="card-header">
                    <span>
                        👤 {{ conv.first_name or 'Client' }}
                        {% if conv.username %}(@{{ conv.username }}){% endif %}
                    </span>
                    <span class="badge">{{ conv.message_count }} messages</span>
                </div>
                {% if conv.service_type %}
                <p>📋 Service : <strong>{{ conv.service_type }}</strong> • Quantité : {{ conv.quantity }}</p>
                {% endif %}
                {% if conv.last_message %}
                <p class="meta">💬 "{{ conv.last_message[:100] }}..."</p>
                {% endif %}
                <p class="meta">🕐 {{ conv.created_at }}</p>
            </div>
            {% endfor %}
        {% else %}
            <div class="empty">
                <p>📭 Aucune conversation pour le moment</p>
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
    <title>Conversation - Le Bon Mot</title>
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
        .reply-form textarea {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            resize: none;
            font-family: inherit;
        }
        .reply-form button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
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
    
    <form class="reply-form" method="POST" action="/conversation/{{ conv.id }}/reply">
        <textarea name="message" rows="3" placeholder="Votre réponse..." required></textarea>
        <button type="submit">Envoyer ➤</button>
    </form>
    
    <script>
        // Auto-scroll vers le bas
        const messages = document.getElementById('messages');
        messages.scrollTop = messages.scrollHeight;
    </script>
</body>
</html>
'''

def create_simple_dashboard():
    """Retourne l'app Flask"""
    return app

