<div align="center">
  <h1>Tohfa ✨</h1>
  <p><strong>AI-Powered Luxury Fabric Recommendation Platform</strong></p>

  <!-- Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Version-v1.0-58a6ff?style=flat-square" />
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
    <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square" />
    <img src="https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white" />
    <img src="https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=flat-square&logo=scikitlearn&logoColor=white" />
    <img src="https://img.shields.io/badge/MySQL-Supported-4479A1?style=flat-square&logo=mysql&logoColor=white" />
    <img src="https://img.shields.io/badge/Railway-Deployed-0B0D0E?style=flat-square&logo=railway&logoColor=white" />
  </p>

  <p>
    <em>Hybrid Recommendation Engine combining Content-Based Filtering, Collaborative Signals & Color Intelligence</em>
  </p>

  <p>
    <b>Catalog :</b> 30 luxury fabrics &nbsp;•&nbsp; <b>Engine :</b> TF-IDF · Cosine Similarity · Popularity · Color Matching &nbsp;•&nbsp; <b>Top-K :</b> 6 recommendations
  </p>
</div>

---

## Table of Contents

1. [Vue d'ensemble](#vue-densemble)
2. [AI Solution](#ai-solution)
3. [Project Architecture](#project-architecture)
4. [Dataset & Features](#dataset--features)
5. [Recommendation Pipeline](#recommendation-pipeline)
6. [Scoring Formula & Weights](#scoring-formula--weights)
7. [Results & Metrics](#results--metrics)
8. [Getting Started](#getting-started)
9. [Limitations & Known Issues](#limitations--known-issues)
10. [Roadmap](#roadmap)
11. [Team & Contact](#team--contact)

---

## Vue d'ensemble

Les boutiques de luxe artisanal souffrent d'un problème de découvrabilité : face à un catalogue riche, les clients peinent à trouver les tissus qui correspondent à leur style, et les systèmes de recommandation classiques nécessitent des volumes de données considérables pour fonctionner.

**Tohfa** est une plateforme web Flask qui connecte des clients à des designers de mode marocains, dotée d'un moteur de recommandation hybride léger, capable de générer des suggestions personnalisées **dès le premier choix de l'utilisateur** (cold-start partiel), sans infrastructure ML lourde.

---

## AI Solution

**Ce que fait l'IA :** Le système analyse la description textuelle du tissu choisi par le client, extrait sa préférence de couleur dominante, et combine ces signaux avec la popularité collective pour recommander les 6 tissus les plus compatibles du catalogue.

**Pourquoi c'est adapté :** L'approche intègre du **Content-Based Filtering** (TF-IDF + Cosine Similarity), un signal de **Collaborative Filtering implicite** (comptage des sélections), et un **moteur de règles couleur**, sans nécessiter de données historiques massives ni d'infrastructure GPU.

---

## Project Architecture

```
tohfa-main/
├── app.py                    ← Flask routes + AI recommendation engine
├── models.py                 ← SQLAlchemy ORM (User, Fabric, Design, Selection)
├── setup_db.py               ← Database seeding (30 luxury fabrics)
├── requirements.txt
├── Procfile / nixpacks.toml  ← Railway deployment config
├── static/
│   ├── css/style.css
│   └── images/               ← 30 fabric JPEG images
└── templates/
    ├── base.html
    ├── login.html / register.html
    ├── client/
    │   ├── fabrics.html       ← Browse catalog
    │   ├── designs.html       ← Browse designs
    │   ├── my_selection.html  ← Current selection
    │   └── recommend.html     ← AI recommendation results ✨
    └── designer/
        ├── dashboard.html
        └── upload.html
```

---

## Dataset & Features

Le catalogue en entrée est seedé depuis `setup_db.py` et contient **30 tissus de luxe**, chacun décrit par les features suivantes :

| Feature | Description | Exemple |
|---|---|---|
| `name` | Nom poétique du tissu (contient la couleur dominante) | `"Atlas Azur"` |
| `description` | Phrase descriptive en français (signal textuel principal) | `"Le bleu profond des cieux de l'Atlas, texture soyeuse."` |
| `image_url` | Chemin vers l'image JPEG associée | `/static/images/Atlas Azur.jpeg` |
| `availability` | Disponibilité en stock (booléen) | `True` |
| `fabric_id` | Clé primaire utilisée pour le scoring | `2` |

La table `user_selections` (1 ligne par client) constitue la **matrice de feedback implicite** utilisée par le signal collaboratif :

| Feature | Description |
|---|---|
| `client_id` | Référence client |
| `fabric_id` | Tissu actuellement choisi (nullable) |
| `design_id` | Design actuellement choisi (nullable) |
| `updated_at` | Horodatage de la dernière mise à jour |

---

## Recommendation Pipeline

### Vue d'ensemble du pipeline

```
Client sélectionne un tissu
          │
          ▼
┌─────────────────────────────────────────────────┐
│              Hybrid Scoring Pipeline            │
│                                                 │
│  ① Content Signal    TF-IDF Cosine Similarity  │  × 0.60
│  ② Collab Signal     Popularity Count          │  × 0.25
│  ③ Rule Signal       Color Keyword Match       │  × 0.15
│                                                 │
│   score = 0.6·tfidf + 0.25·popular + 0.15·color│
└─────────────────────────────────────────────────┘
          │
          ▼
   Top-6 recommendations
   rendues dans recommend.html
   avec barre de compatibilité (%)
```

---

### Étape 1 — Content-Based Filtering · TF-IDF + Cosine Similarity (poids : 0.60)

**Localisation :** `compute_tfidf_similarities()` dans `app.py`

```python
def compute_tfidf_similarities(reference_fabric, all_fabrics):
    corpus, fabric_ids = [], []
    for f in all_fabrics:
        if f.description:
            corpus.append(f.description)
            fabric_ids.append(f.fabric_id)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(corpus)      # fit sur tout le corpus
    ref_vector   = vectorizer.transform([reference_fabric.description])  # transform seul
    similarities = cosine_similarity(ref_vector, tfidf_matrix).flatten()
    return dict(zip(fabric_ids, similarities))
```

**Fonctionnement :**

1. **Construction du corpus** — Les descriptions de tous les tissus disponibles sont collectées (ex : `"Un gris industriel noble avec un reflet métallique."`).
2. **Vectorisation TF-IDF avec bigrammes** — `TfidfVectorizer(ngram_range=(1,2))` encode chaque description en vecteur sparse. Les bigrammes permettent de traiter des syntagmes comme *"reflets dorés"* ou *"texture soyeuse"* comme une seule feature.
3. **Vecteur de référence** — Le tissu choisi est transformé via `.transform()` (et non `.fit_transform()`) pour rester dans l'espace vectoriel du corpus global.
4. **Similarité cosinus** — Produit scalaire normalisé entre le vecteur de référence et chaque vecteur du catalogue. Retourne un score ∈ [0, 1] par tissu.

---

### Étape 2 — Collaborative Filtering implicite · Popularité (poids : 0.25)

```python
popular_counts = db.session.query(
    Selection.fabric_id,
    func.count(Selection.fabric_id).label('total')
).group_by(Selection.fabric_id).all()

popular_ids = [item.fabric_id for item in popular_counts]
```

Tout tissu ayant été sélectionné par au moins un autre client reçoit un bonus de **+0.25**. Il s'agit de la forme la plus simple de collaborative filtering implicite — la popularité agrégée sert de prior global pour guider les nouveaux utilisateurs.

---

### Étape 3 — Préférence Couleur · Moteur de règles (poids : 0.15)

```python
colors = ["Azur", "Bleu", "Or", "Doré", "Rosé", "Gris",
          "Noir", "Vert", "Rouge", "Argent"]
for c in colors:
    if c.lower() in chosen_fabric.name.lower():
        fav_color = c.lower()
        break
```

Un matching par mot-clé extrait la couleur dominante depuis le **nom** du tissu choisi. Les tissus dont le nom contient la même couleur reçoivent un bonus de **+0.15**, encodant l'hypothèse qu'un client choisissant *"Atlas Azur"* a une affinité pour les tons bleus.

---

## Scoring Formula & Weights

```python
score = (0.6  * tfidf_scores.get(fabric.fabric_id, 0)
       + (0.25 if fabric.fabric_id in popular_ids else 0)
       + (0.15 if fav_color and fav_color in fabric.name.lower() else 0))
```

| Signal | Poids | Type | Méthode |
|---|---|---|---|
| Similarité textuelle | **0.60** | Content-Based | TF-IDF Cosine Similarity |
| Popularité collective | **0.25** | Collaborative (implicite) | Comptage sélections |
| Correspondance couleur | **0.15** | Rule-Based | Keyword matching |
| **Total** | **1.00** | **Hybride** | |

> ⚠️ *Les poids sont définis manuellement (heuristique). Un système en production apprendrait ces poids via régression logistique ou LightGBM entraîné sur les logs de clics.*

Le score final est converti en **pourcentage de compatibilité** affiché dans l'interface (`score × 100`), et les 6 tissus avec le score le plus élevé sont retournés (le tissu déjà sélectionné est exclu).

---

## Results & Metrics

| Indicateur | Valeur |
|:---|:---|
| **Taille du catalogue** | 30 tissus de luxe |
| **Fournisseurs de signal** | 3 (TF-IDF, popularité, couleur) |
| **Top-K retourné** | 6 recommandations |
| **Couverture couleur** | 10 couleurs indexées |
| **Cold-start** | ✅ Partiel (dès 1 sélection) |
| **Latence estimée** | < 200 ms (vectorisation en mémoire) |
| **Dépendances ML** | scikit-learn uniquement (pas de GPU) |

> ℹ️ *Note : Le modèle performe bien sur le signal textuel pour des descriptions distinctes. Des descriptions trop courtes ou génériques réduisent la discriminance du TF-IDF. L'ajout de données historiques de sélection améliorera significativement le signal collaboratif.*

---

## Getting Started

### Prérequis
- Python 3.10+
- MySQL (local ou Railway)

### Installation locale

```bash
git clone <repo-url>
cd tohfa-main

pip install -r requirements.txt
```

### Configuration

```bash
# Créer un fichier .env
FLASK_SECRET_KEY=your_secret_key
DATABASE_URL=mysql+pymysql://user:password@localhost/tohfa_db
```

### Lancement

```bash
python app.py
# La base est auto-créée et seedée (30 tissus) au premier démarrage
```

### Déploiement Railway (Cloud)

```bash
# Les fichiers Procfile et nixpacks.toml sont préconfigurés
# Il suffit de connecter le repo à Railway et de définir les variables d'env
```

---

## Limitations & Known Issues

| Limitation | Impact | Solution Envisagée |
|---|---|---|
| Poids heuristiques `[0.60, 0.25, 0.15]` | Non-optimaux sans données réelles | Apprendre les poids via LightGBM sur logs de clics |
| TF-IDF lexical (pas sémantique) | *"argenté"* ≠ *"gris métallique"* | Remplacer par `paraphrase-multilingual-MiniLM` |
| Signal popularité binaire | Tous les tissus populaires = même bonus | Normaliser : `count / max_count` |
| Couleur extraite sur le nom uniquement | "Saphire Céleste" → aucune couleur détectée | NER ou table de synonymes couleur |
| 1 sélection max par client | Profil utilisateur très limité | Permettre un historique de sélections multiples |

---

## Roadmap

- [x] Moteur hybride TF-IDF + popularité + couleur
- [x] Affichage de la barre de compatibilité (%) dans l'UI
- [x] Déploiement Railway avec MySQL
- [ ] Remplacer TF-IDF par un sentence-transformer multilingue (`sentence-transformers`)
- [ ] Ajouter SMOTE ou pondération pour rééquilibrer si dataset biaisé
- [ ] Apprendre les poids du scoring via régression logistique sur feedback implicite
- [ ] Logging des clics & sélections pour constituer un jeu de données d'évaluation
- [ ] Métriques offline : Precision@K, NDCG@K sur un test set de sélections
- [ ] Export des recommandations en PDF pour les clients

---

## Team & Contact

**AI Engineering Students** — Projet académique de recommandation IA

Pour toute question académique ou technique, ouvrez une Issue sur le dépôt GitHub.

---

<div align="center">
  <sub>Built with ❤️ for AI-Powered Fashion Intelligence — Distributed under the MIT License.</sub>
</div>
