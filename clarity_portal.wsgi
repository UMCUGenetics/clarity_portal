"""Clarity Portal wsgi."""
activate_this = '/var/www/html/clarity_portal/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# Add app to the path
import sys
sys.path.insert(0, "/var/www/html/clarity_portal")

# Load app
from clarity_portal import app as application
from clarity_portal.utils import WSGIMiddleware

# Setup prefix
application.wsgi_app = WSGIMiddleware(application.wsgi_app, "/clarity_portal")
