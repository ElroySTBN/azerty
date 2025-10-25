import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from src.database import get_or_create_worker, get_available_tasks, get_task_by_id, accept_task, submit_proof, get_worker_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dossier pour stocker les screenshots
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message de bienvenue du bot worker"""
    user_id = update.effective_user.id
    worker = get_or_create_worker(user_id)
    
    if worker['status'] == 'pending':
        await update.message.reply_text(
            "💰 Bienvenue !\n\n"
            "Votre compte est en cours de validation par notre équipe.\n"
            "Vous recevrez une notification une fois votre compte approuvé.\n\n"
            f"Votre ID : {worker['worker_id']}"
        )
        return
    
    welcome_text = f"""💰 Gagnez de l'argent en ligne

✓ Tâches simples (3-5 min)
✓ 0,15-3$ par tâche
✓ Paiement crypto"""
    
    keyboard = [
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur les boutons"""
    query = update.callback_query
    await query.answer()
    
    if query.data in ["lang_fr", "lang_en"]:
        await show_dashboard(query, context)
    elif query.data == "available_tasks":
        await show_available_tasks(query, context)
    elif query.data == "my_earnings":
        await show_my_earnings(query, context)
    elif query.data.startswith("task_"):
        await show_task_details(query, context)
    elif query.data.startswith("accept_"):
        await accept_task_handler(query, context)
    elif query.data == "back_to_dashboard":
        await show_dashboard(query, context)

