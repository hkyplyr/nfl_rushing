import json

from flask import Flask

from nfl_rushing.database import db
from nfl_rushing.views import bp
from nfl_rushing.models import Player


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.register_blueprint(bp)

    db.init_app(app)
    app.app_context().push()
    db.create_all()
    load_json_data()
    return app


def load_json_data():
    with open('rushing.json', 'r') as f:
        rushing_data = json.load(f)
    players = [Player.init(d) for d in rushing_data]
    db.session.add_all(players)
    db.session.commit()
