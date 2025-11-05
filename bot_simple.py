"""
Bot Telegram Ultra-Simple - Qualification de Leads
Version MVP - Le Bon Mot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import logging
from datetime import datetime
import sqlite3
import os

# Configuration du logger en premier
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Support Supabase (PostgreSQL) - APRÈS la création du logger
USE_SUPABASE = False
SUPABASE_FAILED = False  # Flag pour éviter de réessayer si Supabase a déjà échoué

if os.getenv('SUPABASE_URL') or os.getenv('SUPABASE_DB_HOST'):
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        USE_SUPABASE = True
        logger.info("✅ Supabase (PostgreSQL) détecté - tentative de connexion...")
    except ImportError:
        logger.warning("⚠️ psycopg2-binary non installé, utilisation de SQLite")
        USE_SUPABASE = False
        SUPABASE_FAILED = True

# Grille tarifaire par défaut (utilisée si pas de prix en DB)
PRICING_DEFAULT = {
    'google': {'price': 18, 'currency': 'EUR', 'name': 'Avis Google'},
    'trustpilot': {'price': 16, 'currency': 'EUR', 'name': 'Trustpilot'},
    'forum': {'price': 5, 'currency': 'EUR', 'name': 'Message Forum'},
    'pagesjaunes': {'price': 15, 'currency': 'EUR', 'name': 'Pages Jaunes'},
    'autre_plateforme': {'price': 15, 'currency': 'EUR', 'name': 'Autre plateforme'},
    'suppression': {'price': 'Sur devis', 'currency': '', 'name': 'Suppression de liens'}
}

# Variable globale pour le cache des prix (rechargée après init DB)
PRICING = PRICING_DEFAULT.copy()

def get_pricing():
    """Charge les prix depuis la base de données, avec fallback sur les valeurs par défaut"""
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        
        pricing = {}
        _execute(cursor, 'SELECT service_key, price, currency, name FROM pricing')
        results = cursor.fetchall()
        
        # Convertir les résultats en dictionnaire
        for row in results:
            service_key = row[0]
            price_val = row[1]
            currency = row[2] or 'EUR'
            name = row[3]
            pricing[service_key] = {
                'price': price_val,
                'currency': currency,
                'name': name
            }
        
        # Si aucun prix en DB, utiliser les valeurs par défaut
        if not pricing:
            return PRICING_DEFAULT.copy()
        
        # Ajouter les services par défaut qui ne sont pas en DB
        for key, value in PRICING_DEFAULT.items():
            if key not in pricing:
                pricing[key] = value
        
        return pricing
    except Exception as e:
        logger.warning(f"⚠️ Erreur chargement prix depuis DB: {e}, utilisation des valeurs par défaut")
        return PRICING_DEFAULT.copy()
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def get_service_price(service_key):
    """Récupère le prix d'un service spécifique"""
    pricing = get_pricing()
    return pricing.get(service_key, PRICING_DEFAULT.get(service_key, {'price': 0, 'currency': 'EUR', 'name': service_key}))

def reload_pricing():
    """Recharge les prix depuis la DB (à appeler après modification)"""
    global PRICING
    PRICING = get_pricing()

# Cache global pour les messages et boutons du bot
BOT_MESSAGES_CACHE = {}
BOT_BUTTONS_CACHE = {}

def get_bot_message(message_key, default=""):
    """Récupère un message du bot depuis la DB (avec cache)"""
    global BOT_MESSAGES_CACHE
    
    # Utiliser le cache si disponible
    if message_key in BOT_MESSAGES_CACHE:
        return BOT_MESSAGES_CACHE[message_key]
    
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        _execute(cursor, 'SELECT message_text FROM bot_messages WHERE message_key = ?', (message_key,))
        result = cursor.fetchone()
        
        if result:
            message_text = result[0] if isinstance(result, tuple) else result['message_text']
            BOT_MESSAGES_CACHE[message_key] = message_text
            return message_text
        else:
            # Si pas en DB, utiliser la valeur par défaut et l'insérer
            if default:
                _execute(cursor, '''
                    INSERT INTO bot_messages (message_key, message_text)
                    VALUES (?, ?)
                ''', (message_key, default))
                conn.commit()
                BOT_MESSAGES_CACHE[message_key] = default
            return default
    except Exception as e:
        logger.warning(f"⚠️ Erreur get_bot_message({message_key}): {e}")
        return default
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def get_bot_buttons(button_key):
    """Récupère les boutons pour un écran donné depuis la DB (avec cache)"""
    global BOT_BUTTONS_CACHE
    
    cache_key = f"buttons_{button_key}"
    if cache_key in BOT_BUTTONS_CACHE:
        return BOT_BUTTONS_CACHE[cache_key]
    
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        _execute(cursor, '''
            SELECT button_text, callback_data, row_position
            FROM bot_buttons
            WHERE button_key = ?
            ORDER BY row_position, id
        ''', (button_key,))
        results = cursor.fetchall()
        
        if results:
            # Organiser par rangée
            rows = {}
            for row in results:
                if isinstance(row, tuple):
                    btn_text, callback, row_pos = row[0], row[1], row[2]
                else:
                    btn_text, callback, row_pos = row['button_text'], row['callback_data'], row['row_position']
                
                if row_pos not in rows:
                    rows[row_pos] = []
                rows[row_pos].append((btn_text, callback))
            
            # Convertir en liste de listes
            buttons = [rows[i] for i in sorted(rows.keys())]
            BOT_BUTTONS_CACHE[cache_key] = buttons
            return buttons
        else:
            return []
    except Exception as e:
        logger.warning(f"⚠️ Erreur get_bot_buttons({button_key}): {e}")
        return []
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def reload_bot_config():
    """Recharge les messages et boutons depuis la DB (à appeler après modification)"""
    global BOT_MESSAGES_CACHE, BOT_BUTTONS_CACHE
    BOT_MESSAGES_CACHE.clear()
    BOT_BUTTONS_CACHE.clear()
    logger.info("✅ Cache des messages et boutons rechargé")

