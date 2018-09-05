from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from genologics.lims import Lims

app = Flask(__name__)
app.config.from_object('config')
lims = Lims(app.config['BASEURI'], app.config['USERNAME'], app.config['PASSWORD'])
bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)

from . import views
