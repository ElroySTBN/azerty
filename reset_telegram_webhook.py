#!/usr/bin/env python3
"""
Script pour réinitialiser le webhook/polling Telegram avant de démarrer l'app
Cela évite les conflits "terminated by other getUpdates request"
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_telegram_connection():
    """Supprime le webhook et nettoie les updates en attente"""
    try:
        from telegram import Bot
        
        token = os.getenv('CLIENT_BOT_TOKEN')
        if not token:
            logger.error("❌ CLIENT_BOT_TOKEN non configuré")
            return False
        
        bot = Bot(token=token)
        
        # Supprimer le webhook (si configuré)
        logger.info("🧹 Suppression du webhook Telegram...")
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook supprimé")
        
        # Attendre un peu pour que Telegram libère la connexion
        await asyncio.sleep(2)
        
        logger.info("✅ Bot Telegram réinitialisé avec succès")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  Impossible de réinitialiser le bot: {e}")
        logger.info("   L'app va quand même démarrer...")
        return False

if __name__ == "__main__":
    asyncio.run(reset_telegram_connection())