# État des conversations
user_conversations = {}

def _get_recap(state):
    """Génère un récapitulatif des étapes précédentes avec mise en page améliorée"""
    has_data = any([state.get('service_type'), state.get('quantity'), state.get('link'), state.get('details')])
    
    if not has_data:
        return ""
    
    recap = "━━━━━━━━━━━━━━━━━━\n"
    recap += "*📋 Récapitulatif*\n"
    recap += "━━━━━━━━━━━━━━━━━━\n"
    
    service_type = state.get('service_type')
    if service_type:
        service_info = get_service_price(service_type)
        recap += f"\n🔹 Service : *{service_info.get('name', service_type)}*"
    
    quantity = state.get('quantity')
    if quantity:
        recap += f"\n🔹 Quantité : *{quantity}*"
    
    link = state.get('link')
    if link and link != 'Aucun':
        display_link = link[:50] + "..." if len(link) > 50 else link
        recap += f"\n🔹 Lien : {display_link}"
    
    details = state.get('details')
    if details and details != 'Aucun détail supplémentaire':
        display_details = details[:50] + "..." if len(details) > 50 else details
        recap += f"\n🔹 Détails : {display_details}"
    
    recap += "\n\n"
    return recap

def _is_valid_quantity(text):
    """Vérifie si le texte ne contient que des chiffres"""
    # Retirer les espaces et vérifier si c'est un nombre valide
    cleaned = text.strip().replace(' ', '')
    if not cleaned:
        return False
    # Vérifier si c'est un nombre entier ou avec virgule/point
    try:
        # Accepter "15", "15 avis", "15€" etc.
        import re
        # Extraire tous les chiffres
        numbers = re.findall(r'\d+', cleaned)
        if len(numbers) == 0:
            return False
        # Le premier nombre doit être valide
        int(numbers[0])
        return True
    except:
        return False

def _resolve_db_path() -> str:
    """Retourne un chemin de DB écrivable en prod/local.
    - Priorité à DB_PATH si défini
    - Détecte Railway (variable RAILWAY_ENVIRONMENT) : force /data/lebonmot_simple.db
    - Tente /data/lebonmot_simple.db (Railway persistent volume)
    - Sinon fallback: ./lebonmot_simple.db
    """
    override = os.getenv('DB_PATH')
    if override:
        os.makedirs(os.path.dirname(override) or '.', exist_ok=True)
        logger.info(f"📁 DB_PATH override: {override}")
        return override

    # Si on est sur Railway, FORCER l'utilisation de /data
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
        railway_db_path = "/data/lebonmot_simple.db"
        try:
            os.makedirs("/data", exist_ok=True)
            # Vérifier qu'on peut écrire dans /data
            test_file = "/data/.test_write"
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"✅ Railway détecté : utilisation de /data/lebonmot_simple.db (volume persistant)")
            return railway_db_path
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'utiliser /data sur Railway: {e}")
            # Continuer avec les fallbacks

    candidates = ["/data/lebonmot_simple.db", "./lebonmot_simple.db", "lebonmot_simple.db"]
    for path in candidates:
        try:
            directory = os.path.dirname(path) or '.'
            if directory != '.':
                os.makedirs(directory, exist_ok=True)
            # Vérifier si on peut écrire dans ce répertoire
            test_file = os.path.join(directory, '.test_write') if directory != '.' else '.test_write'
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                logger.info(f"✅ Base de données sélectionnée : {path}")
                return path
            except (OSError, PermissionError) as e:
                logger.debug(f"❌ Impossible d'écrire dans {directory}: {e}")
                continue
        except Exception as e:
            logger.debug(f"❌ Erreur avec {path}: {e}")
            continue
    
    fallback = "lebonmot_simple.db"
    logger.warning(f"⚠️ Fallback vers : {fallback}")
    return fallback

DB_PATH = _resolve_db_path()

# Log du chemin DB utilisé au démarrage (sera mis à jour après tentative de connexion)

