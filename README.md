Pub-IA — Infrastructure publicitaire native pour les apps IA

Google AdSense, mais pour les chatbots.

## Qu'est-ce que Pub-IA ?

Pub-IA est une infrastructure publicitaire native pour les applications IA conversationnelles.
Lorsqu'un utilisateur de votre chatbot exprime une intention d'achat, Pub-IA :
1. Detecte l'intention en temps reel via GPT-4o mini
2. Selectionne l'annonce la plus pertinente
3. Injecte l'annonce naturellement dans la reponse
4. Reverse 70% du CPM au publisher

## Fonctionnalites

| Fonctionnalite | Description |
|----------------|-------------|
| Detection d'intention | 15 categories d'achat via LLM (GPT-4o mini ou Ollama) |
| Selection d'annonces | Algorithme highest-bid-wins avec filtrage budget/dates |
| Format natif | Annonces conversationnelles labelisees "Sponsorise" |
| SDK Multi-langage | JavaScript/TypeScript + Python |
| Dashboard Publisher | Analytics, revenus, gestion des apps |
| Dashboard Annonceur | Campagnes, budget, creatives, statistiques |
| Rate Limiting | Base Redis, par plan (free -> enterprise) |
| Auth OAuth2 | Connexion Google avec sessions securisees |
| Rev Share 70/30 | 70% publisher, 30% Pub-IA |

## Architecture

+-------------------------------------------------------------+
|                     Utilisateur Chatbot                      |
+--------------------------+----------------------------------+
                           |
                           v
+-------------------------------------------------------------+
|                  Demo Chatbot (HTML/JS)                        |
|              http://localhost:3000                            |
+--------------------------+----------------------------------+
                           | SDK Calls
                           v
+-------------------------------------------------------------+
|                    Caddy Reverse Proxy                        |
|                 http://localhost:8080                          |
+----+-------------+-------------+-----------------------------+
      |             |             |
      v             v             v
+----+----+    +--------+   +--------+
|Front |    | Backend  |   |  Demo  |
|React |    | Flask    |   | Static |
|:5173 |    |  :8000  |   |  :3000 |
+----==+    +====+=====+   +========+
                |            |
         +------+------+   |
         v              v
    +---------+   +---------+
    |PostgreSQL|   | Redis  |
    | :5432  |   | :6380 |
    +---------+   +---------+

## Demarrage rapide

### Prérequis

- Docker & Docker Compose v2
- Python 3.11+ (pour développement local)
- Node.js 18+ (pour frontend)
- Compte OpenAI (ou Ollama)

### 1. Cloner le repository

```bash
git clone https://github.com/memphisfils/pub-ia.git
cd pub-ia
```

### 2. Configurer l'environnement

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Modifier les valeurs sensibles dans `.env` :
- `SECRET_KEY` : Générer une clé aléatoire de 64 caractères
- `OPENAI_API_KEY` : Votre clé API OpenAI
- `GOOGLE_CLIENT_ID/SECRET` : OAuth2 Google (optionnel pour test local)

### 3. Démarrer avec Docker

**Windows :**
```bash
start.bat
```

**Linux/Mac :**
```bash
chmod +x start.sh
./start.sh
```

**Ou manuellement :**
```bash
docker compose up -d --build
```

### 4. Appliquer les migrations

```bash
docker compose exec backend alembic upgrade head
```

### 5. Accéder aux services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend Dashboard | http://localhost:5173 | React app |
| Backend API | http://localhost:8080 | Flask API |
| Demo Chatbot | http://localhost:3000 | App de demonstration |
| Health Check | http://localhost:8080/health | Status des services |

## Structure du projet

```
pub-ia/
|-- backend/                    # API Flask
|   |-- pubia/
|   |   |-- models/            # SQLAlchemy (users, campaigns, etc.)
|   |   |-- routes/            # Endpoints (sdk, auth, publisher, advertiser)
|   |   |-- services/         # Logique métier (intent, ads, revenue)
|   |   |-- app.py            # Factory d'application Flask
|   |-- tests/                # Tests pytest
|   |-- requirements.txt
|-- frontend/                 # Dashboard React
|   |-- src/
|   |   |-- pages/           # Tableaux de bord publisher/annonceur
|   |   |-- components/      # Composants UI (Design Arctic)
|   |   |-- services/        # Client API
|   |-- package.json
|-- sdk/                     # SDKs
|   |-- js/                 # TypeScript (npm)
|   |-- python/             # Python (pip)
|-- demo-chatbot/             # Application de demonstration
|   |-- index.html          # Chatbot HTML/JS
|   |-- style.css          # Design Arctic Professional
|   |-- README.md
|-- docker-compose.yml        # Configuration Docker dev
|-- docker-compose.prod.yml   # Configuration Docker prod
|-- Caddyfile              # Proxy inverse SSL
|-- .env.example           # Variables d'environnement
|-- start.sh / start.bat  # Scripts de démarrage
|-- README.md             # Ce fichier
```

## Points d'entrée API

