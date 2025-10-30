"""
Point d'entrée ultra-simple - Le Bon Mot MVP
Lance le bot Telegram et le dashboard admin
"""
import os
import asyncio
import logging
import signal
from threading import Thread
from dotenv import load_dotenv

from bot_simple import setup_simple_bot
from dashboard_simple import create_simple_dashboard, set_bot

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Réduire le bruit des logs
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

def run_flask():
    """Lance le dashboard Flask"""
    # S'assurer que la base SQLite est initialisée même si le bot ne s'est pas encore lancé
    try:
        from bot_simple import init_simple_db
        init_simple_db()
    except Exception as e:
        logger.warning(f"⚠️ Impossible d'initialiser la base avant Flask: {e}")
    app = create_simple_dashboard()
    port = int(os.getenv('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def main():
    """Point d'entrée principal"""
    logger.info("🚀 Démarrage du Bot Le Bon Mot - Version Simple...")
    
    # Token du bot
    CLIENT_BOT_TOKEN = os.getenv('CLIENT_BOT_TOKEN')
    
    if not CLIENT_BOT_TOKEN:
        logger.error("❌ CLIENT_BOT_TOKEN manquant dans .env")
        logger.info("\n" + "="*50)
        logger.info("⚠️  CONFIGURATION REQUISE")
        logger.info("="*50)
        logger.info("\nAjoutez dans votre fichier .env :")
        logger.info("CLIENT_BOT_TOKEN=votre_token_telegram")
        logger.info("\n💡 Créez un bot sur @BotFather")
        logger.info("="*50 + "\n")
        return
    
    # Démarrer Flask en priorité (pour Railway)
    logger.info("🌐 Démarrage du dashboard admin...")
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logger.info("✅ Dashboard admin démarré !")
    logger.info(f"📊 Dashboard: http://localhost:{os.getenv('PORT', 8081)}")
    
    # Démarrer le bot Telegram
    try:
        logger.info("\n🤖 Démarrage du bot Telegram...")
        bot_app = setup_simple_bot(CLIENT_BOT_TOKEN)
        
        async with bot_app:
            await bot_app.start()
            await bot_app.updater.start_polling()
            
            # Connecter le bot au dashboard pour les réponses
            loop = asyncio.get_event_loop()
            set_bot(bot_app, loop)
            
            logger.info("✅ Bot Telegram démarré et connecté !")
            
            logger.info("\n" + "="*50)
            logger.info("🎉 LE BON MOT - OPÉRATIONNEL !")
            logger.info("="*50)
            logger.info(f"\n📱 Bot Telegram : @{(await bot_app.bot.get_me()).username}")
            logger.info(f"📊 Dashboard Admin : http://localhost:{os.getenv('PORT', 8081)}")
            logger.info("\n💡 Tout est prêt ! Les clients peuvent commander.")
            logger.info("   Vous gérez les devis depuis le dashboard.\n")
            logger.info("Ctrl+C pour arrêter\n")
            
            # Gestion propre des signaux pour Railway/Heroku-like
            stop_event = asyncio.Event()

            def _handle_signal(*_):
                logger.info("\n🛑 Signal reçu, arrêt en cours…")
                stop_event.set()

            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    asyncio.get_running_loop().add_signal_handler(sig, _handle_signal)
                except NotImplementedError:
                    # Windows/limitations: on ignore
                    pass

            # Garder l'app active jusqu'au signal d'arrêt
            await stop_event.wait()
            logger.info("Arrêt du bot…")
            await bot_app.updater.stop()
            await bot_app.stop()
    
    except Exception as e:
        logger.error(f"❌ Erreur bot Telegram : {e}", exc_info=True)
        logger.warning("\n⚠️  Le dashboard reste actif même sans bot")
        logger.info(f"📊 Dashboard: http://localhost:{os.getenv('PORT', 8081)}")
        
        # Garder Flask actif
        await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Arrêt du Bot Le Bon Mot...")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)

