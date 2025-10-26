#!/usr/bin/env python3
"""Script pour réinitialiser le bot Telegram"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def reset_bot():
    token = os.getenv('CLIENT_BOT_TOKEN')
    if not token:
        print("❌ Token non trouvé dans .env")
        return
    
    bot = Bot(token=token)
    
    try:
        # Supprimer le webhook (si configuré)
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook supprimé et mises à jour en attente effacées")
        
        # Obtenir les infos du bot
        me = await bot.get_me()
        print(f"✅ Bot actif: @{me.username}")
        print(f"   Nom: {me.first_name}")
        print(f"   ID: {me.id}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    asyncio.run(reset_bot())

