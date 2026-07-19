"""
ASGI config for clm_project project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clm_project.settings")
application = get_asgi_application()
