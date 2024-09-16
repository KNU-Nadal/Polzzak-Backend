from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate

import config

from .database import db
from . import models

from .users import User_ns
from .reviews import Review_ns

app = Flask(__name__)
app.config.from_object(config)

api = Api(
    app,
    version='0.1',
    title="Nadal's API Server",
    description="Nadal's Polzzak_Backend API Server!",
    contact="yghun021007@knu.ac.kr",
)

api.add_namespace(User_ns)
api.add_namespace(Review_ns)

db.init_app(app)
migrate = Migrate()
migrate.init_app(app,db)