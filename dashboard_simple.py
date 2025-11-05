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

def get_crypto_addresses():
    """Charge toutes les adresses crypto depuis la base de données"""
    conn = None
    try:
        conn = _connect_db()
        is_postgres = hasattr(conn, 'get_dsn_parameters')
        if is_postgres and PSYCOPG2_AVAILABLE:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        # Adapter la condition is_active selon le type de DB
        # PostgreSQL utilise BOOLEAN (TRUE), SQLite utilise INTEGER (1)
        try:
            if is_postgres:
                _execute(cursor, "SELECT * FROM crypto_addresses WHERE is_active = TRUE ORDER BY name")
            else:
                _execute(cursor, 'SELECT * FROM crypto_addresses WHERE is_active = 1 ORDER BY name')
            addresses = cursor.fetchall()
            print(f"📋 Adresses crypto récupérées : {len(addresses)} adresse(s)")
        except Exception as e:
            # Si la table n'existe pas encore, retourner liste vide
            print(f"⚠️ Table crypto_addresses n'existe pas ou erreur : {e}")
            return []
        
        # Convertir en liste de dictionnaires pour faciliter le template
        result = []
        for addr in addresses:
            if is_postgres and isinstance(addr, dict):
                result.append({
                    'id': addr.get('id'),
                    'name': addr.get('name'),
                    'address': addr.get('address'),
                    'network': addr.get('network'),
                    'is_active': addr.get('is_active')
                })
            elif hasattr(addr, '__getitem__') and hasattr(addr, 'keys'):
                # SQLite Row object
                result.append({
                    'id': addr['id'],
                    'name': addr['name'],
                    'address': addr['address'],
                    'network': addr['network'],
                    'is_active': addr['is_active']
                })
            else:
                # Tuple fallback (id, name, address, network, is_active)
                result.append({
                    'id': addr[0] if len(addr) > 0 else None,
                    'name': addr[1] if len(addr) > 1 else '',
                    'address': addr[2] if len(addr) > 2 else '',
                    'network': addr[3] if len(addr) > 3 else '',
                    'is_active': addr[4] if len(addr) > 4 else True
                })
        return result
    except Exception as e:
        # En cas d'erreur, retourner liste vide
        print(f"Erreur get_crypto_addresses: {e}")
        return []
    finally:
        # TOUJOURS fermer la connexion
        if conn:
            try:
                conn.close()
            except:
                pass

