#!/bin/bash

# Script de planification pour exécuter le batch Velib toutes les 24h

LOG_FILE="./logs/velib-batch-scheduler.log"
BATCH_SCRIPT="./run-batch.sh"
CRON_JOB="0 2 * * * cd $(pwd) && $BATCH_SCRIPT >> $LOG_FILE 2>&1" # Tous les jours à 02:00

# Fonction pour logger
log() {
    # Créer le dossier logs s'il n'existe pas
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Fonction pour vérifier si Docker est en cours d'exécution
check_docker() {
    docker info > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log "❌ Docker n'est pas en cours d'exécution. Veuillez démarrer Docker."
        return 1
    fi
    return 0
}

# Fonction pour vérifier si le cluster est en cours d'exécution
check_cluster() {
    local running_containers=$(docker-compose ps -q | wc -l)
    if [ "$running_containers" -eq 0 ]; then
        log "❌ Le cluster Docker n'est pas démarré. Lancement du cluster..."
        docker-compose up -d >> "$LOG_FILE" 2>&1
        sleep 60 # Attendre que les services démarrent
        running_containers=$(docker-compose ps -q | wc -l)
        if [ "$running_containers" -eq 0 ]; then
            log "❌ Échec du démarrage du cluster. Abandon de l'exécution du batch."
            return 1
        else
            log "✅ Cluster démarré avec succès."
        fi
    fi
    return 0
}

case "$1" in
    --schedule)
        log "Configuration de la tâche cron pour l'exécution quotidienne du batch à 02:00..."
        (crontab -l 2>/dev/null | grep -v -F "$BATCH_SCRIPT"; echo "$CRON_JOB") | crontab -
        if [ $? -eq 0 ]; then
            log "✅ Tâche cron configurée avec succès."
            log "Pour vérifier: crontab -l"
        else
            log "❌ Erreur lors de la configuration de la tâche cron."
        fi
        ;;
    --run-batch)
        log "Exécution immédiate du job batch Velib..."
        if check_docker && check_cluster; then
            "$BATCH_SCRIPT"
            log "✅ Exécution du job batch terminée."
        else
            log "❌ Le job batch n'a pas pu être exécuté en raison de problèmes d'infrastructure."
        fi
        ;;
    --logs)
        log "Affichage des logs du scheduler:"
        if [ -f "$LOG_FILE" ]; then
            cat "$LOG_FILE"
        else
            log "Aucun fichier de log trouvé à $LOG_FILE."
        fi
        ;;
    --stop)
        log "Arrêt de la tâche cron pour le batch Velib..."
        (crontab -l 2>/dev/null | grep -v -F "$BATCH_SCRIPT") | crontab -
        if [ $? -eq 0 ]; then
            log "✅ Tâche cron arrêtée avec succès."
        else
            log "❌ Erreur lors de l'arrêt de la tâche cron."
        fi
        ;;
    *)
        echo "Usage: $0 {--schedule|--run-batch|--logs|--stop}"
        echo ""
        echo "Options:"
        echo "  --schedule    : Planifier l'exécution quotidienne à 02:00"
        echo "  --run-batch   : Exécuter le batch immédiatement"
        echo "  --logs        : Afficher les logs du scheduler"
        echo "  --stop        : Arrêter la planification"
        exit 1
        ;;
esac