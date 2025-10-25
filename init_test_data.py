"""
Script pour initialiser des données de test dans la base de données
Utile pour tester le dashboard sans avoir à utiliser les bots Telegram
"""

from src.database import (
    init_database, get_db, add_review_to_order
)

def create_test_data():
    """Crée des données de test"""
    print("🔧 Création de données de test...")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO clients (client_id, telegram_id)
        VALUES ('C-T3ST', 123456789)
    """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO workers (worker_id, telegram_id, level, balance, status)
        VALUES 
            ('WRK-001', 111111111, 'Bronze', 25.0, 'active'),
            ('WRK-002', 222222222, 'Certifié', 150.0, 'active'),
            ('WRK-003', 333333333, 'Bronze', 0.0, 'pending')
    """)
    
    cursor.execute("""
        INSERT OR IGNORE INTO orders (order_id, client_id, platform, quantity, target_link, brief, status, price)
        VALUES 
            ('CMD-001', 'C-T3ST', 'Google Reviews', 10, 'https://maps.google.com/restaurant-test', 
             'Restaurant italien, mentionner pâtes maison, ambiance chaleureuse, service rapide. Note moyenne 4.5/5',
             'pending', 50.0),
            ('CMD-002', 'C-T3ST', 'Trustpilot', 5, 'https://trustpilot.com/company-test',
             'Entreprise de services, professionnalisme, rapidité, bon rapport qualité/prix',
             'paid', 25.0)
    """)
    
    conn.commit()
    
    avis_exemples = [
        "Excellent restaurant italien ! Les pâtes sont vraiment faites maison, on sent la différence. L'ambiance est chaleureuse et le service est rapide. Je recommande vivement !",
        "Superbe découverte ! Les plats sont délicieux, l'accueil chaleureux. Les pâtes maison sont un vrai régal. Parfait pour un repas en famille.",
        "Très bon restaurant, les pâtes sont excellentes. Service rapide et efficace. L'ambiance est conviviale. Un très bon rapport qualité/prix.",
    ]
    
    for i, avis in enumerate(avis_exemples):
        add_review_to_order('CMD-002', avis, 4.5)
    
    print("✅ Données de test créées !")
    print("\nVous pouvez maintenant vous connecter au dashboard avec :")
    print("Username: admin")
    print("Password: (celui défini dans .env)")
    
    conn.close()

if __name__ == '__main__':
    init_database()
    create_test_data()
