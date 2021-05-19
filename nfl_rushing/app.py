import json

from flask import Flask

from nfl_rushing.database import db
from nfl_rushing.views import bp
from nfl_rushing.models import Player


def create_app():
    """ Create the flask application

    This method is responsible for creating the root flask
    app object, configuring the use of an in-memory sqlite
    database, registering the blueprints (routes), and lastly
    initializing and loading the data into the database.

    Since this app uses an in-memory database the schema can
    be created and the data can be loaded on startup without
    issue.
    """
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.register_blueprint(bp)

    __initialize_db(app)
    __load_json_data()
    return app


def __initialize_db(app):
    db.init_app(app)
    app.app_context().push()
    db.create_all()


def __load_json_data():
    with open('rushing.json', 'r') as f:
        rushing_data = json.load(f)
    players = [Player.to_database_model(d) for d in rushing_data]
    db.session.add_all(players)
    db.session.commit()
