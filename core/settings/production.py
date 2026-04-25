from .base import *  # noqa: F403

DEBUG = False

# Autoriser tous les domaines Railway
ALLOWED_HOSTS = [
    ".railway.app",
    "localhost",
    "127.0.0.1",
]

# Si Railway fournit son URL dans l'environnement
RAILWAY_URL = os.environ.get("RAILWAY_STATIC_URL")
if RAILWAY_URL:
    ALLOWED_HOSTS.append(RAILWAY_URL.replace("https://", "").replace("http://", "").split("/")[0])

# Sécurité HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Très important pour éviter l'erreur 500 sur les fichiers statiques
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Configuration de secours pour WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_MANIFEST_STRICT = False

# Désactiver la sécurité stricte des Referrer pour Railway
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

import dj_database_url
import os

# Railway fournit souvent une DATABASE_URL ou MYSQL_URL
# On essaye de l'utiliser en priorité via dj_database_url
db_from_env = dj_database_url.config(conn_max_age=60, conn_health_checks=True)

if db_from_env:
    DATABASES = {"default": db_from_env}
else:
    # Fallback manuel si pas d'URL unique
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("MYSQLDATABASE") or os.environ.get("MYSQL_DATABASE") or "railway",
            "USER": os.environ.get("MYSQLUSER") or os.environ.get("MYSQL_USER") or "root",
            "PASSWORD": os.environ.get("MYSQLPASSWORD") or os.environ.get("MYSQL_PASSWORD"),
            "HOST": os.environ.get("MYSQLHOST") or os.environ.get("MYSQL_HOST") or "localhost",
            "PORT": os.environ.get("MYSQLPORT") or os.environ.get("MYSQL_PORT") or "3306",
            "OPTIONS": {
                "charset": "utf8mb4",
            },
            "CONN_MAX_AGE": 60,
        }
    }

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
