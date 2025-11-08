#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier l'état de la base de données
"""
import os
import sys
from bot_simple import _connect, _execute, DB_PATH

def check_database():
    print("=" * 60)
    print("DIAGNOSTIC BASE DE DONNÉES REPUTALYS")
    print("=" * 60)
    print(f"\n📍 Chemin DB configuré: {DB_PATH}")
    print(f"📍 Chemin absolu: {os.path.abspath(DB_PATH)}")
    print(f"📍 Fichier existe: {os.path.exists(DB_PATH)}")
    
    if os.path.exists(DB_PATH):
        size = os.path.getsize(DB_PATH)
        print(f"📍 Taille du fichier: {size} bytes ({size/1024:.2f} KB)")
    
    # Vérifier Supabase
    print(f"\n🔍 Configuration Supabase:")
    print(f"   SUPABASE_URL: {'✅ DÉFINI' if os.getenv('SUPABASE_URL') else '❌ NON DÉFINI'}")
    print(f"   SUPABASE_DB_HOST: {'✅ DÉFINI' if os.getenv('SUPABASE_DB_HOST') else '❌ NON DÉFINI'}")
    
    # Tenter de se connecter
    print(f"\n🔌 Tentative de connexion...")
    try:
        conn = _connect()
        is_postgres = hasattr(conn, 'get_dsn_parameters')
        
        if is_postgres:
            print("   ✅ Connexion PostgreSQL (Supabase) réussie")
            db_type = "PostgreSQL (Supabase)"
        else:
            print("   ✅ Connexion SQLite réussie")
            db_type = "SQLite"
        
        cursor = conn.cursor()
        
        # Vérifier si les tables existent
        print(f"\n📊 Vérification des tables...")
        if is_postgres:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('conversations', 'messages', 'pricing')
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                AND name IN ('conversations', 'messages', 'pricing')
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        print(f"   Tables trouvées: {', '.join(tables) if tables else 'AUCUNE'}")
        
        # Compter les conversations
        if 'conversations' in tables:
            _execute(cursor, "SELECT COUNT(*) FROM conversations")
            count_result = cursor.fetchone()
            total_conv = count_result[0] if isinstance(count_result, (tuple, list)) else count_result
            
            print(f"\n💬 Nombre de conversations: {total_conv}")
            
            if total_conv > 0:
                # Afficher les 5 dernières conversations
                _execute(cursor, """
                    SELECT id, telegram_id, first_name, service_type, created_at 
                    FROM conversations 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                conversations = cursor.fetchall()
                print(f"\n📋 5 dernières conversations:")
                for conv in conversations:
                    if is_postgres and isinstance(conv, dict):
                        print(f"   - ID: {conv.get('id')}, Client: {conv.get('first_name')}, Service: {conv.get('service_type')}, Date: {conv.get('created_at')}")
                    elif isinstance(conv, (tuple, list)):
                        print(f"   - ID: {conv[0]}, Client: {conv[2]}, Service: {conv[3]}, Date: {conv[4]}")
                    else:
                        print(f"   - {conv}")
            
            # Compter les messages
            _execute(cursor, "SELECT COUNT(*) FROM messages")
            count_result = cursor.fetchone()
            total_msg = count_result[0] if isinstance(count_result, (tuple, list)) else count_result
            print(f"💬 Nombre de messages: {total_msg}")
        else:
            print(f"\n❌ La table 'conversations' n'existe pas!")
            print(f"   La base de données doit être initialisée.")
        
        conn.close()
        print(f"\n✅ Diagnostic terminé")
        print(f"   Type de DB: {db_type}")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la connexion: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    check_database()

