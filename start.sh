#!/bin/bash
# ========================================
# Pub-IA - Script de démarrage
# ========================================

echo "🚀 Démarrage de l'infrastructure Pub-IA..."
echo ""

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Vérifier si .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env manquant !"
    echo "   Copiez .env.example vers .env et remplissez les valeurs :"
    echo "   cp .env.example .env"
    echo ""
    read -p "Voulez-vous créer un .env à partir de .env.example ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ Fichier .env créé. N'oubliez pas de modifier les valeurs sensibles !"
    else
        exit 1
    fi
fi

# Arrêter les containers existants
echo "🛑 Arrêt des containers existants..."
docker-compose down

# Construire et démarrer les services
echo ""
echo "🔨 Construction des images Docker..."
docker-compose up -d --build

# Attendre que les services soient prêts
echo ""
echo "⏳ Attente du démarrage des services..."
sleep 10

# Vérifier la santé des services
echo ""
echo "🏥 Vérification de la santé des services..."

# Vérifier backend
if curl -s http://localhost:8080/health | grep -q '"status":"ok"'; then
    echo "   ✅ Backend: OK"
else
    echo "   ⚠️  Backend: Pas encore prêt (vérifiez les logs: docker-compose logs backend)"
fi

# Afficher les URLs
echo ""
echo "========================================"
echo "🎉 Pub-IA est démarré !"
echo "========================================"
echo ""
echo "📱 URLs :"
echo "   🌐 Frontend (Dashboard): http://localhost:5173"
echo "   🔧 Backend API:          http://localhost:8080"
echo "   💬 Demo Chatbot:         http://localhost:3000"
echo "   🏥 Health Check:         http://localhost:8080/health"
echo ""
echo "📊 Commands utiles :"
echo "   docker-compose logs -f          # Voir les logs"
echo "   docker-compose down             # Arrêter"
echo "   docker-compose restart          # Redémarrer"
echo ""
echo "📚 Documentation:"
echo "   README.md                       # Guide complet"
echo "   demo-chatbot/README.md          # Guide démo"
echo ""
echo "========================================"
