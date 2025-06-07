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
├── .streamlit
│   └── config.toml          # Configuration Streamlit avec thème personnalisé
└── README.md
```

## Fonctionnalités
- **Navigation par Rôle**: Accès facile aux statistiques des joueurs par rôle (TOP, JUNGLE, MID, ADC, SUPPORT)
- **Statistiques des Joueurs**:
  - Moyenne KDA, éliminations, morts et assistances (avec gestion sécurisée des nombres)
  - Statistiques CS par minute (avec valeurs par défaut)
  - Suivi du score de vision
  - Analyse des champions joués
- **Historique des Matchs**:
  - Historique détaillé avec icônes des champions
  - Suivi Victoires/Défaites avec indicateurs visuels (✅/❌)
  - Métriques de performance par partie (avec validation des données)
  - Statistiques par champion
- **Analyses Visuelles**:
  - Distribution victoires/défaites par champion
  - Tendances de performance
  - Visualisations de données interactives avec Plotly
- **Gestion des Données**:
  - Conversions numériques sécurisées
  - Valeurs par défaut pour les données manquantes
  - Gestion robuste des erreurs

## Démarrage

### Prérequis
- Python 3.7 ou supérieur
- Streamlit
- Pandas
- Plotly

### Installation
1. Cloner le dépôt:
   ```
   git clone <url-du-dépôt>
   cd sc-esport-stats
   ```

2. Installer les packages requis:
   ```
   pip install -r requirements.txt
   ```

### Lancement de l'Application
Pour lancer l'application Streamlit:
```
streamlit run src/app.py
```

### Configuration
L'application utilise un thème personnalisé défini dans `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0b9394"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
```

## Traitement des Données
- Les données numériques sont converties de manière sécurisée
- Les valeurs manquantes sont remplacées par des valeurs par défaut cohérentes
- Le formatage des dates est standardisé
- Gestion des erreurs pour le traitement des données

## Sources de Données
- Les données des matchs sont stockées au format JSON
- Les icônes des champions sont récupérées depuis l'API Data Dragon de Riot Games

## Contribution
Les contributions sont les bienvenues ! N'hésitez pas à soumettre une Pull Request.

## Problèmes Connus
- La validation des données est strictement appliquée pour éviter les valeurs NaN
- Toutes les colonnes numériques utilisent des méthodes de conversion sécurisées
- Des valeurs par défaut sont fournies pour les données manquantes