def _connect():
    """Connexion à la base de données (Supabase PostgreSQL ou SQLite)
    Système robuste avec timeout et fallback automatique vers SQLite"""
    global USE_SUPABASE, SUPABASE_FAILED
    # Essayer Supabase si configuré et pas déjà échoué
    if USE_SUPABASE and not SUPABASE_FAILED:
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            # Format: postgresql://user:password@host:port/database
            # Ou utiliser les variables séparées
            db_host = os.getenv('SUPABASE_DB_HOST')
            db_port = os.getenv('SUPABASE_DB_PORT', '5432')
            db_name = os.getenv('SUPABASE_DB_NAME')
            db_user = os.getenv('SUPABASE_DB_USER')
            db_password = os.getenv('SUPABASE_DB_PASSWORD')
            
            # Timeout de connexion (5 secondes) pour éviter les blocages
            connect_timeout = 5
            
            if supabase_url:
                # Si l'URL contient "pooler" ou port 6543, utiliser connection pooling (plus fiable)
                is_pooling = 'pooler.supabase.com' in supabase_url or ':6543' in supabase_url
                if is_pooling:
                    logger.info("🔗 Utilisation de Supabase Connection Pooling (plus fiable)")
                    # Connection pooling : pas d'options de session (mode transaction)
                    conn = psycopg2.connect(
                        supabase_url,
                        connect_timeout=connect_timeout
                    )
                else:
                    # Connexion directe : peut utiliser options de session
                    conn = psycopg2.connect(
                        supabase_url,
                        connect_timeout=connect_timeout,
                        options='-c statement_timeout=10000'  # Timeout de requête : 10 secondes
                    )
            elif db_host and db_name and db_user and db_password:
                # Utiliser connection pooling si port 6543, sinon port standard 5432
                is_pooling = db_port == '6543' or 'pooler' in db_host
                if is_pooling:
                    logger.info("🔗 Utilisation de Supabase Connection Pooling (port 6543)")
                    # Connection pooling : pas d'options de session (mode transaction)
                    conn = psycopg2.connect(
                        host=db_host,
                        port=db_port,
                        database=db_name,
                        user=db_user,
                        password=db_password,
                        connect_timeout=connect_timeout
                    )
                else:
                    # Connexion directe : peut utiliser options de session
                    conn = psycopg2.connect(
                        host=db_host,
                        port=db_port,
                        database=db_name,
                        user=db_user,
                        password=db_password,
                        connect_timeout=connect_timeout,
                        options='-c statement_timeout=10000'
                    )
            else:
                raise ValueError("Variables Supabase manquantes")
            
            # Pour connection pooling (transaction mode), ne pas tester avec SELECT
            # car cela peut causer "set_session cannot be used inside a transaction"
            # La connexion elle-même est suffisante pour valider
            
            # Détecter si c'est du pooling
            is_pooling_connection = (
                (supabase_url and ('pooler.supabase.com' in supabase_url or ':6543' in supabase_url)) or
                (db_host and ('pooler' in db_host or db_port == '6543'))
            )
            
            if not is_pooling_connection:
                # Seulement tester pour connexions directes (pas pooling)
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
            
            conn.autocommit = False
            logger.info("✅ Connexion Supabase réussie")
            return conn
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Erreur connexion Supabase (réseau/timeout): {e}")
            logger.warning("⚠️ Fallback vers SQLite - connexion Supabase échouée")
            # Désactiver Supabase pour éviter de réessayer à chaque requête
            SUPABASE_FAILED = True
            USE_SUPABASE = False
            # Continuer avec SQLite ci-dessous
        except Exception as e:
            logger.error(f"❌ Erreur connexion Supabase (autre): {e}")
            logger.warning("⚠️ Fallback vers SQLite - connexion Supabase échouée")
            SUPABASE_FAILED = True
            USE_SUPABASE = False
            # Continuer avec SQLite ci-dessous
    
    # Connexion SQLite (fallback ou si Supabase non configuré)
    # Système robuste avec retry et création automatique du répertoire
    try:
        # Créer le répertoire si nécessaire
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and db_dir != '.':
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10.0)
        # Optimisations sûres qui ne compromettent pas la persistance
        conn.execute('PRAGMA synchronous=NORMAL')  # Bon compromis vitesse/sécurité
        conn.execute('PRAGMA cache_size=-5000')  # 5MB de cache (raisonnable)
        conn.execute('PRAGMA temp_store=MEMORY')  # Tables temporaires en RAM
        conn.execute('PRAGMA foreign_keys=ON')  # Activer les clés étrangères
        conn.execute('PRAGMA journal_mode=DELETE')  # Mode journal sûr (pas WAL qui peut poser problème)
        
        # Tester la connexion
        conn.execute('SELECT 1')
        
        logger.debug(f"✅ Connexion SQLite : {DB_PATH}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"❌ Erreur SQLite : {e}")
        # Dernier recours : créer dans le répertoire courant
        fallback_path = "lebonmot_simple.db"
        logger.warning(f"⚠️ Fallback SQLite vers : {fallback_path}")
        conn = sqlite3.connect(fallback_path, check_same_thread=False, timeout=10.0)
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA cache_size=-5000')
        conn.execute('PRAGMA temp_store=MEMORY')
        conn.execute('PRAGMA foreign_keys=ON')
        return conn

def _execute(cursor, query, params=None):
    """Exécute une requête en adaptant les placeholders selon le type de DB"""
    # Détecter le type de DB depuis le cursor
    is_postgres = hasattr(cursor, 'connection') and hasattr(cursor.connection, 'get_dsn_parameters')
    
    if is_postgres:
        # PostgreSQL utilise %s au lieu de ?
        query = query.replace('?', '%s')
    
    if params:
        return cursor.execute(query, params)
    else:
        return cursor.execute(query)

def init_simple_db():
    """Initialise une base de données ultra-simple (Supabase PostgreSQL ou SQLite)"""
    conn = _connect()
    cursor = conn.cursor()
    
    # Log du type de DB après connexion réelle
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    if is_postgres:
        logger.info("📁 Base de données : Supabase (PostgreSQL)")
    else:
        logger.info(f"📁 Base de données : {DB_PATH} (abs: {os.path.abspath(DB_PATH)})")
    
    # Détecter le type de DB depuis la connexion réelle (pas le flag)
    if is_postgres:
        # Schéma PostgreSQL (Supabase)
        # Table des conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL,
                username TEXT,
                first_name TEXT,
                service_type TEXT,
                quantity TEXT,
                link TEXT,
                details TEXT,
                estimated_price TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER,
                telegram_id BIGINT NOT NULL,
                message TEXT NOT NULL,
                sender TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')
        
        # Table des prix (configurable depuis dashboard)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing (
                id SERIAL PRIMARY KEY,
                service_key TEXT UNIQUE NOT NULL,
                price TEXT NOT NULL,
                currency TEXT DEFAULT 'EUR',
                name TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des adresses crypto (configurable depuis dashboard)
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
        
        # Table des templates de messages (configurable depuis dashboard)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_templates (
                id SERIAL PRIMARY KEY,
                template_key TEXT UNIQUE NOT NULL,
                template_text TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des messages du bot (configurable depuis dashboard)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_messages (
                id SERIAL PRIMARY KEY,
                message_key TEXT UNIQUE NOT NULL,
                message_text TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des boutons du bot (configurable depuis dashboard)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_buttons (
                id SERIAL PRIMARY KEY,
                button_key TEXT NOT NULL,
                button_text TEXT NOT NULL,
                callback_data TEXT NOT NULL,
                row_position INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(button_key, row_position)
            )
        ''')
        
        # Insérer les prix par défaut si la table est vide
        cursor.execute('SELECT COUNT(*) FROM pricing')
        if cursor.fetchone()[0] == 0:
            default_prices = [
                ('google', '18', 'EUR', 'Avis Google'),
                ('trustpilot', '16', 'EUR', 'Trustpilot'),
                ('forum', '5', 'EUR', 'Message Forum'),
                ('pagesjaunes', '15', 'EUR', 'Pages Jaunes'),
                ('autre_plateforme', '15', 'EUR', 'Autre plateforme'),
                ('suppression', 'Sur devis', '', 'Suppression de liens')
            ]
            for service_key, price, currency, name in default_prices:
                cursor.execute('''
                    INSERT INTO pricing (service_key, price, currency, name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (service_key) DO NOTHING
                ''', (service_key, price, currency, name))
        
        # Insérer les templates par défaut si la table est vide
        cursor.execute('SELECT COUNT(*) FROM message_templates')
        if cursor.fetchone()[0] == 0:
            default_templates = [
                ('payment_crypto', '''💰 *Informations de paiement*

Veuillez effectuer le paiement à l'adresse suivante :

*Adresse crypto :* [VOTRE_ADRESSE_CRYPTO]

*Montant :* [MONTANT]
*Réseau :* [RESEAU]

Une fois le paiement effectué, vous pouvez m'envoyer :
• Une capture d'écran de la confirmation de transaction (c'est la solution la plus simple)

Ou bien, si vous êtes à l'aise avec les cryptomonnaies :
• Le hash de la transaction (cette longue suite de caractères qui confirme votre paiement)'''),
                ('payment_received', '''✅ *Paiement reçu !*

Merci pour votre paiement. Votre commande est maintenant en cours de traitement.

*Délai estimé :* 48-72h

Je vous tiendrai informé dès que la commande sera livrée. N'hésitez pas si vous avez des questions !'''),
                ('order_confirmed', '''✅ *Commande confirmée !*

Votre commande a été bien reçue et est en cours de traitement.

*Récapitulatif :*
• Service : [SERVICE]
• Quantité : [QUANTITE]
• Prix : [PRIX]

*Délai estimé :* 48-72h

Je vous tiendrai informé de l'avancement !'''),
                ('follow_up', '''👋 Bonjour,

Souhaitez-vous un point sur l'avancement de votre commande ?

N'hésitez pas si vous avez des questions !''')
            ]
            for template_key, template_text in default_templates:
                cursor.execute('''
                    INSERT INTO message_templates (template_key, template_text)
                    VALUES (%s, %s)
                    ON CONFLICT (template_key) DO NOTHING
                ''', (template_key, template_text))
        
        # Créer les index pour améliorer les performances
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversations_telegram_id 
            ON conversations(telegram_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
            ON messages(conversation_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_telegram_id 
            ON messages(telegram_id)
        ''')
    else:
        # Schéma SQLite
        # Table des conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                service_type TEXT,
                quantity TEXT,
                link TEXT,
                details TEXT,
                estimated_price TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                telegram_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                sender TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')
        
        # Table des prix (configurable depuis dashboard)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_key TEXT UNIQUE NOT NULL,
                price TEXT NOT NULL,
                currency TEXT DEFAULT 'EUR',
                name TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des adresses crypto (configurable depuis dashboard)
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
        
        # Table des templates de messages (configurable depuis dashboard)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_key TEXT UNIQUE NOT NULL,
                template_text TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des messages du bot (configurable depuis dashboard)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_key TEXT UNIQUE NOT NULL,
                message_text TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des boutons du bot (configurable depuis dashboard)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                button_key TEXT NOT NULL,
                button_text TEXT NOT NULL,
                callback_data TEXT NOT NULL,
                row_position INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(button_key, row_position)
            )
        ''')
        
        # Insérer les prix par défaut si la table est vide
        cursor.execute('SELECT COUNT(*) FROM pricing')
        if cursor.fetchone()[0] == 0:
            default_prices = [
                ('google', '18', 'EUR', 'Avis Google'),
                ('trustpilot', '16', 'EUR', 'Trustpilot'),
                ('forum', '5', 'EUR', 'Message Forum'),
                ('pagesjaunes', '15', 'EUR', 'Pages Jaunes'),
                ('autre_plateforme', '15', 'EUR', 'Autre plateforme'),
                ('suppression', 'Sur devis', '', 'Suppression de liens')
            ]
            for service_key, price, currency, name in default_prices:
                cursor.execute('''
                    INSERT OR IGNORE INTO pricing (service_key, price, currency, name)
                    VALUES (?, ?, ?, ?)
                ''', (service_key, price, currency, name))
    
    conn.commit()
    conn.close()
    logger.info("✅ Base de données simple initialisée")
    
    # Recharger les prix depuis la DB après initialisation
    global PRICING
    PRICING = get_pricing()

def save_message(telegram_id, message, sender='client'):
    """Sauvegarde un message"""
    conn = _connect()
    cursor = conn.cursor()
    
    try:
        # Trouver ou créer la conversation
        _execute(cursor, 'SELECT id FROM conversations WHERE telegram_id = ? ORDER BY created_at DESC LIMIT 1', (telegram_id,))
        result = cursor.fetchone()
        
        if result:
            conversation_id = result[0]
        else:
            # Créer une nouvelle conversation
            _execute(cursor, 'INSERT INTO conversations (telegram_id) VALUES (?)', (telegram_id,))
            if USE_SUPABASE:
                # PostgreSQL retourne l'ID différemment
                cursor.execute('SELECT LASTVAL()')
                conversation_id = cursor.fetchone()[0]
            else:
                conversation_id = cursor.lastrowid
        
        # Sauvegarder le message
        _execute(cursor, '''
            INSERT INTO messages (conversation_id, telegram_id, message, sender)
            VALUES (?, ?, ?, ?)
        ''', (conversation_id, telegram_id, message, sender))
        
        conn.commit()
    except Exception as e:
        logger.error(f"Erreur save_message: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

async def send_admin_notification(message: str, bot_instance=None):
    """
    Envoie une notification Telegram à l'administrateur.
    
    Cette fonction est préparée pour être utilisée à l'avenir pour notifier
    l'admin des nouveaux messages, commandes, etc.
    
    Args:
        message: Le message à envoyer à l'admin
        bot_instance: Instance du bot Telegram (optionnel, sera utilisé si fourni)
    
    Pour activer cette fonctionnalité :
    1. Ajoutez ADMIN_TELEGRAM_ID dans votre .env
    2. Appelez cette fonction aux moments appropriés (nouveau message, nouvelle commande, etc.)
    """
    admin_telegram_id = os.getenv('ADMIN_TELEGRAM_ID')
    
    if not admin_telegram_id:
        logger.debug("ADMIN_TELEGRAM_ID non configuré - notifications admin désactivées")
        return False
    
    try:
        admin_id = int(admin_telegram_id)
        
        # Si bot_instance est fourni, l'utiliser directement
        if bot_instance:
            await bot_instance.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"✅ Notification admin envoyée à {admin_id}")
            return True
        else:
            # Sinon, on pourrait utiliser le bot global si disponible
            # Pour l'instant, on log juste le message
            logger.info(f"📢 Notification admin (bot non disponible) : {message}")
            return False
    except ValueError:
        logger.warning(f"ADMIN_TELEGRAM_ID invalide : {admin_telegram_id}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la notification admin : {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start - Affiche le message d'accueil"""
    try:
        logger.info(f"📥 Commande /start reçue de l'utilisateur {update.effective_user.id}")
        user = update.effective_user
        telegram_id = user.id
        
        # Réinitialiser l'état de conversation
        user_conversations[telegram_id] = {'step': 'menu'}
        
        welcome_text = f"""🔐 **Reputalys**
_Service Anonyme de E-réputation_

━━━━━━━━━━━━━━━━━━
🌍 Avis 100% authentiques et géolocalisés
💬 Messages de forum professionnels
🔒 Anonymat total garanti
🎯 IP réelles, comptes vérifiés
💳 Paiement crypto uniquement
━━━━━━━━━━━━━━━━━━
✅ Plus de 15 000 avis livrés avec succès
✅ Délai moyen : 48-72h
━━━━━━━━━━━━━━━━━━

Que souhaitez-vous faire aujourd'hui ?"""

        keyboard = [
            [InlineKeyboardButton("📝 Passer une commande", callback_data="new_quote")],
            [InlineKeyboardButton("📋 Mes Commandes", callback_data="my_orders")],
            [InlineKeyboardButton("💬 Contacter le support", callback_data="contact_support")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        logger.info(f"✅ Message de bienvenue envoyé à l'utilisateur {telegram_id}")
    except Exception as e:
        logger.error(f"❌ Erreur dans start() : {e}", exc_info=True)
        try:
            await update.message.reply_text("❌ Une erreur est survenue. Veuillez réessayer.")
        except:
            pass

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les boutons"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    telegram_id = user.id
    
    # Initialiser la conversation si elle n'existe pas
    if telegram_id not in user_conversations:
        user_conversations[telegram_id] = {
            'step': 'menu',
            'username': user.username,
            'first_name': user.first_name
        }
    
    data = query.data
    
    if data == "new_quote":
        # Démarrer le processus de qualification - Choix principal
        user_conversations[telegram_id] = {
            'step': 'main_choice',
            'username': user.username,
            'first_name': user.first_name
        }
        
        keyboard = [
            [InlineKeyboardButton("⭐ Avis (Google, Trustpilot, etc.)", callback_data="category:avis")],
            [InlineKeyboardButton("💬 Messages sur forum", callback_data="category:forum")],
            [InlineKeyboardButton("🗑️ Suppression de lien (1ère page)", callback_data="category:suppression")],
            [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        recap = _get_recap(user_conversations[telegram_id])
        cta_msg = "🎯 *Choisissez votre service en cliquant sur un bouton ci-dessous*"
        
        await query.edit_message_text(
            f"{recap}📋 *Que souhaitez-vous commander ?*\n\n{cta_msg}\n\nChoisissez le type de service :",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data.startswith("category:"):
        category = data.split(":")[1]
        
        if category == "avis":
            # Choix de la plateforme d'avis
            user_conversations[telegram_id]['step'] = 'service_type'
            recap = _get_recap(user_conversations[telegram_id])
            
            keyboard = [
                [InlineKeyboardButton("⭐ Avis Google", callback_data="service:google")],
                [InlineKeyboardButton("🌟 Trustpilot", callback_data="service:trustpilot")],
                [InlineKeyboardButton("🌐 Autre plateforme", callback_data="service:autre_plateforme")],
                [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
                [InlineKeyboardButton("◀️ Retour", callback_data="new_quote")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"{recap}⭐ *Avis sur quelle plateforme ?*\n\nChoisissez la plateforme :",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif category == "forum":
            # Direct au service forum
            user_conversations[telegram_id]['service_type'] = 'forum'
            user_conversations[telegram_id]['step'] = 'quantity'
            recap = _get_recap(user_conversations[telegram_id])
            
            keyboard = [
                [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
                [InlineKeyboardButton("◀️ Retour", callback_data="new_quote")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"{recap}📊 *Étape 2/4 : Quantité*\n"
                f"Combien de messages souhaitez-vous ?\n"
                f"💡 _Entrez simplement un nombre_",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif category == "suppression":
            # Direct au service suppression
            user_conversations[telegram_id]['service_type'] = 'suppression'
            user_conversations[telegram_id]['step'] = 'quantity'
            recap = _get_recap(user_conversations[telegram_id])
            
            keyboard = [
                [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
                [InlineKeyboardButton("◀️ Retour", callback_data="new_quote")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"{recap}📊 *Étape 2/4 : Quantité*\n"
                f"Combien de liens à supprimer ?\n"
                f"💡 _Entrez simplement un nombre_",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    elif data.startswith("service:"):
        service = data.split(":")[1]
        user_conversations[telegram_id]['service_type'] = service
        user_conversations[telegram_id]['step'] = 'quantity'
        
        service_info = get_service_price(service)
        recap = _get_recap(user_conversations[telegram_id])
        
        keyboard = [
            [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
            [InlineKeyboardButton("◀️ Retour", callback_data="category:avis")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"{recap}📊 *Étape 2/4 : Quantité*\n"
            f"Combien d'avis souhaitez-vous ?\n"
            f"💡 _Entrez simplement un nombre_",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "my_orders":
        # Afficher les commandes du client
        user_conversations[telegram_id]['step'] = 'viewing_orders'
        
        conn = _connect()
        try:
            if USE_SUPABASE:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
            
            # Debug : vérifier toutes les conversations de cet utilisateur
            _execute(cursor, 'SELECT COUNT(*) as total FROM conversations WHERE telegram_id = ?', (telegram_id,))
            if USE_SUPABASE:
                total_conv = cursor.fetchone()['total']
            else:
                total_conv = cursor.fetchone()['total']
            
            _execute(cursor, '''
                SELECT * FROM conversations 
                WHERE telegram_id = ? AND service_type IS NOT NULL AND service_type != ''
                ORDER BY created_at DESC
                LIMIT 5
            ''', (telegram_id,))
            
            orders = cursor.fetchall()
            logger.info(f"Mes commandes: telegram_id={telegram_id}, total_conversations={total_conv}, orders_found={len(orders)}")
        except Exception as e:
            logger.error(f"Erreur récupération commandes: {e}")
            orders = []
        finally:
            conn.close()
        
        if orders:
            orders_text = "📋 **Vos commandes récentes**\n\n"
            for order in orders:
                service_info = get_service_price(order['service_type'])
                service_name = service_info.get('name', order['service_type'])
                orders_text += f"• **{service_name}** - {order['quantity']}\n"
                orders_text += f"  💰 {order['estimated_price']}\n"
                created_at = str(order['created_at'])
                orders_text += f"  📅 {created_at[:10]}\n\n"
            
            orders_text += "\n💬 Pour toute question, contactez le support !"
        else:
            orders_text = "📋 **Aucune commande pour le moment**\n\nCommencez par passer votre première commande ! 🚀"
        
        keyboard = [[InlineKeyboardButton("« Retour au menu", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(orders_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif data == "contact_support":
        user_conversations[telegram_id] = {'step': 'support_mode'}
        
        await query.edit_message_text(
            "💬 **Mode Support activé**\n\n"
            "Vous pouvez maintenant discuter directement avec notre équipe.\n"
            "Écrivez votre message ci-dessous ! 👇",
            parse_mode='Markdown'
        )
        
        save_message(telegram_id, "👤 Client a contacté le support", 'system')
    
    elif data == "skip_link":
        # Passer l'étape lien pour forum/suppression
        telegram_id = query.from_user.id
        state = user_conversations.get(telegram_id, {})
        state['link'] = 'Aucun'
        state['step'] = 'details'
        
        recap = _get_recap(state)
        
        keyboard = [
            [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
            [InlineKeyboardButton("⏭️ Passer cette étape", callback_data="skip_details")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"{recap}✅ Lien ignoré\n"
            f"📝 *Étape 4/4 : Détails supplémentaires (optionnel)*\n"
            f"Avez-vous des précisions à ajouter ?\n"
            f"💡 _Exemples : mots-clés, style souhaité, points à mentionner_\n"
            f"💡 _Si non, cliquez sur \"Passer cette étape\"_",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "skip_details":
        # Finaliser le devis sans détails
        telegram_id = query.from_user.id
        state = user_conversations.get(telegram_id, {})
        state['details'] = 'Aucun détail supplémentaire'
        
        # Finaliser le devis (copier la logique de handle_message step='details')
        service_type = state.get('service_type', 'autre_plateforme')
        quantity = state.get('quantity', '?')
        service_info = get_service_price(service_type)
        
        try:
            qty_num = int(''.join(filter(str.isdigit, quantity)))
            price_val = service_info.get('price', 0)
            if price_val == 'Sur devis' or str(price_val).lower() == 'sur devis':
                price_text = "*Sur devis* (notre équipe vous contactera)"
            else:
                # Convertir le prix en nombre si c'est une chaîne
                price_num = float(price_val) if isinstance(price_val, str) and price_val.replace('.', '').replace('-', '').isdigit() else float(price_val)
                total = qty_num * price_num
                currency = service_info.get('currency', 'EUR')
                price_text = f"*≈ {total} {currency}*"
                state['estimated_price'] = f"{total} {currency}"
        except:
            price_text = "*À calculer* (quantité à préciser)"
            state['estimated_price'] = "À calculer"
        
        # Sauvegarder en DB
        conn = _connect()
        try:
            cursor = conn.cursor()
            _execute(cursor, '''
                INSERT INTO conversations (telegram_id, username, first_name, service_type, quantity, link, details, estimated_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_id, state.get('username'), state.get('first_name'), 
                  service_type, quantity, state.get('link', 'Aucun'), state.get('details', 'Aucun détail supplémentaire'), state.get('estimated_price', 'À calculer')))
            conn.commit()
            logger.info(f"Commande sauvegardée (skip_details): telegram_id={telegram_id}, service={service_type}, quantity={quantity}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde commande (skip_details): {e}")
            conn.rollback()
        finally:
            conn.close()
        
        final_recap = _get_recap(state)
        
        keyboard = [
            [InlineKeyboardButton("📝 Nouvelle commande", callback_data="new_quote")],
            [InlineKeyboardButton("📋 Mes commandes", callback_data="my_orders")],
            [InlineKeyboardButton("💬 Support", callback_data="contact_support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        recap_final = f"""✅ *Devis généré avec succès !*

{final_recap}💰 *Prix estimé :* {price_text}

━━━━━━━━━━━━━━━━━━
👨‍💼 *Un membre du support vous contactera dans les plus brefs délais.*
Vous pouvez continuer à nous écrire ici pour toute question. Notre support vous répondra rapidement. 💬"""

        state['step'] = 'support_mode'
        
        await query.edit_message_text(recap_final, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif data == "back_to_start":
        user_conversations[telegram_id] = {'step': 'menu'}
        
        welcome_text = f"""🔐 *Reputalys*
_Service Anonyme de E-réputation_

━━━━━━━━━━━━━━━━━━
🌍 Avis 100% authentiques et géolocalisés
💬 Messages de forum professionnels
🔒 Anonymat total garanti
🎯 IP réelles, comptes vérifiés
💳 Paiement crypto uniquement
━━━━━━━━━━━━━━━━━━
✅ Plus de 15 000 avis livrés avec succès
✅ Délai moyen : 48-72h
━━━━━━━━━━━━━━━━━━

Que souhaitez-vous faire ?"""

        keyboard = [
            [InlineKeyboardButton("📝 Passer une commande directement", callback_data="new_quote")],
            [InlineKeyboardButton("💬 Contacter le support", callback_data="contact_support")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les messages texte"""
    user = update.effective_user
    telegram_id = user.id
    message_text = update.message.text
    
    # Sauvegarder le message
    save_message(telegram_id, message_text, 'client')
    
    # Récupérer l'état de la conversation
    state = user_conversations.get(telegram_id, {})
    step = state.get('step', 'support_mode')
    
    if step == 'quantity':
        # Vérifier que la quantité est valide (uniquement des chiffres)
        if not _is_valid_quantity(message_text):
            service_type = state.get('service_type', '')
            keyboard = [
                [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")]
            ]
            if service_type:
                keyboard.append([InlineKeyboardButton("◀️ Retour", callback_data=f"service:{service_type}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ *Quantité invalide*\n"
                "Veuillez entrer uniquement un nombre.\n"
                "💡 _Exemples valides : 50, 100, 200_",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Extraire le nombre de la réponse
        import re
        numbers = re.findall(r'\d+', message_text)
        quantity_value = numbers[0] if numbers else message_text
        
        state['quantity'] = quantity_value
        state['step'] = 'link'
        
        recap = _get_recap(state)
        service_type = state.get('service_type', '')
        
        # Pour les avis, le lien est obligatoire
        if service_type in ['google', 'trustpilot', 'pagesjaunes', 'autre_plateforme']:
            keyboard = [
                [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
                [InlineKeyboardButton("◀️ Modifier la quantité", callback_data=f"service:{service_type}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"{recap}🔗 *Étape 3/4 : Lien (obligatoire)*\n"
                f"Veuillez partager le lien de l'établissement.\n"
                f"💡 _Copiez-collez simplement le lien_",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif service_type == 'forum':
            # Pour forum, le lien est obligatoire
            keyboard = [
                [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
                [InlineKeyboardButton("◀️ Modifier la quantité", callback_data=f"service:{service_type}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"{recap}🔗 *Étape 3/4 : Lien (obligatoire)*\n"
                f"Veuillez partager le lien de l'établissement.\n"
                f"💡 _Copiez-collez simplement le lien_",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            # Pour suppression uniquement, le lien est optionnel
            state['step'] = 'details'
            
            keyboard = [
                [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
                [InlineKeyboardButton("⏭️ Passer cette étape", callback_data="skip_link")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"{recap}🔗 *Étape 3/4 : Lien (optionnel)*\n"
                f"Avez-vous un lien à partager ?\n"
                f"💡 _Si non, cliquez sur \"Passer cette étape\"_",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    elif step == 'link':
        # Pour les avis et forum, le lien est obligatoire
        service_type = state.get('service_type', '')
        if service_type in ['google', 'trustpilot', 'pagesjaunes', 'autre_plateforme', 'forum']:
            if message_text.lower() in ['non', 'skip', 'aucun', 'pas de lien']:
                keyboard = [
                    [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
                    [InlineKeyboardButton("◀️ Retour", callback_data=f"service:{service_type}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "❌ *Lien obligatoire*\n"
                    "Le lien est requis pour traiter votre commande.\n"
                    "Veuillez partager le lien de l'établissement.\n"
                    "💡 _Copiez-collez le lien_",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return
        
        # L'utilisateur a fourni un lien (ou skip pour forum/suppression)
        if message_text.lower() in ['non', 'skip', 'aucun', 'pas de lien']:
            state['link'] = 'Aucun'
        else:
            state['link'] = message_text
        
        state['step'] = 'details'
        
        recap = _get_recap(state)
        
        keyboard = [
            [InlineKeyboardButton("🏠 Menu principal", callback_data="back_to_start")],
            [InlineKeyboardButton("⏭️ Passer cette étape", callback_data="skip_details")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{recap}✅ Lien enregistré !\n"
            f"📝 *Étape 4/4 : Détails supplémentaires (optionnel)*\n"
            f"Avez-vous des précisions à ajouter ?\n"
            f"💡 _Exemples : mots-clés, style souhaité, points à mentionner_\n"
            f"💡 _Si non, cliquez sur \"Passer cette étape\"_",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif step == 'details':
        # Finaliser le devis
        if message_text.lower() in ['non', 'skip', 'aucun', 'rien']:
            state['details'] = 'Aucun détail supplémentaire'
        else:
            state['details'] = message_text
        
        # Calculer le prix
        service_type = state.get('service_type', 'autre_plateforme')
        quantity = state.get('quantity', '?')
        service_info = get_service_price(service_type)
        
        # Essayer de convertir la quantité en nombre
        try:
            qty_num = int(''.join(filter(str.isdigit, quantity)))
            price_val = service_info.get('price', 0)
            if price_val == 'Sur devis' or str(price_val).lower() == 'sur devis':
                price_text = "**Sur devis** (notre équipe vous contactera)"
            else:
                # Convertir le prix en nombre si c'est une chaîne
                price_num = float(price_val) if isinstance(price_val, str) and price_val.replace('.', '').replace('-', '').isdigit() else float(price_val)
                total = qty_num * price_num
                currency = service_info.get('currency', 'EUR')
                price_text = f"**≈ {total} {currency}**"
                state['estimated_price'] = f"{total} {currency}"
        except:
            price_text = "**À calculer** (quantité à préciser)"
            state['estimated_price'] = "À calculer"
        
        # Sauvegarder la conversation complète en DB
        conn = _connect()
        try:
            cursor = conn.cursor()
            _execute(cursor, '''
                INSERT INTO conversations (telegram_id, username, first_name, service_type, quantity, link, details, estimated_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_id, state.get('username'), state.get('first_name'), 
                  service_type, quantity, state.get('link', 'Aucun'), state.get('details', 'Aucun détail supplémentaire'), state.get('estimated_price', 'À calculer')))
            conn.commit()
            logger.info(f"Commande sauvegardée: telegram_id={telegram_id}, service={service_type}, quantity={quantity}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde commande: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        # Générer le récapitulatif final avec toutes les informations
        final_recap = _get_recap(state)
        
        # Afficher le récapitulatif final complet avec prix uniquement à la fin
        keyboard = [
            [InlineKeyboardButton("📝 Nouvelle commande", callback_data="new_quote")],
            [InlineKeyboardButton("📋 Mes commandes", callback_data="my_orders")],
            [InlineKeyboardButton("💬 Support", callback_data="contact_support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        recap_final = f"""✅ *Devis généré avec succès !*

{final_recap}💰 *Prix estimé :* {price_text}

━━━━━━━━━━━━━━━━━━
👨‍💼 *Un membre du support vous contactera dans les plus brefs délais.*
Vous pouvez continuer à nous écrire ici pour toute question. Notre support vous répondra rapidement. 💬"""

        state['step'] = 'support_mode'
        
        await update.message.reply_text(recap_final, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif step == 'support_mode' or step == 'menu':
        # Mode support actif
        await update.message.reply_text(
            "✅ Message reçu !\n\n"
            "Notre équipe vous répondra très bientôt. ⏱️",
            parse_mode='Markdown'
        )

def setup_simple_bot(token):
    """Configure le bot simple"""
    init_simple_db()
    
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Bot simple configuré")
    
    return app

