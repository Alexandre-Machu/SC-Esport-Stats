# SC-Esport-Stats

## Aperçu
SC-Esport-Stats est une application web construite avec Streamlit qui permet aux utilisateurs de visualiser et d'analyser les statistiques League of Legends de l'équipe SC-Esport. L'application fournit une interface conviviale pour afficher diverses statistiques des joueurs et de l'équipe.

## Structure du Projet
```
sc-esport-stats
├── src
│   ├── app.py                # Point d'entrée principal de l'application Streamlit
│   ├── components
│   │   ├── stats_display.py        # Affichage des statistiques globales
│   │   └── player_stats_display.py # Affichage des statistiques par joueur
│   └── data_processing
│       └── stats_analyzer.py       # Traitement et analyse des données
├── data
│   └── *.json                # Fichiers de données des matchs
├── requirements.txt          # Dépendances Python
└── README.md
```

## Fonctionnalités

### Vue d'Ensemble des Joueurs
- **Affichage par Rôle**: TOP > JUNGLE > MID > ADC > SUPPORT
- **Statistiques Principales**:
  - KDA (Kills/Deaths/Assists)
  - Kill Participation (%)
  - CS/min (tous les rôles sauf support)
  - Vision Score (support uniquement)
  - Nombre de parties jouées
- **Champions**: Affichage des champions les plus joués avec nombre de parties

### Statistiques Détaillées par Joueur
- **Métriques de Performance**:
  - KDA détaillé avec moyennes
  - CS/min calculé à partir de `Missions_CreepScore`
  - Vision score moyen
- **Historique des Matchs**:
  - Liste détaillée des parties
  - Statistiques par partie (KDA, CS, Vision)
  - Résultats (Victoire/Défaite)

## Traitement des Données
- Utilisation de `Missions_CreepScore` pour un calcul précis des CS
- Calcul des moyennes par partie
- Conversion des durées de partie (ms → minutes)
- Tri automatique des joueurs par rôle

## Démarrage

### Prérequis
- Python 3.7+
- Streamlit
- Pandas

### Installation
1. Cloner le dépôt:
```bash
git clone <url-du-dépôt>
cd sc-esport-stats
```

2. Installer les dépendances:
```bash
pip install -r requirements.txt
```

### Lancement
```bash
streamlit run src/app.py
```

## Sources de Données
- Données des matchs: Format JSON
- Icons des champions: Data Dragon API (League of Legends)
- Icons des rôles: Community Dragon