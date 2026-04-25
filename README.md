# TOHFA v2 — Plateforme Tissu & Design

## Architecture

```
tohfa_v2/
├── app.py              # Routes Flask (client + designer)
├── models.py           # Modèles DB (User, Fabric, Design, Selection)
├── setup_db.py         # Init DB + seed des tissus
├── requirements.txt
├── .env
├── static/
│   ├── css/style.css   # CSS dark/light mode
│   ├── images/         # Photos des tissus
│   └── uploads/
│       └── designs/    # Uploads des designers (créé auto)
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── client/
    │   ├── fabrics.html
    │   ├── designs.html
    │   ├── my_selection.html
    │   └── recommend.html
    └── designer/
        ├── dashboard.html
        └── upload.html
```

## Installation

```bash
# 1. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Créer la base MySQL
mysql -u root -e "CREATE DATABASE tohfa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. Configurer .env si besoin
# DATABASE_URL=mysql+pymysql://root:motdepasse@localhost/tohfa_db

# 5. Initialiser la DB et les tissus
python setup_db.py

# 6. Lancer l'app
python app.py
```

## Rôles utilisateurs

### Client
- Crée un compte avec rôle "Client"
- Parcourt la collection de tissus → sélectionne son tissu préféré
- Parcourt les designs publiés par les designers → sélectionne un design
- Obtient des recommandations IA basées sur son choix de tissu
- Visualise sa sélection complète tissu + design
- Contact TOHFA pour finaliser la commande

### Designer
- Crée un compte avec rôle "Designer" + définit sa marge (%)
- Publie des designs (photo + nom + description + prix)
- Suit sur son dashboard : nombre de sélections par design, gains estimés
- Peut activer/désactiver/supprimer ses designs

## Système de marges (tracking)

Quand un client sélectionne un design, la commission du designer est :
```
commission = design.price × designer.margin_pct
```

Visible dans le dashboard designer en temps réel.

## Fonctionnalités

- ✅ Dark / Light mode (toggle navbar, persisté en localStorage)
- ✅ Auth par rôle (client / designer), redirections automatiques
- ✅ Upload d'images pour les designers (drag & drop)
- ✅ Dashboard designer avec stats et gestion des designs
- ✅ Recommandations IA TF-IDF sur les tissus
- ✅ Aperçu "Ma Sélection" pour les clients
- ✅ CSRF protection sur tous les formulaires
- ✅ Responsive mobile
