# Pub-IA — Advertising Infrastructure for AI Chatbots

> Google AdSense, but for chatbots.

[![Status](https://img.shields.io/badge/status-MVP-blue)](https://github.com/memphisfils/pub-ia)
[![Stack](https://img.shields.io/badge/stack-Flask%20%7C%20React%20%7C%20PostgreSQL-0077CC)](https://pub-ia.io)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What is Pub-IA?

Pub-IA is an advertising infrastructure for conversational AI applications.

When a chatbot user expresses a purchase intent, Pub-IA:
1. Detects the intent in real-time via GPT-4o mini
2. Selects the most relevant advertisement
3. Injects the ad naturally into the response
4. Revers 70% of the CPM to the publisher

---

## Features

| Feature | Description |
|---------|-------------|
| **Intent Detection** | 15 purchase categories via LLM (GPT-4o mini or Ollama) |
| **Ad Selection** | Highest-bid-wins algorithm with budget/date filtering |
| **Native Format** | Conversation-style ads labeled "Sponsorisé" |
| **Multi-language SDK** | JavaScript/TypeScript + Python |
| **Publisher Dashboard** | Analytics, revenue, app management |
| **Advertiser Dashboard** | Campaigns, budget, creatives, statistics |
| **Rate Limiting** | Redis-based, by plan (free to enterprise) |
| **OAuth2 Auth** | Google login with secure sessions |
| **Rev Share 70/30** | 70% publisher, 30% Pub-IA |

---

## Architecture

```
+-------------------------------------------------------------+
|                     Chatbot User                              |
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
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose v2
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend)
- OpenAI account (or Ollama)

### 1. Clone the repository

```bash
git clone https://github.com/memphisfils/pub-ia.git
cd pub-ia
```

### 2. Configure environment

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**Edit sensitive values in `.env`:**
- `SECRET_KEY`: Generate a random 64-character key
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_CLIENT_ID/SECRET`: Google OAuth2 (optional for local test)

### 3. Start with Docker

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Or manually:**
```bash
docker compose up -d --build
```

### 4. Apply migrations

```bash
docker compose exec backend alembic upgrade head
```

### 5. Access services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend Dashboard | http://localhost:5173 | React app |
| Backend API | http://localhost:8080 | Flask API |
| Demo Chatbot | http://localhost:3000 | Demo app |
| Health Check | http://localhost:8080/health | Service status |

---

## Project Structure

```
pub-ia/
|-- backend/                    # Flask API
|   |-- pubia/
|   |   |-- models/            # SQLAlchemy (users, campaigns, etc.)
|   |   |-- routes/            # Endpoints (sdk, auth, publisher, advertiser)
|   |   |-- services/         # Business logic (intent, ads, revenue)
|   |   |-- app.py            # Flask app factory
|   |-- tests/                # Pytest tests
|   |-- requirements.txt
|-- frontend/                 # React Dashboard
|   |-- src/
|   |   |-- pages/           # Publisher/Advertiser dashboards
|   |   |-- components/      # UI components (Arctic Design)
|   |   |-- services/        # API client
|   |-- package.json
|-- sdk/                     # SDKs
|   |-- js/                 # TypeScript (npm)
|   |-- python/             # Python (pip)
|-- demo-chatbot/             # Demo application
|   |-- index.html          # HTML chatbot
|   |-- style.css          # Arctic Professional design
|   |-- README.md
|-- docker-compose.yml        # Docker dev config
|-- docker-compose.prod.yml   # Docker prod config
|-- Caddyfile              # Reverse proxy SSL
|-- .env.example           # Environment variables
|-- start.sh / start.bat  # Startup scripts
|-- README.md             # This file
```

---

## API Endpoints

### Public SDK (used by publishers)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/analyze-intent` | POST | Detect purchase intent |
| `/v1/get-ad` | POST | Return native advertisement |
| `/v1/track-click` | POST | Log ad click |

**Example usage:**

```bash
# Analyze intent
curl -X POST http://localhost:8080/v1/analyze-intent \
  -H "Authorization: Bearer pk_live_xxx" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quel laptop acheter ?"}'

# Response
{
  "has_intent": true,
  "intent": "achat_tech",
  "confidence": 0.87,
  "category": "Tech",
  "intent_id": "uuid"
}
```

### Auth

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/google` | GET | Google OAuth2 login |
| `/auth/google/callback` | GET | OAuth callback |
| `/auth/logout` | POST | Logout |
| `/auth/me` | GET | User profile |

### Publisher Dashboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/publisher/apps` | GET/POST | Manage publisher apps |
| `/api/publisher/analytics` | GET | Analytics overview |
| `/api/publisher/analytics/daily` | GET | Daily data |
| `/api/publisher/analytics/by-category` | GET | Revenue by category |
| `/api/publisher/revenue` | GET | Balance and history |

### Advertiser Dashboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/advertiser/campaigns` | GET/POST | Manage campaigns |
| `/api/advertiser/campaigns/:id/creatives` | GET/POST | Manage ads |
| `/api/advertiser/campaigns/:id/pause` | POST | Pause campaign |
| `/api/advertiser/budget` | GET | Budget balance |
| `/api/advertiser/budget/deposit` | POST | Add budget |

---

## SDK Integration

### JavaScript / TypeScript

```bash
npm install pub-ia-sdk
```

```javascript
import pubIA from 'pub-ia-sdk';

// Initialization
pubIA.init({ apiKey: 'pk_live_xxx' });

// In your chatbot
const intent = await pubIA.analyzeIntent(userPrompt);

if (intent.hasIntent) {
  const ad = await pubIA.getAd(intent);
  if (ad) {
    response += '\n\n' + ad.nativeText;
  }
}

// Track clicks
pubIA.trackClick(ad.impressionId);
```

### Python

```bash
pip install pub-ia-sdk
```

```python
from pub_ia_sdk import pub_ia

# Initialization
pub_ia.init(api_key="pk_live_xxx")

# In your chatbot
intent = pub_ia.analyze_intent(user_prompt)

if intent["has_intent"]:
    ad = pub_ia.get_ad(intent)
    if ad:
        response += "\n\n" + ad["native_text"]

# Track clicks
pub_ia.track_click(ad["impression_id"])
```

---

## Design System

**Arctic Professional** — Clean, modern, professional

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-main` | `#F4F7FA` | Page background |
| `--bg-card` | `#FFFFFF` | Card background |
| `--accent` | `#0077CC` | Primary color |
| `--success` | `#10B981` | Positive status |
| `--warning` | `#F59E0B` | Sponsored alerts |
| `--font` | `Outfit` | Font family |

---

## Tests

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v --cov=services
```

### Frontend (coming soon)

```bash
cd frontend
npm run test
```

---

## Plans & Pricing

### Publishers

| Plan | Price | Rev Share | Features |
|------|-------|----------|----------|
| **Free** | Free | 70% | 10K impressions/day |
| **Starter** | 49 eur/month | 72% | 50K impressions/day |
| **Pro** | 149 eur/month | 75% | 200K impressions/day |
| **Business** | 399 eur/month | 80% | 1M impressions/day |

### Advertisers

- **CPM**: 5-25 eur depending on category
- **CPC**: Click-based model available
- **Minimum budget**: 50 eur

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt

# Launch Flask
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

# Frontend (coming soon)
cd frontend
npm run test
```

---

## Roadmap

- [x] **Phase 0-3**: Setup, SDK, DB, Auth
- [x] **Phase 4-5**: Publisher/Advertiser Dashboards
- [x] **Phase 6**: MVP Complete + Demo Chatbot
- [ ] **Phase 7**: Publisher subscriptions (Stripe)
- [ ] **Phase 8**: Real-time RTB <100ms
- [ ] **Phase 9**: A/B testing creatives
- [ ] **Phase 10**: Production (Sentry, monitoring)

---

## Contributing

Contributions are welcome.

1. Fork the repo
2. Create your branch (`git checkout -b feature/my-feature`)
3. Commit (`git commit -m 'Add my feature'`)
4. Push (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Team

**Developed by**: Paul fils (Memphis Arslo)  
**Stack**: Flask + React + PostgreSQL + Redis  
**Design**: Arctic Professional  
**Infra**: Hetzner CPX31 + Docker + Caddy

---

**[Full Documentation](https://pub-ia.io/docs)** · **[Report a Bug](https://github.com/memphisfils/pub-ia/issues)** · **[Contact](mailto:contact@pub-ia.io)**