from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate

from config import Config

from .database import db
from . import models

from .image import Image_ns
from .users import User_ns
from .reviews import Review_ns
from .teams import Team_ns
from .places  import Place_ns
from .events import Event_ns

app = Flask(__name__)
app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 최대 100MB로 설정
api = Api(
    app,
    version='0.1',
    title="Nadal's API Server",
    description="Nadal's Polzzak_Backend API Server!",
    contact="yghun021007@knu.ac.kr",
)

api.add_namespace(User_ns)
api.add_namespace(Review_ns)
api.add_namespace(Team_ns)
api.add_namespace(Place_ns)
api.add_namespace(Event_ns)
api.add_namespace(Image_ns)

db.init_app(app)
migrate = Migrate()
migrate.init_app(app,db)
