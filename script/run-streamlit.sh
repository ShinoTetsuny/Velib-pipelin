#!/bin/bash

echo "=== LANCEMENT DE L'APPLICATION STREAMLIT ==="

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    exit 1
fi

# Installer les dépendances si nécessaire
echo "📦 Vérification des dépendances..."
pip3 install -r requirements.txt

# Lancer Streamlit
echo "🚀 Lancement de l'application Streamlit..."
echo "📱 L'application sera disponible sur : http://localhost:8501"
echo ""

cd app
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
