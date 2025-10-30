"""
Bot Telegram Ultra-Simple - Qualification de Leads
Version MVP - Le Bon Mot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import logging
from datetime import datetime
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Grille tarifaire
PRICING = {
    'google': {'price': 18, 'currency': 'EUR', 'name': 'Avis Google', 'guarantee': '6 mois non-drop + replacement gratuit'},
    'trustpilot': {'price': 16, 'currency': 'EUR', 'name': 'Trustpilot', 'guarantee': '1 an non-drop'},
    'forum': {'price': 5, 'currency': 'EUR', 'name': 'Message Forum', 'guarantee': 'Qualité garantie'},
    'pagesjaunes': {'price': 15, 'currency': 'EUR', 'name': 'Pages Jaunes', 'guarantee': 'Non-drop garanti'},
    'autre_plateforme': {'price': 15, 'currency': 'EUR', 'name': 'Autre plateforme', 'guarantee': 'Selon plateforme'},
    'suppression': {'price': 'Sur devis', 'currency': '', 'name': 'Suppression de liens', 'guarantee': 'Travail sur mesure'}
}

# État des conversations
user_conversations = {}

def init_simple_db():
    """Initialise une base de données ultra-simple"""
    conn = sqlite3.connect('lebonmot_simple.db')
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
    conn = sqlite3.connect('lebonmot_simple.db')
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

Bonjour {user.first_name} ! 👋

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
            [InlineKeyboardButton("« Retour", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📋 **Que souhaitez-vous commander ?**\n\nChoisissez le type de service :",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data.startswith("category:"):
        category = data.split(":")[1]
        
        if category == "avis":
            # Choix de la plateforme d'avis
            user_conversations[telegram_id]['step'] = 'service_type'
            
            keyboard = [
                [InlineKeyboardButton("⭐ Avis Google", callback_data="service:google")],
                [InlineKeyboardButton("🌟 Trustpilot", callback_data="service:trustpilot")],
                [InlineKeyboardButton("📒 Pages Jaunes", callback_data="service:pagesjaunes")],
                [InlineKeyboardButton("🌐 Autre plateforme", callback_data="service:autre_plateforme")],
                [InlineKeyboardButton("« Retour", callback_data="new_quote")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "⭐ **Avis sur quelle plateforme ?**\n\nChoisissez la plateforme :",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif category == "forum":
            # Direct au service forum
            user_conversations[telegram_id]['service_type'] = 'forum'
            user_conversations[telegram_id]['step'] = 'quantity'
            
            service_info = PRICING['forum']
            
            await query.edit_message_text(
                f"✅ Service sélectionné : **{service_info['name']}**\n"
                f"💰 Prix unitaire : **{service_info['price']} {service_info['currency']}**\n"
                f"🛡️ Garantie : {service_info['guarantee']}\n\n"
                f"📊 **Étape 1/3 : Quantité**\n\n"
                f"Combien de messages souhaitez-vous ?\n"
                f"_(Répondez avec un nombre, ex: 5, 10, 20...)_",
                parse_mode='Markdown'
            )
        
        elif category == "suppression":
            # Direct au service suppression
            user_conversations[telegram_id]['service_type'] = 'suppression'
            user_conversations[telegram_id]['step'] = 'quantity'
            
            service_info = PRICING['suppression']
            
            await query.edit_message_text(
                f"✅ Service sélectionné : **{service_info['name']}**\n"
                f"💰 Prix : **{service_info['price']}** (estimation sur mesure)\n"
                f"🛡️ Garantie : {service_info['guarantee']}\n\n"
                f"📊 **Étape 1/3 : Détails**\n\n"
                f"Combien de liens à supprimer ?\n"
                f"_(Répondez avec un nombre, ex: 1, 2, 3...)_",
                parse_mode='Markdown'
            )
    
    elif data.startswith("service:"):
        service = data.split(":")[1]
        user_conversations[telegram_id]['service_type'] = service
        user_conversations[telegram_id]['step'] = 'quantity'
        
        service_info = PRICING[service]
        
        await query.edit_message_text(
            f"✅ Service sélectionné : **{service_info['name']}**\n"
            f"💰 Prix unitaire : **{service_info['price']} {service_info['currency']}**\n"
            f"🛡️ Garantie : {service_info['guarantee']}\n\n"
            f"📊 **Étape 2/4 : Quantité**\n\n"
            f"Combien d'{'avis' if service != 'forum' else 'messages'} souhaitez-vous environ ?\n"
            f"_(Répondez avec un nombre ou une estimation, ex: 5, 10, 20...)_",
            parse_mode='Markdown'
        )
    
    elif data == "my_orders":
        # Afficher les commandes du client
        user_conversations[telegram_id]['step'] = 'viewing_orders'
        
        conn = sqlite3.connect('lebonmot_simple.db')
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
            "💬 **Mode Support activé**\n\n"
            "Vous pouvez maintenant discuter directement avec notre équipe.\n"
            "Écrivez votre message ci-dessous ! 👇"
        )
        
        save_message(telegram_id, "👤 Client a contacté le support", 'system')
    
    elif data == "back_to_start":
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

Que souhaitez-vous faire ?"""

        keyboard = [
            [InlineKeyboardButton("📝 Obtenir un devis", callback_data="new_quote")],
            [InlineKeyboardButton("💬 Contacter le support", callback_data="contact_support")],
            [InlineKeyboardButton("ℹ️ Nos garanties", callback_data="guarantees")]
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
        # L'utilisateur a répondu avec une quantité
        state['quantity'] = message_text
        state['step'] = 'link'
        
        await update.message.reply_text(
            f"✅ Quantité notée : **{message_text}**\n\n"
            f"🔗 **Étape 3/4 : Lien (optionnel)**\n\n"
            f"Avez-vous un lien à partager ?\n"
            f"_(Page Google Maps, profil Trustpilot, forum, etc.)_\n\n"
            f"Sinon, répondez **\"non\"** ou **\"skip\"**",
            parse_mode='Markdown'
        )
    
    elif step == 'link':
        # L'utilisateur a fourni un lien (ou skip)
        if message_text.lower() in ['non', 'skip', 'aucun', 'pas de lien']:
            state['link'] = 'Aucun'
        else:
            state['link'] = message_text
        
        state['step'] = 'details'
        
        await update.message.reply_text(
            f"📝 **Étape 4/4 : Détails supplémentaires (optionnel)**\n\n"
            f"Avez-vous des précisions à ajouter ?\n"
            f"_(Points à mentionner, mots-clés, style souhaité, etc.)_\n\n"
            f"Sinon, répondez **\"non\"** ou **\"skip\"**",
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
        conn = sqlite3.connect('lebonmot_simple.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (telegram_id, username, first_name, service_type, quantity, link, details, estimated_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (telegram_id, state.get('username'), state.get('first_name'), 
              service_type, quantity, state.get('link'), state.get('details'), state.get('estimated_price', 'À calculer')))
        conn.commit()
        conn.close()
        
        # Afficher le récapitulatif
        recap = f"""✅ **Devis généré !**

━━━━━━━━━━━━━━━━━━
📋 **Récapitulatif**

🔹 Service : {service_info['name']}
🔹 Quantité : {quantity}
🔹 Lien : {state.get('link', 'Aucun')}
🔹 Détails : {state.get('details', 'Aucun')}

💰 **Prix estimé :** {price_text}
🛡️ **Garantie :** {service_info['guarantee']}

━━━━━━━━━━━━━━━━━━

✨ **Notre équipe vous contacte sous peu !**

Vous pouvez continuer à nous écrire ici pour toute question. Notre support vous répondra rapidement. 💬"""

        state['step'] = 'support_mode'
        
        await update.message.reply_text(recap, parse_mode='Markdown')
    
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

