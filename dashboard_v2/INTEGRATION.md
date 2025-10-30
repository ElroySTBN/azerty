# 🔌 Intégration du Dashboard Mobile dans main.py

## Modification à faire dans main.py

Ajoute ces lignes dans ton fichier `main.py` :

```python
# Après les imports existants
from dashboard_v2.api_mobile import mobile

# Dans la création de l'app Flask (après create_app)
# Si tu utilises src.web_admin.create_app():
def create_app():
    app = Flask(__name__)
    # ... configuration existante ...
    
    # AJOUTER ICI :
    app.register_blueprint(mobile)
    
    return app
```

## Alternative : Intégration rapide

Si tu veux tester rapidement sans tout refaire, ajoute juste ceci dans `main.py` :

```python
from dashboard_v2.api_mobile import mobile
app.register_blueprint(mobile)
```

après la création de l'app Flask.

## URLs disponibles

Une fois intégré :

- **Dashboard mobile** : `http://localhost:8081/mobile`
- **API commandes** : `http://localhost:8081/mobile/api/orders`
- **API messages** : `http://localhost:8081/mobile/api/messages`
- **Chat** : `http://localhost:8081/mobile/chat/<client_id>`
- **Détails** : `http://localhost:8081/mobile/order/<order_id>`

## Test rapide

1. Lance `python main.py`
2. Visite `http://localhost:8081/mobile`
3. Tu devrais voir le dashboard !

Si tu vois une erreur 404, vérifie que le blueprint est bien enregistré.
