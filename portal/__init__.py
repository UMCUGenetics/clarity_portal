from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')

from . import views

bootstrap = Bootstrap(app)
