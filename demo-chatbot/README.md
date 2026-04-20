# 🤖 Pub-IA Demo Chatbot

**App de démonstration pour l'intégration du SDK Pub-IA**

Cette application montre comment intégrer la publicité native Pub-IA dans un chatbot conversationnel en **15 minutes**.

---

## 🚀 Démarrage rapide

### 1. Lancer l'infrastructure Pub-IA

```bash
# À la racine du projet pub-ia
docker compose up -d
```

### 2. Ouvrir la démo

```bash
# Ouvrir simplement le fichier HTML dans votre navigateur
open demo-chatbot/index.html
# ou
start demo-chatbot\index.html  # Windows
```

### 3. Tester !

Posez des questions avec intention d'achat :
- *"Quel laptop acheter pour travailler ?"*
- *"Quelle crème anti-âge tu recommandes ?"*
- *"Je cherche des sneakers de running"*

---

## 📁 Structure

```
demo-chatbot/
├── index.html          ← Application complète (HTML + JS inline)
├── style.css           ← Design Arctic Professional
└── README.md           ← Ce fichier
```

---

## 🔧 Configuration

### Clé API

Dans `index.html`, modifiez cette ligne avec votre vraie clé API :

```javascript
const API_KEY = 'pk_live_demo_key'; // ← Remplacer par votre clé
```

Pour obtenir une clé API :
1. Connectez-vous au dashboard Pub-IA
2. Créez une nouvelle app publisher
3. Copiez la clé API générée

### Endpoint API

Par défaut, le SDK pointe vers `http://localhost:8000/v1`.

Pour la production, changez :

```javascript
const API_ENDPOINT = 'https://pub-ia.io/v1';
```

---

## 💡 Comment ça marche

### Flux d'intégration

```
1. Utilisateur tape un prompt
   ↓
2. SDK analyse l'intention (POST /v1/analyze-intent)
   ↓
3. Si intention détectée (confidence > 0.65)
   ↓
4. SDK récupère l'annonce (POST /v1/get-ad)
   ↓
5. Annonce affichée nativement dans la conversation
   ↓
6. Si l'utilisateur clique, tracker le clic (POST /v1/track-click)
```

### Code d'intégration minimal

```javascript
// 1. Analyser l'intention
const intent = await fetch('https://pub-ia.io/v1/analyze-intent', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer pk_live_xxx'
  },
  body: JSON.stringify({ prompt: userMessage })
});

const intentData = await intent.json();

// 2. Si intention détectée, récupérer l'annonce
if (intentData.has_intent) {
  const ad = await fetch('https://pub-ia.io/v1/get-ad', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer pk_live_xxx'
    },
    body: JSON.stringify({
      intent: intentData.intent,
      intent_id: intentData.intent_id,
      confidence: intentData.confidence
    })
  });

  const adData = await ad.json();
  
  // 3. Afficher l'annonce native
  displayAd(adData.native_text);
}
```

---

## 🎨 Design

Le chatbot utilise le **Design System Arctic Professional** :

- **Police** : Outfit (Google Fonts)
- **Couleurs** : 
  - Fond : `#F4F7FA`
  - Accent : `#0077CC`
  - Cartes : `#FFFFFF` avec bordure `#E1E8F0`
- **Annonces** : Bordure amber `#F59E0B` avec label "Sponsorisé"

---

## 📱 Responsive

L'app est **mobile-first** et s'adapte à toutes les tailles d'écran :

- **Desktop** : Max 600px centré
- **Tablette** (< 768px) : Plein écran
- **Mobile** (< 480px) : Optimisé pour petits écrans

---

## 🔍 Exemples de prompts

### ✅ Avec intention d'achat (détectée)

| Prompt | Catégorie détectée |
|--------|-------------------|
| "Quel laptop acheter pour travailler ?" | achat_tech |
| "Quelle crème anti-âge tu recommandes ?" | achat_beaute |
| "Je cherche des sneakers de running" | achat_sport |
| "Quelle banque en ligne choisir ?" | achat_finance |
| "Je veux réserver un hôtel à Paris" | achat_voyage |

### ❌ Sans intention d'achat (non détectée)

| Prompt | Raison |
|--------|--------|
| "Quelle est la météo demain ?" | Pas d'achat |
| "Comment apprendre Python ?" | Programmation |
| "Combien font 25% de 200 ?" | Maths |
| "Raconte-moi une blague" | Divertissement |

---

## 🛠️ Personnalisation

### Changer les réponses du bot

Dans `index.html`, modifiez la fonction `generateBotResponse()` :

```javascript
function generateBotResponse(prompt) {
  // Intégrer votre vraie LLM ici (OpenAI, Ollama, etc.)
  return "Ma réponse personnalisée...";
}
```

### Style des annonces

Dans `style.css`, modifiez les classes `.ad-label`, `.ad-cta`, etc.

---

## 📊 Métriques

La démo inclut le tracking des clics pour mesurer :

- **Impressions** : Nombre d'annonces affichées
- **Clics** : Nombre de clics sur les annonces
- **CTR** : Taux de clic (clics / impressions)

---

## ⚠️ Notes

- Cette démo utilise une **clé API en dur** — en production, utilisez des variables d'environnement
- Les réponses du bot sont **simulées** — intégrez votre vrai LLM
- Le SDK est appelé **directement** — dans une vraie app, utilisez le package npm `pub-ia-sdk`

---

## 📚 Ressources

- [Documentation Pub-IA](https://pub-ia.io/docs)
- [SDK JavaScript](https://github.com/memphisfils/pub-ia/tree/main/sdk/js)
- [API Reference](https://pub-ia.io/api)

---

**Développé avec ❤️ par l'équipe Pub-IA**
