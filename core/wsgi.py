import os

from django.core.wsgi import get_wsgi_application

# Utilise DJANGO_SETTINGS_MODULE si défini, sinon development par défaut
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

application = get_wsgi_application()
