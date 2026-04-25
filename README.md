# NEXTGEN - DevConnect

Plateforme sociale de mise en réseau (type LinkedIn light) construite avec Django.

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.10+
- MySQL (ou MariaDB)
- pip (gestionnaire de paquets Python)

### Installation

1. **Cloner le projet**
   ```bash
   git clone <url-du-repo>
   cd devconnect
   ```

2. **Créer l'environnement virtuel**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer la base de données**
   - Créer une base MySQL : `devconnect`
   - Créer un fichier `.env` à partir de `.env.example` :
     ```bash
     cp .env.example .env
     ```
   - Adapter les valeurs dans `.env`

5. **Lancer les migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

7. **Lancer le serveur**
   ```bash
   python manage.py runserver
   ```

8. **Accéder à l'application**
   - Site : http://127.0.0.1:8000
   - Admin : http://127.0.0.1:8000/admin/


## 📂 Structure du Projet

```
devconnect/
├── core/                 # Configuration Django
│   ├── settings/        # Settings (base, dev, prod)
│   ├── urls.py          # Routes principales
│   └── ...
├── apps/
│   ├── users/           # Utilisateurs et profils
│   ├── posts/           # Publications et stories
│   ├── interactions/    # Likes, commentaires, partages
│   └── notifications/   # Système de notifications
├── templates/           # Templates HTML
└── static/              # Fichiers statiques
```

## 🔐 Sécurité

### Points d'attention
- La clé secrète Django (`SECRET_KEY`) doit être longue et aléatoire en production
- Ne jamais commit le fichier `.env`
- Utiliser HTTPS en production
- Valider les uploads de fichiers (taille, type)
- Les mots de passe sont hashés avec PBKDF2

### Configuration de production
Voir `core/settings/production.py` pour les réglages sécurité :
- HSTS activé
- Cookies sécurisés (Secure, HttpOnly)
- CORS restreint

## 🧪 Tests

```bash
python manage.py test apps.users
python manage.py test apps.posts
python manage.py test apps.interactions
```

## 🎨 Fonctionnalités

- **Profils utilisateurs** : Bio, compétences, avatar
- **Fil d'actualité** : Publications, images, code snippets
- **Stories** : Contenu éphémère (24h)
- **Interactions** : Likes, commentaires, partages, reposts
- **Réseau** : Système d'abonnements avec demandes
- **Messagerie** : Messages directs entre utilisateurs
- **Notifications** : Alertes en temps réel
- **Recherche** : Utilisateurs et contenu

## 📄 Licence

Projet académique - NEXTGEN 2026
