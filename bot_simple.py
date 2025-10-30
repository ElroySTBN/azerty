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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Grille tarifaire
PRICING = {
    'google': {'price': 18, 'currency': 'EUR', 'name': 'Avis Google'},
    'trustpilot': {'price': 16, 'currency': 'EUR', 'name': 'Trustpilot'},
    'forum': {'price': 5, 'currency': 'EUR', 'name': 'Message Forum'},
    'pagesjaunes': {'price': 15, 'currency': 'EUR', 'name': 'Pages Jaunes'},
    'autre_plateforme': {'price': 15, 'currency': 'EUR', 'name': 'Autre plateforme'},
    'suppression': {'price': 'Sur devis', 'currency': '', 'name': 'Suppression de liens'}
}

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
        service_info = PRICING.get(service_type, {})
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
    - Tente /data/lebonmot_simple.db (Railway)
    - Sinon fallback: ./lebonmot_simple.db
    """
    override = os.getenv('DB_PATH')
    if override:
        os.makedirs(os.path.dirname(override) or '.', exist_ok=True)
        return override

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
                return path
            except (OSError, PermissionError):
                continue
        except Exception:
            continue
    return "lebonmot_simple.db"

DB_PATH = _resolve_db_path()

def _connect():
    """Connexion SQLite optimisée (sans WAL pour éviter problèmes de persistance)"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Optimisations sûres qui ne compromettent pas la persistance
    conn.execute('PRAGMA synchronous=NORMAL')  # Bon compromis vitesse/sécurité
    conn.execute('PRAGMA cache_size=-5000')  # 5MB de cache (raisonnable)
    conn.execute('PRAGMA temp_store=MEMORY')  # Tables temporaires en RAM
    conn.execute('PRAGMA foreign_keys=ON')  # Activer les clés étrangères
    return conn

def init_simple_db():
    """Initialise une base de données ultra-simple"""
    conn = _connect()
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()
    logger.info("✅ Base de données simple initialisée")

def save_message(telegram_id, message, sender='client'):
    """Sauvegarde un message"""
    conn = _connect()
    cursor = conn.cursor()
    
    # Trouver ou créer la conversation
    cursor.execute('SELECT id FROM conversations WHERE telegram_id = ? ORDER BY created_at DESC LIMIT 1', (telegram_id,))
    result = cursor.fetchone()
    
    if result:
        conversation_id = result[0]
    else:
        # Créer une nouvelle conversation
        cursor.execute('INSERT INTO conversations (telegram_id) VALUES (?)', (telegram_id,))
        conversation_id = cursor.lastrowid
    
    # Sauvegarder le message
    cursor.execute('''
        INSERT INTO messages (conversation_id, telegram_id, message, sender)
        VALUES (?, ?, ?, ?)
    ''', (conversation_id, telegram_id, message, sender))
    
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start - Affiche le message d'accueil"""
    user = update.effective_user
    telegram_id = user.id
    
    # Réinitialiser l'état de conversation
    user_conversations[telegram_id] = {'step': 'menu'}
    
    welcome_text = f"""🔐 **Le Bon Mot**
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

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les boutons"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    telegram_id = user.id
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
        
        service_info = PRICING[service]
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
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE telegram_id = ? AND service_type IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 5
        ''', (telegram_id,))
        
        orders = cursor.fetchall()
        conn.close()
        
        if orders:
            orders_text = "📋 **Vos commandes récentes**\n\n"
            for order in orders:
                service_name = PRICING.get(order['service_type'], {}).get('name', order['service_type'])
                orders_text += f"• **{service_name}** - {order['quantity']}\n"
                orders_text += f"  💰 {order['estimated_price']}\n"
                orders_text += f"  📅 {order['created_at'][:10]}\n\n"
            
            orders_text += "\n💬 Pour toute question, contactez le support !"
        else:
            orders_text = "📋 **Aucune commande pour le moment**\n\nCommencez par passer votre première commande ! 🚀"
        
        keyboard = [[InlineKeyboardButton("« Retour au menu", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(orders_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif data == "contact_support":
        user_conversations[telegram_id] = {'step': 'support_mode'}
        
        await query.edit_message_text(
            "💬 *Mode Support activé*\n\n"
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
        service_info = PRICING[service_type]
        
        try:
            qty_num = int(''.join(filter(str.isdigit, quantity)))
            if service_info['price'] == 'Sur devis':
                price_text = "*Sur devis* (notre équipe vous contactera)"
            else:
                total = qty_num * service_info['price']
                price_text = f"*≈ {total} {service_info['currency']}*"
                state['estimated_price'] = f"{total} {service_info['currency']}"
        except:
            price_text = "*À calculer* (quantité à préciser)"
            state['estimated_price'] = "À calculer"
        
        # Sauvegarder en DB
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (telegram_id, username, first_name, service_type, quantity, link, details, estimated_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (telegram_id, state.get('username'), state.get('first_name'), 
              service_type, quantity, state.get('link', 'Aucun'), state.get('details', 'Aucun détail supplémentaire'), state.get('estimated_price', 'À calculer')))
        conn.commit()
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
        
        welcome_text = f"""🔐 *Le Bon Mot*
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
        service_info = PRICING[service_type]
        
        # Essayer de convertir la quantité en nombre
        try:
            qty_num = int(''.join(filter(str.isdigit, quantity)))
            if service_info['price'] == 'Sur devis':
                price_text = "**Sur devis** (notre équipe vous contactera)"
            else:
                total = qty_num * service_info['price']
                price_text = f"**≈ {total} {service_info['currency']}**"
                state['estimated_price'] = f"{total} {service_info['currency']}"
        except:
            price_text = "**À calculer** (quantité à préciser)"
            state['estimated_price'] = "À calculer"
        
        # Sauvegarder la conversation complète en DB
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (telegram_id, username, first_name, service_type, quantity, link, details, estimated_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (telegram_id, state.get('username'), state.get('first_name'), 
              service_type, quantity, state.get('link', 'Aucun'), state.get('details', 'Aucun détail supplémentaire'), state.get('estimated_price', 'À calculer')))
        conn.commit()
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

