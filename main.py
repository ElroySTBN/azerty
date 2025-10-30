import os
import asyncio
import logging
from threading import Thread
from dotenv import load_dotenv

from src.database import init_database
from src.client_bot import setup_client_bot
from src.web_admin import set_client_bot
from miniapp_railway import app as miniapp_flask

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

def run_flask_app():
    """Lance l'application Flask (Dashboard Admin + Mini App) dans un thread séparé"""
    miniapp_flask.run(host='0.0.0.0', port=int(os.getenv('PORT', 8081)), debug=False, use_reloader=False)

async def main():
    """
    Point d'entrée principal
    Lance le bot client et le dashboard Flask
    (Workers gérés manuellement)
    """
    logger.info("🚀 Démarrage de la Marketplace d'avis...")
    
    init_database()
    logger.info("✅ Base de données initialisée")
    
    CLIENT_BOT_TOKEN = os.getenv('CLIENT_BOT_TOKEN')
    
    if not CLIENT_BOT_TOKEN:
        logger.error("❌ ERREUR: Le token du bot client n'est pas configuré")
        logger.info("\n" + "="*70)
        logger.info("⚠️  CONFIGURATION REQUISE")
        logger.info("="*70)
        logger.info("\n1. Créez un bot sur Telegram via @BotFather")
        logger.info("   - Bot CLIENT : pour les entreprises qui commandent")
        logger.info("\n2. Configurez la variable suivante dans .env :")
        logger.info("   - CLIENT_BOT_TOKEN")
        logger.info("   - ADMIN_PASSWORD")
        logger.info("\n💡 Guide complet : Voir README.md")
        logger.info("="*70 + "\n")
        return
    
    logger.info("🤖 Configuration du bot Telegram Client...")
    client_app = setup_client_bot(CLIENT_BOT_TOKEN)
    
    logger.info("🌐 Démarrage du dashboard Flask...")
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    logger.info("✅ Tous les services sont démarrés !")
    logger.info("\n" + "="*50)
    logger.info("📊 Dashboard Admin: http://localhost:8081/admin")
    logger.info("🚀 Mini App: http://localhost:8081")
    logger.info("   Username: admin")
    logger.info("   Password: admin123")
    logger.info("="*50 + "\n")
    
    async with client_app:
        await client_app.start()
        await client_app.updater.start_polling()
        
        # Connecter le bot client au dashboard pour les notifications
        loop = asyncio.get_event_loop()
        set_client_bot(client_app, loop)
        
        logger.info("✅ Bot Client démarré et en écoute")
        
        logger.info("\n🎉 Marketplace opérationnelle !")
        logger.info("Vous pouvez maintenant :")
        logger.info("  - Accéder à la Mini App sur http://localhost:8081")
        logger.info("  - Accéder au dashboard admin sur http://localhost:8081/admin")
        logger.info("  - Parler au bot sur Telegram")
        logger.info("\n⚠️  MODE SIMPLIFIÉ : Workers désactivés")
        logger.info("   Vous gérez les commandes manuellement via le dashboard")
        logger.info("\nAppuyez sur Ctrl+C pour arrêter\n")
        
        await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Arrêt de la marketplace...")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
