import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config["PASTA_UPLOADS"] = os.path.join(app.root_path, "static", "uploads")

try:
    os.makedirs(app.config["PASTA_UPLOADS"], exist_ok=True)
except OSError:
    pass

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # registra o comando "flask db ..."

from app import models  # noqa: E402,F401
from app import hooks, template_filters  # noqa: E402,F401
from app.routes import BLUEPRINTS  # noqa: E402

for blueprint in BLUEPRINTS:
    app.register_blueprint(blueprint)