def get_message_templates():
    """Charge tous les templates de messages depuis la base de données"""
    conn = None
    try:
        conn = _connect_db()
        is_postgres = hasattr(conn, 'get_dsn_parameters')
        if is_postgres and PSYCOPG2_AVAILABLE:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        try:
            _execute(cursor, 'SELECT * FROM message_templates ORDER BY template_key')
            templates_rows = cursor.fetchall()
        except Exception as e:
            print(f"⚠️ Table message_templates n'existe pas ou erreur : {e}")
            return {}
        
        # Convertir en dictionnaire {template_key: template_text}
        templates = {}
        for row in templates_rows:
            if is_postgres and isinstance(row, dict):
                key = row.get('template_key')
                text = row.get('template_text')
            elif hasattr(row, '__getitem__') and hasattr(row, 'keys'):
                key = row['template_key']
                text = row['template_text']
            else:
                key = row[1] if len(row) > 1 else None
                text = row[2] if len(row) > 2 else ''
            
            if key:
                templates[key] = text
        
        return templates
    except Exception as e:
        print(f"Erreur get_message_templates: {e}")
        return {}
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

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

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint pour récupérer les statistiques en JSON"""
    conn = None
    try:
        conn = _connect_db()
        is_postgres = hasattr(conn, 'get_dsn_parameters')
        if is_postgres and PSYCOPG2_AVAILABLE:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        # Stats globales optimisées
        _execute(cursor, '''
            SELECT 
                COUNT(CASE WHEN service_type IS NOT NULL THEN 1 END) as total_orders,
                COUNT(DISTINCT telegram_id) as total_clients,
                (SELECT COUNT(*) FROM messages WHERE sender = 'client') as total_messages
            FROM conversations
        ''')
        stats_row = cursor.fetchone()
        
        # Gérer les différents formats de résultats
        if is_postgres and isinstance(stats_row, dict):
            total_orders = stats_row.get('total_orders', 0) or 0
            total_clients = stats_row.get('total_clients', 0) or 0
            total_messages = stats_row.get('total_messages', 0) or 0
        elif hasattr(stats_row, '__getitem__') and hasattr(stats_row, 'keys'):
            total_orders = stats_row['total_orders'] or 0
            total_clients = stats_row['total_clients'] or 0
            total_messages = stats_row['total_messages'] or 0
        else:
            total_orders = (stats_row[0] if stats_row else 0) or 0
            total_clients = (stats_row[1] if stats_row and len(stats_row) > 1 else 0) or 0
            total_messages = (stats_row[2] if stats_row and len(stats_row) > 2 else 0) or 0
        
        return jsonify({
            'total_orders': total_orders,
            'total_clients': total_clients,
            'total_messages': total_messages,
            'timestamp': datetime.now().isoformat()
        })
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

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
    view = request.args.get('view', 'overview')  # overview, conversations, orders, pricing, crypto
    
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
            pricing=pricing_data,
            crypto_addresses=[]
        )
    
    # Si vue crypto, charger les adresses directement
    if view == 'crypto':
        crypto_addresses = get_crypto_addresses()
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
            pricing=None,
            crypto_addresses=crypto_addresses,
            templates=None
        )
    
    # Si vue templates, charger les templates
    if view == 'templates':
        templates = get_message_templates()
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
            pricing=None,
            crypto_addresses=[],
            templates=templates
        )
    
    # Connexion optimisée pour autres vues
    conn = None
    try:
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
        
        # Gérer les différents formats de résultats (PostgreSQL dict vs SQLite Row/tuple)
        if is_postgres and isinstance(stats_row, dict):
            total_orders = stats_row.get('total_orders', 0) or 0
            total_clients = stats_row.get('total_clients', 0) or 0
            total_messages = stats_row.get('total_messages', 0) or 0
        elif hasattr(stats_row, '__getitem__') and hasattr(stats_row, 'keys'):
            # SQLite Row object
            total_orders = stats_row['total_orders'] or 0
            total_clients = stats_row['total_clients'] or 0
            total_messages = stats_row['total_messages'] or 0
        else:
            # Tuple fallback (par index)
            total_orders = (stats_row[0] if stats_row else 0) or 0
            total_clients = (stats_row[1] if stats_row and len(stats_row) > 1 else 0) or 0
            total_messages = (stats_row[2] if stats_row and len(stats_row) > 2 else 0) or 0
        
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
            pricing=None,
            crypto_addresses=[],
            templates=None
        )
    finally:
        # TOUJOURS fermer la connexion
        if conn:
            try:
                conn.close()
            except:
                pass

@app.route('/conversation/<int:conv_id>')
@login_required
def conversation(conv_id):
    """Affiche une conversation spécifique"""
    conn = None
    try:
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
        
        # Charger les adresses crypto pour la sélection
        crypto_addresses = get_crypto_addresses()
        
        return render_template_string(CONVERSATION_TEMPLATE, conv=conv, messages=messages, crypto_addresses=crypto_addresses)
    finally:
        # TOUJOURS fermer la connexion
        if conn:
            try:
                conn.close()
            except:
                pass

@app.route('/conversation/<int:conv_id>/reply', methods=['POST'])
@login_required
def reply(conv_id):
    """Envoie une réponse au client"""
    message = request.form.get('message')
    
    if not message:
        return jsonify({'error': 'Message vide'}), 400
    
    conn = None
    try:
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
            return jsonify({'error': 'Conversation introuvable'}), 404
        
        telegram_id = result['telegram_id'] if (is_postgres and isinstance(result, dict)) else result[0]
        
        # Sauvegarder le message en DB
        _execute(cursor, '''
            INSERT INTO messages (conversation_id, telegram_id, message, sender)
            VALUES (?, ?, ?, ?)
        ''', (conv_id, telegram_id, message, 'admin'))
        conn.commit()
    finally:
        # TOUJOURS fermer la connexion
        if conn:
            try:
                conn.close()
            except:
                pass
    
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

@app.route('/pricing/update', methods=['POST'])
@login_required
def update_pricing():
    """Met à jour les prix depuis le dashboard"""
    conn = None
    try:
        conn = _connect_db()
        is_postgres = hasattr(conn, 'get_dsn_parameters')
        if is_postgres and PSYCOPG2_AVAILABLE:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        # Services disponibles
        services = ['google', 'trustpilot', 'forum', 'pagesjaunes', 'autre_plateforme', 'suppression']
        
        updated_count = 0
        for service_key in services:
            name = request.form.get(f'name_{service_key}')
            price = request.form.get(f'price_{service_key}')
            currency = request.form.get(f'currency_{service_key}', 'EUR')
            
            if name and price:
                # Vérifier si le service existe déjà
                _execute(cursor, 'SELECT id FROM pricing WHERE service_key = ?', (service_key,))
                exists = cursor.fetchone()
                
                if exists:
                    # Mettre à jour
                    _execute(cursor, '''
                        UPDATE pricing 
                        SET price = ?, currency = ?, name = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE service_key = ?
                    ''', (price, currency, name, service_key))
                else:
                    # Insérer
                    _execute(cursor, '''
                        INSERT INTO pricing (service_key, price, currency, name)
                        VALUES (?, ?, ?, ?)
                    ''', (service_key, price, currency, name))
                updated_count += 1
        
        conn.commit()
        
        # Recharger les prix dans le bot
        reload_pricing()
        
        return redirect('/?view=pricing&success=1')
    finally:
        # TOUJOURS fermer la connexion
        if conn:
            try:
                conn.close()
            except:
                pass

@app.route('/crypto/add', methods=['POST'])
@login_required
def add_crypto_address():
    """Ajoute une nouvelle adresse crypto"""
    name = request.form.get('name')
    address = request.form.get('address')
    network = request.form.get('network')
    
    if not name or not address or not network:
        return redirect('/?view=crypto&error=1')
    
    conn = None
    try:
        conn = _connect_db()
        is_postgres = hasattr(conn, 'get_dsn_parameters')
        if is_postgres and PSYCOPG2_AVAILABLE:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        # Adapter is_active selon le type de DB : PostgreSQL (BOOL) vs SQLite (INTEGER)
        is_active_value = True if is_postgres else 1
        
        # Vérifier que la table existe, sinon la créer
        try:
            _execute(cursor, '''
                INSERT INTO crypto_addresses (name, address, network, is_active)
                VALUES (?, ?, ?, ?)
            ''', (name, address, network, is_active_value))
            conn.commit()
            print(f"✅ Adresse crypto ajoutée : {name} ({network})")
        except Exception as e:
            # Si la table n'existe pas, la créer et réessayer
            print(f"⚠️ Erreur lors de l'insertion : {e}")
            if is_postgres:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS crypto_addresses (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        address TEXT NOT NULL,
                        network TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            else:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS crypto_addresses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        address TEXT NOT NULL,
                        network TEXT NOT NULL,
                        is_active INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            conn.commit()
            # Réessayer l'insertion
            _execute(cursor, '''
                INSERT INTO crypto_addresses (name, address, network, is_active)
                VALUES (?, ?, ?, ?)
            ''', (name, address, network, is_active_value))
            conn.commit()
            print(f"✅ Table créée et adresse crypto ajoutée : {name} ({network})")
        
        return redirect('/?view=crypto&success=1')
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout de l'adresse crypto : {e}")
        return redirect('/?view=crypto&error=1')
    finally:
        # TOUJOURS fermer la connexion
        if conn:
            try:
                conn.close()
            except:
                pass

@app.route('/crypto/delete/<int:addr_id>', methods=['POST'])
@login_required
def delete_crypto_address(addr_id):
    """Supprime une adresse crypto (soft delete en la désactivant)"""
    conn = None
    try:
        conn = _connect_db()
        is_postgres = hasattr(conn, 'get_dsn_parameters')
        if is_postgres and PSYCOPG2_AVAILABLE:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        _execute(cursor, '''
            UPDATE crypto_addresses 
            SET is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (False, addr_id))
        
        conn.commit()
        
        return redirect('/?view=crypto&success=1')
    finally:
        # TOUJOURS fermer la connexion
        if conn:
            try:
                conn.close()
            except:
                pass

@app.route('/conversation/<int:conv_id>/template', methods=['POST'])
@login_required
def send_template(conv_id):
    """Remplit le textarea avec un template de message (au lieu d'envoyer directement)"""
    template_id = request.form.get('template_id')
    crypto_address_id = request.form.get('crypto_address_id')  # ID de l'adresse sélectionnée
    
    if not template_id:
        return jsonify({'error': 'Template introuvable'}), 400
    
    # Charger les templates depuis la DB
    templates = get_message_templates()
    
    # Si pas de templates en DB, utiliser les valeurs par défaut
    if not templates:
        templates = {
            'payment_crypto': '''💰 *Informations de paiement*

Veuillez effectuer le paiement à l'adresse suivante :

*Adresse crypto :* [VOTRE_ADRESSE_CRYPTO]

*Montant :* [MONTANT]
*Réseau :* [RESEAU]

Une fois le paiement effectué, vous pouvez m'envoyer :
• Une capture d'écran de la confirmation de transaction (c'est la solution la plus simple)

Ou bien, si vous êtes à l'aise avec les cryptomonnaies :
• Le hash de la transaction (cette longue suite de caractères qui confirme votre paiement)''',
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
    conn = None
    try:
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
            return jsonify({'error': 'Conversation introuvable'}), 404
        
        # Gérer différents formats de résultats (PostgreSQL dict vs SQLite Row/tuple)
        if is_postgres and isinstance(conv, dict):
            telegram_id = conv.get('telegram_id')
        elif hasattr(conv, '__getitem__') and hasattr(conv, 'keys'):
            # SQLite Row object
            telegram_id = conv['telegram_id']
        else:
            # Tuple fallback - trouver l'index de telegram_id (normalement colonne 1)
            telegram_id = conv[1] if conv and len(conv) > 1 else None
        
        # Fonction helper pour extraire valeur depuis conv selon format
        def get_conv_value(key, default=''):
            if is_postgres and isinstance(conv, dict):
                return conv.get(key, default)
            elif hasattr(conv, '__getitem__') and hasattr(conv, 'keys'):
                return conv.get(key, default) if hasattr(conv, 'get') else conv[key]
            else:
                # Tuple fallback - utiliser indices (service_type=3, quantity=4, estimated_price=7)
                index_map = {'service_type': 3, 'quantity': 4, 'estimated_price': 7}
                idx = index_map.get(key, -1)
                if idx >= 0 and conv and len(conv) > idx:
                    return conv[idx] or default
                return default
        
        # Remplacer les variables [VARIABLE] par les valeurs réelles
        message = message.replace('[SERVICE]', get_conv_value('service_type', 'Service'))
        message = message.replace('[QUANTITE]', str(get_conv_value('quantity', '?')))
        message = message.replace('[PRIX]', get_conv_value('estimated_price', 'À calculer'))
        message = message.replace('[MONTANT]', get_conv_value('estimated_price', 'À calculer'))
        
        # Pour payment_crypto, remplir l'adresse et le réseau si fournis
        if template_id == 'payment_crypto' and crypto_address_id:
            try:
                addr_id = int(crypto_address_id)
                if is_postgres:
                    _execute(cursor, "SELECT * FROM crypto_addresses WHERE id = ? AND is_active = TRUE", (addr_id,))
                else:
                    _execute(cursor, 'SELECT * FROM crypto_addresses WHERE id = ? AND is_active = 1', (addr_id,))
                
                crypto_addr = cursor.fetchone()
                if crypto_addr:
                    if is_postgres and isinstance(crypto_addr, dict):
                        crypto_address = crypto_addr.get('address', '')
                        crypto_network = crypto_addr.get('network', '')
                    elif hasattr(crypto_addr, '__getitem__') and hasattr(crypto_addr, 'keys'):
                        crypto_address = crypto_addr['address'] if 'address' in crypto_addr.keys() else (crypto_addr[2] if len(crypto_addr) > 2 else '')
                        crypto_network = crypto_addr['network'] if 'network' in crypto_addr.keys() else (crypto_addr[3] if len(crypto_addr) > 3 else '')
                    else:
                        crypto_address = crypto_addr[2] if len(crypto_addr) > 2 else ''
                        crypto_network = crypto_addr[3] if len(crypto_addr) > 3 else ''
                    
                    message = message.replace('[VOTRE_ADRESSE_CRYPTO]', crypto_address)
                    message = message.replace('[RESEAU]', crypto_network)
                else:
                    message = message.replace('[VOTRE_ADRESSE_CRYPTO]', 'VOTRE_ADRESSE_ICI')
                    message = message.replace('[RESEAU]', 'Bitcoin / Ethereum / USDT')
            except Exception as e:
                print(f"⚠️ Erreur récupération adresse crypto: {e}")
                message = message.replace('[VOTRE_ADRESSE_CRYPTO]', 'VOTRE_ADRESSE_ICI')
                message = message.replace('[RESEAU]', 'Bitcoin / Ethereum / USDT')
        elif template_id == 'payment_crypto':
            message = message.replace('[VOTRE_ADRESSE_CRYPTO]', 'VOTRE_ADRESSE_ICI')
            message = message.replace('[RESEAU]', 'Bitcoin / Ethereum / USDT')
        
        # Retourner le message rempli en JSON pour remplir le textarea
        return jsonify({'message': message})
    finally:
        # TOUJOURS fermer la connexion
        if conn:
            try:
                conn.close()
            except:
                pass

@app.route('/templates/update', methods=['POST'])
@login_required
def update_templates():
    """Met à jour les templates de messages depuis le dashboard"""
    conn = None
    try:
        conn = _connect_db()
        is_postgres = hasattr(conn, 'get_dsn_parameters')
        if is_postgres and PSYCOPG2_AVAILABLE:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
        template_keys = ['payment_crypto', 'payment_received', 'order_confirmed', 'follow_up']
        
        for template_key in template_keys:
            template_text = request.form.get(f'template_{template_key}')
            if template_text:
                # Vérifier si le template existe déjà
                _execute(cursor, 'SELECT id FROM message_templates WHERE template_key = ?', (template_key,))
                exists = cursor.fetchone()
                
                if exists:
                    # Mettre à jour
                    _execute(cursor, '''
                        UPDATE message_templates 
                        SET template_text = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE template_key = ?
                    ''', (template_text, template_key))
                else:
                    # Insérer
                    _execute(cursor, '''
                        INSERT INTO message_templates (template_key, template_text)
                        VALUES (?, ?)
                    ''', (template_key, template_text))
        
        conn.commit()
        
        return redirect('/?view=templates&success=1')
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

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
            <a href="/?view=crypto" class="tab {% if view == 'crypto' %}active{% endif %}">
                ₿ Adresses Crypto
            </a>
            <a href="/?view=templates" class="tab {% if view == 'templates' %}active{% endif %}">
                📝 Templates
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
        
        {% elif view == 'crypto' %}
            <h2 class="section-title">₿ Gestion des Adresses Crypto</h2>
            {% if request.args.get('success') %}
            <div style="margin-bottom: 20px; padding: 15px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 4px; color: #155724;">
                ✅ <strong>Adresse crypto enregistrée avec succès !</strong>
            </div>
            {% endif %}
            {% if request.args.get('error') %}
            <div style="margin-bottom: 20px; padding: 15px; background: #f8d7da; border-left: 4px solid #dc3545; border-radius: 4px; color: #721c24;">
                ❌ <strong>Erreur :</strong> Veuillez remplir tous les champs.
            </div>
            {% endif %}
            
            <p style="margin-bottom: 20px; color: #666;">Gérez vos adresses crypto pour les paiements clients. Les adresses sont utilisées dans les messages de paiement envoyés depuis les conversations.</p>
            
            <!-- Formulaire pour ajouter une adresse -->
            <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                <h3 style="margin-bottom: 15px; color: #333; font-size: 18px;">➕ Ajouter une adresse crypto</h3>
                <form method="POST" action="/crypto/add">
                    <div style="display: grid; grid-template-columns: 1fr 2fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div>
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #666;">Nom *</label>
                            <input type="text" name="name" placeholder="Ex: Bitcoin Principal" 
                                   style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 6px;" required>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #666;">Adresse *</label>
                            <input type="text" name="address" placeholder="Ex: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh" 
                                   style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 6px; font-family: monospace; font-size: 13px;" required>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #666;">Réseau *</label>
                            <select name="network" style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 6px;" required>
                                <option value="">-- Sélectionner --</option>
                                <option value="Bitcoin">Bitcoin</option>
                                <option value="Ethereum">Ethereum</option>
                                <option value="USDT">USDT</option>
                                <option value="USDC">USDC</option>
                                <option value="BNB">BNB</option>
                                <option value="Autre">Autre</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" style="background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: 600;">
                        ➕ Ajouter l'adresse
                    </button>
                </form>
            </div>
            
            <!-- Liste des adresses existantes -->
            <h3 style="margin-bottom: 15px; color: #333; font-size: 18px;">📋 Adresses enregistrées</h3>
            {% if crypto_addresses %}
                <div style="display: flex; flex-direction: column; gap: 15px;">
                    {% for addr in crypto_addresses %}
                    <div class="card" style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; font-size: 16px; margin-bottom: 8px; color: #333;">
                                {{ addr.name }}
                            </div>
                            <div style="font-family: monospace; font-size: 13px; color: #666; margin-bottom: 5px; word-break: break-all;">
                                {{ addr.address }}
                            </div>
                            <div style="font-size: 13px; color: #999;">
                                🌐 Réseau : {{ addr.network }}
                            </div>
                        </div>
                        <form method="POST" action="/crypto/delete/{{ addr.id }}" style="margin-left: 20px;" onsubmit="return confirm('Êtes-vous sûr de vouloir supprimer cette adresse ?');">
                            <button type="submit" style="padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">
                                🗑️ Supprimer
                            </button>
                        </form>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="empty">📭 Aucune adresse crypto enregistrée. Ajoutez-en une ci-dessus.</div>
            {% endif %}
            
            <div style="margin-top: 20px; padding: 15px; background: #fffbea; border-left: 4px solid #ffd700; border-radius: 4px;">
                <strong>💡 Note :</strong> Les adresses crypto sont stockées dans la base de données et persistent même après redéploiement. 
                Vous pouvez les sélectionner lors de l'envoi de messages de paiement depuis les conversations.
            </div>
        
        {% elif view == 'templates' %}
            <h2 class="section-title">📝 Gestion des Templates de Messages</h2>
            {% if request.args.get('success') %}
            <div style="margin-bottom: 20px; padding: 15px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 4px; color: #155724;">
                ✅ <strong>Templates enregistrés avec succès !</strong> Les modifications sont actives immédiatement.
            </div>
            {% endif %}
            <p style="margin-bottom: 20px; color: #666;">Modifiez les templates de messages utilisés pour communiquer avec les clients. Les variables comme [SERVICE], [QUANTITE], [PRIX], [MONTANT], [VOTRE_ADRESSE_CRYPTO], [RESEAU] seront remplacées automatiquement.</p>
            
            <form method="POST" action="/templates/update" style="background: white; padding: 20px; border-radius: 8px;">
                {% set template_names = {
                    'payment_crypto': '💰 Paiement Crypto',
                    'payment_received': '✅ Paiement reçu',
                    'order_confirmed': '✅ Commande confirmée',
                    'follow_up': '👋 Suivi'
                } %}
                
                {% for template_key, template_name in template_names.items() %}
                <div style="margin-bottom: 30px;">
                    <h3 style="margin-bottom: 10px; color: #333; font-size: 18px;">{{ template_name }}</h3>
                    <textarea name="template_{{ template_key }}" 
                              style="width: 100%; min-height: 200px; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-family: monospace; font-size: 13px; line-height: 1.5; resize: vertical;" 
                              required>{% if templates %}{{ templates.get(template_key, '') }}{% endif %}</textarea>
                    <p style="margin-top: 5px; font-size: 12px; color: #666;">Variables disponibles : [SERVICE], [QUANTITE], [PRIX], [MONTANT]{% if template_key == 'payment_crypto' %}, [VOTRE_ADRESSE_CRYPTO], [RESEAU]{% endif %}</p>
                </div>
                {% endfor %}
                
                <div style="margin-top: 20px; text-align: right;">
                    <button type="submit" style="background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: 600;">
                        💾 Enregistrer les Templates
                    </button>
                </div>
            </form>
            
            <div style="margin-top: 20px; padding: 15px; background: #fffbea; border-left: 4px solid #ffd700; border-radius: 4px;">
                <strong>💡 Note :</strong> Les templates sont stockés dans la base de données (Supabase ou SQLite). 
                Ils persistent même après redéploiement et sont utilisés immédiatement dans les conversations.
            </div>
        {% endif %}
    </div>
    
    <!-- Rafraîchissement automatique pour les vues avec conversations/commandes -->
    {% if view in ['overview', 'conversations', 'orders'] %}
    <script>
        (function() {
            let refreshInterval;
            let isPageVisible = true;
            let lastStats = {
                total_orders: {{ stats.total_orders }},
                total_clients: {{ stats.total_clients }},
                total_messages: {{ stats.total_messages }}
            };
            
            // Indicateur de rafraîchissement discret
            const refreshIndicator = document.createElement('div');
            refreshIndicator.style.cssText = 'position: fixed; top: 10px; right: 10px; background: #667eea; color: white; padding: 8px 12px; border-radius: 6px; font-size: 12px; z-index: 1000; display: none; box-shadow: 0 2px 8px rgba(0,0,0,0.2);';
            refreshIndicator.innerHTML = '🔄 Mise à jour...';
            document.body.appendChild(refreshIndicator);
            
            // Détecter si la page est visible (pas en arrière-plan)
            document.addEventListener('visibilitychange', function() {
                isPageVisible = !document.hidden;
                if (isPageVisible) {
                    // Rafraîchir immédiatement quand la page redevient visible
                    checkForUpdates();
                }
            });
            
            // Fonction pour vérifier les mises à jour
            function checkForUpdates() {
                if (!isPageVisible) return;
                
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        // Vérifier si les stats ont changé
                        const hasChanges = 
                            data.total_orders !== lastStats.total_orders ||
                            data.total_clients !== lastStats.total_clients ||
                            data.total_messages !== lastStats.total_messages;
                        
                        if (hasChanges) {
                            // Afficher l'indicateur
                            refreshIndicator.style.display = 'block';
                            
                            // Rafraîchir la page après un court délai
                            setTimeout(() => {
                                window.location.reload();
                            }, 500);
                        }
                        
                        lastStats = {
                            total_orders: data.total_orders,
                            total_clients: data.total_clients,
                            total_messages: data.total_messages
                        };
                    })
                    .catch(error => {
                        console.error('Erreur lors de la vérification des mises à jour:', error);
                    });
            }
            
            // Démarrer le rafraîchissement automatique toutes les 20 secondes (optimisé pour économiser ressources)
            refreshInterval = setInterval(checkForUpdates, 20000);
            
            // Vérifier aussi quand la fenêtre redevient active
            window.addEventListener('focus', checkForUpdates);
            
            // Nettoyer à la fermeture
            window.addEventListener('beforeunload', function() {
                if (refreshInterval) {
                    clearInterval(refreshInterval);
                }
            });
        })();
    </script>
    {% endif %}
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
                <button type="button" onclick="showCryptoModal()" class="template-btn" style="background: #667eea; color: white;">💰 Paiement Crypto</button>
                <button type="button" onclick="loadTemplate('payment_received')" class="template-btn" style="background: #28a745; color: white;">✅ Paiement reçu</button>
                <button type="button" onclick="loadTemplate('order_confirmed')" class="template-btn" style="background: #17a2b8; color: white;">✅ Commande confirmée</button>
                <button type="button" onclick="loadTemplate('follow_up')" class="template-btn" style="background: #ffc107; color: #333;">👋 Suivi</button>
            </div>
        </div>
    </div>
    
    <!-- Modal pour choisir l'adresse crypto -->
    <div id="cryptoModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center;">
        <div style="background: white; padding: 30px; border-radius: 12px; max-width: 500px; width: 90%; max-height: 80vh; overflow-y: auto;">
            <h3 style="margin-bottom: 20px; color: #333;">₿ Choisir une adresse crypto</h3>
            <form id="cryptoForm" onsubmit="return loadCryptoTemplate(event);">
                <input type="hidden" name="template_id" value="payment_crypto">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #666;">Sélectionnez une adresse :</label>
                    <select name="crypto_address_id" id="cryptoAddressSelect" required style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 14px;">
                        <option value="">-- Choisir une adresse --</option>
                        {% for addr in crypto_addresses %}
                        <option value="{{ addr.id }}">{{ addr.name }} ({{ addr.network }})</option>
                        {% endfor %}
                    </select>
                    {% if not crypto_addresses %}
                    <p style="margin-top: 10px; color: #dc3545; font-size: 13px;">
                        ⚠️ Aucune adresse disponible. <a href="/?view=crypto" style="color: #667eea;">Ajoutez-en une ici</a>.
                    </p>
                    {% endif %}
                </div>
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button type="button" onclick="closeCryptoModal()" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 6px; cursor: pointer;">
                        Annuler
                    </button>
                    <button type="submit" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">
                        Utiliser ce template
                    </button>
                </div>
            </form>
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
        
        function loadTemplate(templateId) {
            const formData = new FormData();
            formData.append('template_id', templateId);
            
            fetch('/conversation/{{ conv.id }}/template', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    const textarea = document.getElementById('messageTextarea');
                    textarea.value = data.message;
                    textarea.focus();
                    // Scroll vers le textarea
                    textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else if (data.error) {
                    alert('Erreur : ' + data.error);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Une erreur est survenue lors du chargement du template');
            });
        }
        
        function loadCryptoTemplate(event) {
            event.preventDefault();
            const cryptoAddressId = document.getElementById('cryptoAddressSelect').value;
            
            if (!cryptoAddressId) {
                alert('Veuillez sélectionner une adresse crypto');
                return false;
            }
            
            const formData = new FormData();
            formData.append('template_id', 'payment_crypto');
            formData.append('crypto_address_id', cryptoAddressId);
            
            fetch('/conversation/{{ conv.id }}/template', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    const textarea = document.getElementById('messageTextarea');
                    textarea.value = data.message;
                    textarea.focus();
                    closeCryptoModal();
                    // Scroll vers le textarea
                    textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else if (data.error) {
                    alert('Erreur : ' + data.error);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Une erreur est survenue lors du chargement du template');
            });
            
            return false;
        }
        
        function showCryptoModal() {
            document.getElementById('cryptoModal').style.display = 'flex';
        }
        
        function closeCryptoModal() {
            document.getElementById('cryptoModal').style.display = 'none';
        }
        
        // Fermer le modal en cliquant à l'extérieur
        const modal = document.getElementById('cryptoModal');
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeCryptoModal();
                }
            });
        }
    </script>
