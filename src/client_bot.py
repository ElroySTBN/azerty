import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from src.database import get_or_create_client, create_order, get_client_orders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# États de conversation
PLATFORM, QUANTITY, TARGET_LINK, BRIEF = range(4)

# Stockage temporaire des données de commande
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message de bienvenue du bot client"""
    user_id = update.effective_user.id
    client = get_or_create_client(user_id)
    
    welcome_text = f"""🔐 

Service anonyme de gestion de réputation en ligne.

✓ Anonymat total garanti
✓ Paiement crypto uniquement  
✓ Aucune donnée personnelle

Votre ID : #{client['client_id']}"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Commander des avis", callback_data="order_reviews")],
        [InlineKeyboardButton("📊 Mes commandes", callback_data="my_orders")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur les boutons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "order_reviews":
        await start_order_flow(query, context)
    elif query.data == "my_orders":
        await show_my_orders(query, context)
    elif query.data.startswith("platform_"):
        await handle_platform_selection(query, context)
    elif query.data == "back_to_menu":
        await back_to_menu(query, context)

async def start_order_flow(query, context):
    """Démarre le flow de commande d'avis"""
    keyboard = [
        [InlineKeyboardButton("Google Reviews", callback_data="platform_google")],
        [InlineKeyboardButton("Trustpilot", callback_data="platform_trustpilot")],
        [InlineKeyboardButton("Pages Jaunes", callback_data="platform_pagesjaunes")],
        [InlineKeyboardButton("Autre", callback_data="platform_autre")],
        [InlineKeyboardButton("« Retour", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📋 Nouvelle commande\n\nSur quelle plateforme souhaitez-vous des avis ?",
        reply_markup=reply_markup
    )

async def handle_platform_selection(query, context):
    """Gère la sélection de la plateforme"""
    platform = query.data.replace("platform_", "")
    platform_names = {
        "google": "Google Reviews",
        "trustpilot": "Trustpilot",
        "pagesjaunes": "Pages Jaunes",
        "autre": "Autre"
    }
    
    user_id = query.from_user.id
    user_data_store[user_id] = {"platform": platform_names.get(platform, "Autre")}
    
    await query.edit_message_text(
        f"✅ Plateforme sélectionnée : {platform_names.get(platform, 'Autre')}\n\n"
        "Combien d'avis souhaitez-vous ? (entrez un nombre)"
    )
    
    context.user_data['awaiting'] = 'quantity'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les messages texte selon l'état de la conversation"""
    user_id = update.effective_user.id
    awaiting = context.user_data.get('awaiting')
    
    if awaiting == 'quantity':
        try:
            quantity = int(update.message.text)
            if quantity < 1 or quantity > 100:
                await update.message.reply_text("❌ Veuillez entrer un nombre entre 1 et 100.")
                return
            
            user_data_store[user_id]['quantity'] = quantity
            price = quantity * 5.0
            
            await update.message.reply_text(
                f"✅ Quantité : {quantity} avis\n"
                f"💰 Prix estimé : {price} USDT\n\n"
                "Veuillez entrer le lien de la page cible (ex: lien Google Maps, profil Trustpilot, etc.)"
            )
            context.user_data['awaiting'] = 'target_link'
            
        except ValueError:
            await update.message.reply_text("❌ Veuillez entrer un nombre valide.")
    
    elif awaiting == 'target_link':
        user_data_store[user_id]['target_link'] = update.message.text
        
        await update.message.reply_text(
            "✅ Lien enregistré !\n\n"
            "Maintenant, décrivez ce que vous souhaitez dans les avis (brief) :\n"
            "- Points à mentionner\n- Ton souhaité\n- Note moyenne\n"
            "- Toute autre instruction importante"
        )
        context.user_data['awaiting'] = 'brief'
    
    elif awaiting == 'brief':
        user_data_store[user_id]['brief'] = update.message.text
        
        client = get_or_create_client(user_id)
        data = user_data_store[user_id]
        
        order_id = create_order(
            client['client_id'],
            data['platform'],
            data['quantity'],
            data['target_link'],
            data['brief']
        )
        
        await update.message.reply_text(
            f"✅ Commande créée avec succès !\n\n"
            f"📋 Référence : {order_id}\n"
            f"📊 Plateforme : {data['platform']}\n"
            f"🔢 Quantité : {data['quantity']} avis\n"
            f"💰 Prix : {data['quantity'] * 5.0} USDT\n\n"
            f"⏳ Statut : En attente de paiement\n\n"
            f"Notre équipe va rédiger les avis selon votre brief. "
            f"Vous recevrez une notification une fois les avis distribués aux workers."
        )
        
        context.user_data['awaiting'] = None
        del user_data_store[user_id]
        
        keyboard = [[InlineKeyboardButton("📊 Voir mes commandes", callback_data="my_orders")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Que souhaitez-vous faire ?", reply_markup=reply_markup)

async def show_my_orders(query, context):
    """Affiche les commandes du client"""
    user_id = query.from_user.id
    client = get_or_create_client(user_id)
    orders = get_client_orders(client['client_id'])
    
    if not orders:
        await query.edit_message_text(
            "📊 Mes commandes\n\n"
            "Vous n'avez pas encore de commandes.\n\n"
            "Utilisez /start pour commander des avis.",
        )
        return
    
    text = "📊 Mes commandes\n\n"
    
    status_emoji = {
        'pending': '⏳ En attente',
        'paid': '✅ Payé',
        'distributed': '🔄 En cours',
        'completed': '✅ Terminé'
    }
    
    for order in orders[:5]:
        text += f"━━━━━━━━━━━━━━━\n"
        text += f"📋 {order['order_id']}\n"
        text += f"📊 {order['platform']}\n"
        text += f"🔢 {order['quantity']} avis\n"
        text += f"💰 {order['price']} USDT\n"
        text += f"📍 {status_emoji.get(order['status'], order['status'])}\n"
    
    text += "\n━━━━━━━━━━━━━━━"
    
    keyboard = [[InlineKeyboardButton("« Retour au menu", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def back_to_menu(query, context):
    """Retour au menu principal"""
    user_id = query.from_user.id
    client = get_or_create_client(user_id)
    
    welcome_text = f"""🔐 

Service anonyme de gestion de réputation en ligne.

✓ Anonymat total garanti
✓ Paiement crypto uniquement  
✓ Aucune donnée personnelle

Votre ID : #{client['client_id']}"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Commander des avis", callback_data="order_reviews")],
        [InlineKeyboardButton("📊 Mes commandes", callback_data="my_orders")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup)

def setup_client_bot(token):
    """Configure et retourne l'application du bot client"""
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application
