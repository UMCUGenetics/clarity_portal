"""Clarity Portal wsgi."""
# Add app to the path
import sys
sys.path.insert(0, "/data/clarityportal/clarity_portal")

# Load app
from portal import app as application
from portal.utils import WSGIMiddleware

# Setup prefix
application.wsgi_app = WSGIMiddleware(application.wsgi_app, "")