</body>
</html>
'''

PREVIEW_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Prévisualisation - Reputalys</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .preview-box {
            background: #f9f9f9;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            white-space: pre-wrap;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 15px;
            line-height: 1.6;
            color: #333;
        }
        textarea {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            line-height: 1.6;
            resize: vertical;
            margin-bottom: 20px;
        }
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: flex-end;
        }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-cancel {
            background: #6c757d;
            color: white;
        }
        .btn-cancel:hover {
            background: #5a6268;
        }
        .btn-send {
            background: #667eea;
            color: white;
        }
        .btn-send:hover {
            background: #5568d3;
        }
        .info {
            background: #fffbea;
            border-left: 4px solid #ffd700;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 Prévisualisation du message</h1>
            <p style="color: #666; margin-top: 5px;">Vérifiez et modifiez le message avant de l'envoyer au client.</p>
        </div>
        
        <div class="info">
            💡 <strong>Astuce :</strong> Vous pouvez modifier le message ci-dessous avant de l'envoyer. Les variables ont déjà été remplacées par les valeurs réelles.
        </div>
        
        <div>
            <label style="display: block; margin-bottom: 10px; font-weight: 600; color: #333;">Message à envoyer :</label>
            <form method="POST" action="/conversation/{{ conv_id }}/send">
                <input type="hidden" name="crypto_address_id" value="{{ crypto_address_id }}">
                <textarea name="message" id="messageText">{{ message }}</textarea>
                
                <div class="button-group">
                    <a href="/conversation/{{ conv_id }}" class="btn-cancel" style="text-decoration: none; display: inline-block; text-align: center;">Annuler</a>
                    <button type="submit" class="btn-send">📤 Envoyer le message</button>
                </div>
            </form>
        </div>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
            <h3 style="margin-bottom: 10px; color: #333;">Aperçu (Markdown) :</h3>
            <div class="preview-box" id="preview">{{ message }}</div>
        </div>
    </div>
    
    <script>
        // Mise à jour de l'aperçu en temps réel
        const textarea = document.getElementById('messageText');
        const preview = document.getElementById('preview');
        
        textarea.addEventListener('input', function() {
            preview.textContent = this.value;
        });
    </script>
</body>
</html>
'''

def create_simple_dashboard():
    """Retourne l'app Flask"""
    return app

