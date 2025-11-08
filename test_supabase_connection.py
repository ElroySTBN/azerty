#!/usr/bin/env python3
"""
Script de test de connexion Supabase
Teste la connexion avec différentes configurations pour diagnostiquer les problèmes
"""
import os
import sys
import time
from urllib.parse import urlparse

def test_supabase_connection():
    print("=" * 60)
    print("TEST DE CONNEXION SUPABASE")
    print("=" * 60)
    
    # Charger les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    db_host = os.getenv('SUPABASE_DB_HOST')
    db_port = os.getenv('SUPABASE_DB_PORT', '5432')
    db_name = os.getenv('SUPABASE_DB_NAME')
    db_user = os.getenv('SUPABASE_DB_USER')
    db_password = os.getenv('SUPABASE_DB_PASSWORD')
    
    print(f"\n📋 Configuration détectée:")
    print(f"   SUPABASE_URL: {'✅ DÉFINI' if supabase_url else '❌ NON DÉFINI'}")
    if supabase_url:
        # Masquer le mot de passe dans l'URL
        safe_url = supabase_url
        if '@' in safe_url:
            parts = safe_url.split('@')
            if ':' in parts[0]:
                user_pass = parts[0].split(':')
                if len(user_pass) == 2:
                    safe_url = f"{user_pass[0]}:****@{parts[1]}"
        print(f"   URL: {safe_url}")
    
    print(f"   SUPABASE_DB_HOST: {'✅ DÉFINI' if db_host else '❌ NON DÉFINI'}")
    if db_host:
        print(f"   Host: {db_host}")
    print(f"   Port: {db_port}")
    
    if not supabase_url and not (db_host and db_name and db_user and db_password):
        print("\n❌ Aucune configuration Supabase trouvée!")
        print("   Configurez SUPABASE_URL ou les variables SUPABASE_DB_*")
        return False
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        print("\n✅ psycopg2-binary installé")
    except ImportError:
        print("\n❌ psycopg2-binary non installé!")
        print("   Installez-le avec: pip install psycopg2-binary")
        return False
    
    # Tester différentes configurations
    print("\n🔌 Tests de connexion...")
    
    if supabase_url:
        # Tester l'URL telle quelle
        print(f"\n1️⃣ Test avec SUPABASE_URL (telle quelle)")
        try:
            conn = psycopg2.connect(supabase_url, connect_timeout=30)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            print("   ✅ Connexion réussie!")
            
            # Tester une requête réelle
            conn = psycopg2.connect(supabase_url, connect_timeout=30)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            print(f"   ✅ Test requête réussie: {count} conversations trouvées")
            return True
            
        except Exception as e:
            print(f"   ❌ Échec: {e}")
            
            # Essayer de convertir pooler en direct
            if 'pooler' in supabase_url or ':6543' in supabase_url:
                print(f"\n2️⃣ Test avec URL convertie (port direct 5432)")
                try:
                    # Essayer avec port 5432
                    test_url = supabase_url.replace(':6543', ':5432')
                    if 'pooler.supabase.com' in test_url:
                        # Extraire les infos de l'URL
                        parsed = urlparse(test_url)
                        # Remplacer pooler par db et .com par .co
                        host_parts = parsed.hostname.split('.')
                        if 'pooler' in host_parts:
                            # Format: aws-1-eu-west-3.pooler.supabase.com
                            # On ne peut pas vraiment convertir sans connaître le vrai host
                            print("   ⚠️ Impossible de convertir automatiquement pooler -> db")
                            print("   💡 Solution: Utilisez l'URL de connexion directe depuis Supabase Dashboard")
                        else:
                            conn = psycopg2.connect(test_url, connect_timeout=30)
                            cursor = conn.cursor()
                            cursor.execute('SELECT 1')
                            cursor.close()
                            conn.close()
                            print("   ✅ Connexion réussie avec port 5432!")
                            return True
                except Exception as e2:
                    print(f"   ❌ Échec: {e2}")
    
    elif db_host and db_name and db_user and db_password:
        # Tester avec les variables séparées
        print(f"\n1️⃣ Test avec variables séparées")
        
        # Tester d'abord le port configuré
        ports_to_try = []
        if db_port == '6543' or 'pooler' in db_host:
            print("   ⚠️ Pooler détecté, test des deux ports...")
            # Essayer port direct puis pooler
            if 'pooler' in db_host:
                # Essayer de convertir
                direct_host = db_host.replace('pooler', 'db').replace('.com', '.co')
                ports_to_try = [
                    (direct_host, '5432', 'Host direct (converti)'),
                    (db_host, '5432', 'Pooler host, port direct'),
                    (db_host, '6543', 'Pooler (original)')
                ]
            else:
                ports_to_try = [
                    (db_host, '5432', 'Port direct'),
                    (db_host, '6543', 'Port pooler')
                ]
        else:
            ports_to_try = [(db_host, db_port, 'Port configuré')]
        
        for try_host, try_port, desc in ports_to_try:
            try:
                print(f"\n   🔄 Test {desc}: {try_host}:{try_port}")
                conn = psycopg2.connect(
                    host=try_host,
                    port=try_port,
                    database=db_name,
                    user=db_user,
                    password=db_password,
                    connect_timeout=30
                )
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
                cursor.close()
                
                # Tester une requête réelle
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM conversations")
                count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                print(f"   ✅ Connexion réussie: {count} conversations trouvées")
                return True
                
            except Exception as e:
                print(f"   ❌ Échec: {e}")
    
    print("\n❌ Aucune connexion réussie")
    print("\n💡 Recommandations:")
    print("   1. Vérifiez vos identifiants Supabase")
    print("   2. Utilisez l'URL de connexion DIRECTE (port 5432) au lieu du pooler (port 6543)")
    print("   3. Vérifiez que votre IP n'est pas bloquée par Supabase")
    print("   4. Vérifiez les logs Railway pour plus de détails")
    
    return False

if __name__ == '__main__':
    test_supabase_connection()