### SDK publique (utilisée par les publishers)

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/v1/analyze-intent` | POST | Detecte une intention d'achat |
| `/v1/get-ad` | POST | Retourne une annonce native |
| `/v1/track-click` | POST | Enregistre un clic sur annonce |

**Exemple d'utilisation :**

```bash
# Analyser l'intention
curl -X POST http://localhost:8080/v1/analyze-intent \
  -H "Authorization: Bearer pk_live_xxx" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quel laptop acheter ?"}'

# Réponse
{
  "has_intent": true,
  "intent": "achat_tech",
  "confidence": 0.87,
  "category": "Tech",
  "intent_id": "uuid"
}
```

### Auth

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/auth/google` | GET | Connexion OAuth2 Google |
| `/auth/google/callback` | GET | Callback OAuth |
| `/auth/logout` | POST | Déconnexion |
| `/auth/me` | GET | Profil utilisateur |

### Dashboard Publisher

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/api/publisher/apps` | GET/POST | Gérer les apps publisher |
| `/api/publisher/analytics` | GET | Vue d'ensemble analytics |
| `/api/publisher/analytics/daily` | GET | Données jour par jour |
| `/api/publisher/analytics/by-category` | GET | Revenus par catégorie |
| `/api/publisher/revenue` | GET | Solde et historique |

### Dashboard Annonceur

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/api/advertiser/campaigns` | GET/POST | Gérer les campagnes |
| `/api/advertiser/campaigns/:id/creatives` | GET/POST | Gérer les annonces |
| `/api/advertiser/campaigns/:id/pause` | POST | Mettre en pause campagne |
| `/api/advertiser/budget` | GET | Solde budget |
| `/api/advertiser/budget/deposit` | POST | Ajouter du budget |

## Intégration SDK

### JavaScript / TypeScript

```bash
npm install pub-ia-sdk
```

```javascript
import pubIA from 'pub-ia-sdk';

// Initialisation
pubIA.init({ apiKey: 'pk_live_xxx' });

// Dans votre chatbot
const intent = await pubIA.analyzeIntent(userPrompt);

if (intent.hasIntent) {
  const ad = await pubIA.getAd(intent);
  if (ad) {
    response += '\n\n' + ad.nativeText;
  }
}

// Tracker les clics
pubIA.trackClick(ad.impressionId);
```

### Python

```bash
pip install pub-ia-sdk
```

```python
from pub_ia_sdk import pub_ia

# Initialisation
pub_ia.init(api_key="pk_live_xxx")

# Dans votre chatbot
intent = pub_ia.analyze_intent(user_prompt)

if intent["has_intent"]:
    ad = pub_ia.get_ad(intent)
    if ad:
        response += "\n\n" + ad["native_text"]

# Tracker les clics
pub_ia.track_click(ad["impression_id"])
```

## Système de design

**Arctic Professional** — Design propre, moderne, professionnel

| Jeton | Valeur | Usage |
|-------|--------|-------|
| `--bg-main` | `#F4F7FA` | Fond de page |
| `--bg-card` | `#FFFFFF` | Fond des cartes |
| `--accent` | `#0077CC` | Couleur principale |
| `--success` | `#10B981` | Statut positif |
| `--warning` | `#F59E0B` | Alertes sponsorisees |
| `--font` | `Outfit` | Police de caractere |

## Tests

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v --cov=services
```

### Frontend (à venir)

```bash
cd frontend
npm run test
```

## Plans et tarifs

### Publishers

| Plan | Prix | Rev Share | Fonctionnalités |
|------|------|-----------|-----------------|
| **Free** | Gratuit | 70% | 10K impressions/jour |
| **Starter** | 49 eur/mois | 72% | 50K impressions/jour |
| **Pro** | 149 eur/mois | 75% | 200K impressions/jour |
| **Business** | 399 eur/mois | 80% | 1M impressions/jour |

### Annonceurs

- **CPM** : 5-25 eur selon la catégorie
- **CPC** : Modèle au clic disponible
- **Budget minimum** : 50 eur

## Développement local

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt

# Lancer Flask
flask run --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
# Backend
cd backend
pytest tests/ -v --cov=services

# Frontend (à venir)
cd frontend
npm run test
```

## Feuille de route

- [x] **Phase 0-3** : Mise en place, SDK, BD, Auth
- [x] **Phase 4-5** : Tableaux de bord Publisher/Annonceur
- [x] **Phase 6** : MVP complet + Démo Chatbot
- [ ] **Phase 7** : Abonnement publisher (Stripe)
- [ ] **Phase 8** : RTB temps réel <100ms
- [ ] **Phase 9** : A/B testing creatives
- [ ] **Phase 10** : Production (Sentry, monitoring)

## Contribuer

Les contributions sont les bienvenues.

1. Fork le dépôt
2. Créez votre branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committez (`git commit -m 'Ajout de super fonctionnalite'`)
4. Push (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

## Licence

Licence MIT — voir [LICENSE](LICENSE) pour plus de détails.

## Équipe

**Développé par** : Paul fils (Memphis Arslo)  
**Stack** : Flask + React + PostgreSQL + Redis  
**Design** : Arctic Professional  
**Infra** : Hetzner CPX31 + Docker + Caddy

---

[Documentation complète](https://pub-ia.io/docs) · [Signaler un bug](https://github.com/memphisfils/pub-ia/issues) · [Contacter l'équipe](mailto:contact@pub-ia.io)