async def show_dashboard(query, context):
    """Affiche le dashboard du worker"""
    user_id = query.from_user.id
    worker = get_or_create_worker(user_id)
    
    if worker['status'] != 'active':
        await query.edit_message_text(
            "⏳ Votre compte est en attente de validation.\n\n"
            "Vous recevrez une notification une fois approuvé."
        )
        return
    
    available_tasks_count = len(get_available_tasks())
    
    dashboard_text = f"""👤 Profil : {worker['worker_id']}
⭐ Niveau : {worker['level']}
💰 Solde : {worker['balance']:.2f} USDT"""
    
    keyboard = [
        [InlineKeyboardButton(f"💼 Tâches disponibles ({available_tasks_count})", callback_data="available_tasks")],
        [InlineKeyboardButton("💳 Mes gains", callback_data="my_earnings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(dashboard_text, reply_markup=reply_markup)

async def show_available_tasks(query, context):
    """Affiche la liste des tâches disponibles"""
    tasks = get_available_tasks()
    
    if not tasks:
        await query.edit_message_text(
            "💼 Tâches disponibles\n\n"
            "Aucune tâche disponible pour le moment.\n"
            "Revenez plus tard !",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Retour", callback_data="back_to_dashboard")]])
        )
        return
    
    text = "💼 Tâches disponibles\n\n"
    keyboard = []
    
    platform_emoji = {
        'Google Reviews': '📍',
        'Trustpilot': '⭐',
        'Pages Jaunes': '📒',
        'Autre': '📝'
    }
    
    for task in tasks[:10]:
        order = task  
        text += f"🟢 Tâche #{task['task_id']}\n"
        text += f"Type : Avis {task.get('platform', 'Google')}\n"
        text += f"Rémunération : {task['reward']} USDT\n"
        text += f"Durée : ~5 min\n\n"
        text += "✅ TEXTE FOURNI (copier-coller)\n\n"
        
        keyboard.append([InlineKeyboardButton(f"Voir {task['task_id']}", callback_data=f"task_{task['task_id']}")])
    
    keyboard.append([InlineKeyboardButton("« Retour", callback_data="back_to_dashboard")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_task_details(query, context):
    """Affiche les détails d'une tâche"""
    task_id = query.data.replace("task_", "")
    task = get_task_by_id(task_id)
    
    if not task or task['status'] != 'available':
        await query.answer("Cette tâche n'est plus disponible.", show_alert=True)
        await show_available_tasks(query, context)
        return
    
    text = f"""📋 Détails de la tâche #{task['task_id']}

💰 Rémunération : {task['reward']} USDT
⭐ Note à mettre : {task['rating']}/5

📍 Lien cible :
{task['target_link']}

📝 Texte à copier-coller :
"{task['review_content']}"

━━━━━━━━━━━━━━━━━━━━━
📋 Instructions :
1. Cliquez sur le lien ci-dessus
2. Publiez l'avis avec le texte fourni
3. Mettez la note indiquée ({task['rating']}/5)
4. Prenez un screenshot
5. Envoyez le screenshot ET le lien de votre avis

⚠️ Attention : Suivez exactement les instructions pour être payé."""
    
    keyboard = [
        [InlineKeyboardButton("✅ Accepter cette tâche", callback_data=f"accept_{task_id}")],
        [InlineKeyboardButton("« Retour aux tâches", callback_data="available_tasks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def accept_task_handler(query, context):
    """Gère l'acceptation d'une tâche par un worker"""
    task_id = query.data.replace("accept_", "")
    user_id = query.from_user.id
    worker = get_or_create_worker(user_id)
    
    success = accept_task(task_id, worker['worker_id'])
    
    if success:
        await query.answer("✅ Tâche acceptée !", show_alert=True)
        await query.edit_message_text(
            f"✅ Tâche #{task_id} acceptée !\n\n"
            "Maintenant :\n"
            "1. Publiez votre avis sur la plateforme\n"
            "2. Prenez un screenshot de votre avis publié\n"
            "3. Envoyez-moi le screenshot en photo\n"
            "4. Puis envoyez-moi le lien de votre avis\n\n"
            "💡 Envoyez d'abord la photo, puis le lien dans le message suivant."
        )
        context.user_data['awaiting_proof'] = task_id
    else:
        await query.answer("❌ Cette tâche a déjà été prise.", show_alert=True)
        await show_available_tasks(query, context)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la réception de screenshots"""
    if 'awaiting_proof' not in context.user_data:
        await update.message.reply_text("Utilisez /start pour voir les tâches disponibles.")
        return
    
    task_id = context.user_data['awaiting_proof']
    photo = update.message.photo[-1]
    
    file = await context.bot.get_file(photo.file_id)
    file_path = os.path.join(UPLOAD_FOLDER, f"{task_id}_{photo.file_id}.jpg")
    await file.download_to_drive(file_path)
    
    context.user_data['screenshot_path'] = file_path
    
    await update.message.reply_text(
        "✅ Screenshot reçu !\n\n"
        "Maintenant, envoyez-moi le lien de votre avis publié."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les messages texte (liens de preuve)"""
    if 'awaiting_proof' not in context.user_data or 'screenshot_path' not in context.user_data:
        return
    
    task_id = context.user_data['awaiting_proof']
    screenshot_path = context.user_data['screenshot_path']
    proof_link = update.message.text
    
    submit_proof(task_id, screenshot_path, proof_link)
    
    await update.message.reply_text(
        "✅ Preuve reçue ! En attente de validation.\n\n"
        "Notre équipe va vérifier votre travail.\n"
        "Vous recevrez une notification une fois validé.\n\n"
        "💰 Récompense à venir : Ajoutée à votre solde après validation"
    )
    
    del context.user_data['awaiting_proof']
    del context.user_data['screenshot_path']
    
    keyboard = [[InlineKeyboardButton("📊 Mon dashboard", callback_data="back_to_dashboard")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Que souhaitez-vous faire ?", reply_markup=reply_markup)

async def show_my_earnings(query, context):
    """Affiche les gains du worker"""
    user_id = query.from_user.id
    worker = get_or_create_worker(user_id)
    tasks = get_worker_tasks(worker['worker_id'])
    
    completed_tasks = [t for t in tasks if t['status'] == 'validated']
    pending_tasks = [t for t in tasks if t['status'] == 'pending_validation']
    
    text = f"💳 Mes gains\n\n"
    text += f"💰 Solde actuel : {worker['balance']:.2f} USDT\n"
    text += f"✅ Tâches validées : {len(completed_tasks)}\n"
    text += f"⏳ En attente : {len(pending_tasks)}\n\n"
    
    if completed_tasks:
        text += "━━━━━━━━━━━━━━━\n"
        text += "Dernières tâches validées :\n\n"
        for task in completed_tasks[:5]:
            text += f"• {task['task_id']} : +{task['reward']} USDT\n"
    
    keyboard = [[InlineKeyboardButton("« Retour", callback_data="back_to_dashboard")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def notify_worker(bot, telegram_id, message):
    """Envoie une notification à un worker"""
    try:
        await bot.send_message(chat_id=telegram_id, text=message)
    except Exception as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")

def setup_worker_bot(token):
    """Configure et retourne l'application du bot worker"""
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application
