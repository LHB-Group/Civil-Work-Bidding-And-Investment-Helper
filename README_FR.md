<h1 align="center"> Prédiction des prix des appels d'offres pour les travaux de génie civil à San Francisco. AI-Powered.🌉🏗️ 💸</h1>

![python-shield](https://forthebadge.com/images/badges/made-with-python.svg)

* [App](https://costofmyconstructionproject.herokuapp.com/)
> En cas de 404, cliquez sur [vidéo enregistrée](https://drive.google.com/file/d/13Y7McHQZtmEVhrX_G1Ukog_OVayNIo4P/view?usp=sharing)

## Table of contents
* [Background](#background)
* [Projet](#projet)
* [Documents clés](#documents-clés)
* [Répertoires supérieurs](#répertoires-supérieurs)
* [Technologies](#technologies)
* [Base de données](#base-de-données)
* [Configuration](#configuration)
* [License](#license)
* [Auteurs](#auteurs)
* [Contact](#contact)

## Background

San Francisco est une ville hyper-populaire avec une communauté de sans-abri (20% de la population), des risques de catastrophes naturelles et des prix de logement astronomiques. Il n'y a pas suffisamment de logements abordables pour tout le monde à San Francisco. Les projets de construction de logements abordables sont très demandés. De nombreux investisseurs envisagent d'investir dans des projets de construction à San Francisco, qui peuvent offrir un rendement élevé. Pour les projets de construction, les ingénieurs s'efforcent de prévoir le coût du projet de construction le plus raisonnable possible pour gagner les appels d'offres. 🏗️ 💸

## Projet

Ce projet est une application alimentée par l'IA 🧠🤖 pour estimer le coût des projets de construction à San Francisco. 

* [Presentation du projet](https://docs.google.com/presentation/d/1uWvuKxi8LZJN_XV6F3pEtfRy1y2JgECC/edit?usp=sharing&ouid=117915938711430623839&rtpof=true&sd=true)

Parmi les efforts déployés, citons le nettoyage des données, la collecte de données supplémentaires sur les caractéristiques, la mise en place de modèles d'apprentissage automatique, le calcul de l'erreur prédictive, le réglage des paramètres, la création d'une page Web et le déploiement d'une application en ligne. 

Les modèles d'apprentissage automatique ont été entraînés avec les données historiques provenant des permis de construire de San Francisco disponibles depuis le début des années 1980 (merci à datasf.org).

Un ensemble de paramètres et de modèles d'apprentissage automatique ont été testés (dont le modèle linéaire, le modèle Lasso, E-Net, KRidge, GBoosting, XGBoost, LGBoost et Random Forest). **Le modèle Random Forest**🌲🌳🌲🌲🌳 a enfin été retenu comme modèle final.

> Coût du gros œuvre 

> ✅ comprend le coût des fondations, des colonnes, des poutres, des dalles, des planchers, du toit et le coût de la main-d'œuvre.

> ❌ ne comprend pas le prix du terrain, les travaux de finition, l'électricité et la plomberie et les coûts commerciaux.

## Documents clés
	
1 - Notebook sur [l'analyse exploratoire des données](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/Master/NoteBooks/Exploratory_Data_Analysis.ipynb)

2 - Script sur [le nettoyage des données](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/Master/src/building_permits.py) 

3 - Notebook sur [les modèles prédictifs d'apprentissage automatique](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/Master/NoteBooks/predictive_models.ipynb)

4 - Scores de [modèles et d'expériences d'apprentissage automatique](https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper/blob/Master/Tracking/exp_logs.csv)

### Répertoires supérieurs

    .
    ├── Docker                  # Déploiement de l'application. Scripts avec streamlit, modèles ML finaux et paramètres du conteneur Docker.
    ├── NoteBooks               # Jupyter notebooks sur EDA, feature engineering and ML models
    ├── ShapeOut                # Documents sur les empreintes des bâtiments à SF
    ├── Tracking                # Scores de modèles et d'expériences d'apprentissage automatique
    ├── src                     # Scripts sur functions, database cleaning, building ground surface area and ML model experiments 
    ├── LICENSE
    ├── README.md 
	 ├── README_FR.md
    └── requirements.txt

## Technologies
Le projet est créé avec :
* Python 3.8
* Jupyter Notebook 6.4.12
* Python libraries (see /requirements.txt)
* Streamlit 1.12.0
* Docker 20.10.18
* VSCode 1.71.2

## Base de données
1 - [Permis de construire à San Francisco](https://data.sfgov.org/Housing-and-Buildings/Building-Permits/i98e-djp9/data)

> Un permis de construire est un document d'approbation officiel délivré par un organisme gouvernemental qui vous permet, à vous ou à votre entrepreneur, de réaliser un projet de construction ou de rénovation sur votre propriété. Pour plus de détails, consultez le [site](https://www.thespruce.com/what-is-a-building-permit-1398344). Chaque ville ou comté dispose de son propre bureau chargé des bâtiments, qui peut remplir de multiples fonctions telles que la délivrance de permis, l'inspection des bâtiments pour faire respecter les mesures de sécurité, la modification des règles pour répondre aux besoins d'une population croissante, etc. Pour la ville de San Francisco, la délivrance des permis est assurée par [SF DBI](www.sfdbi.org/).

2 - [Building Footprints in San Francisco](https://data.sfgov.org/Housing-and-Buildings/Building-Footprints-File-Geodatabase-Format-/asx6-3trm)

## Configuration

Pour exécuter ce projet, 
1. Clonez le repo :
   ```sh
   git clone https://github.com/LHB-Group/Civil-Work-Bidding-And-Investment-Helper.git
   ```
2. Installez les [paquets](#technologies)

3. Installez les libraries de python
   ```sh
   pip3 install -r requirements.txt
   ```
## License

Distribué sous la licence MIT. Voir LICENSE.txt pour plus d'informations.

## Auteurs

[croustibats](https://github.com/croustibats) ,
[hicham-mrani](https://github.com/hicham-mrani) and 	
[levist7](https://github.com/levist7)

## Contact

Veuillez consulter les coordonnées sur le dossier de présentation [ci-dessus](#projet).

---
Réalisé avec ❤️ à Paris
----
