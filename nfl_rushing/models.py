import json

from flask import Flask

from nfl_rushing.database import db


class Player(db.Model):
    __tablename__ = 'players'

    name = db.Column(db.Text, primary_key=True)
    team = db.Column(db.Text)
    position = db.Column(db.Text)
    attempts = db.Column(db.Integer)
    attempts_per_game = db.Column(db.Float)
    yards = db.Column(db.Integer)
    yards_per_carry = db.Column(db.Float)
    yards_per_game = db.Column(db.Float)
    touchdowns = db.Column(db.Integer)
    longest_run = db.Column(db.Integer)
    long_is_touchdown = db.Column(db.Boolean)
    first_downs = db.Column(db.Integer)
    first_down_percentage = db.Column(db.Float)
    over_twenty = db.Column(db.Integer)
    over_forty = db.Column(db.Integer)
    fumbles = db.Column(db.Integer)

    @staticmethod
    def get_column_for_sort(sort_value):
        if sort_value == 'yds':
            return Player.yards
        elif sort_value == 'td':
            return Player.touchdowns
        elif sort_value == 'lng':
            return Player.longest_run
        else:
            return Player.yards


def __load_data():
    with open('rushing.json', 'r') as f:
        rushing_data = json.load(f)

    for data in rushing_data:
        longest_run = str(data['Lng'])
        long_is_touchdown = 'T' in longest_run
        longest_run = int(longest_run.replace('T', ''))

        player = Player(
            name=data['Player'],
            team=data['Team'],
            position=data['Pos'],
            attempts=data['Att'],
            attempts_per_game=data['Att/G'],
            yards=data['Yds'],
            yards_per_carry=data['Avg'],
            yards_per_game=data['Yds/G'],
            touchdowns=data['TD'],
            longest_run=longest_run,
            long_is_touchdown=long_is_touchdown,
            first_downs=data['1st'],
            first_down_percentage=data['1st%'],
            over_twenty=data['20+'],
            over_forty=data['40+'],
            fumbles=data['FUM']
        )
        db.session.add(player)
    db.session.commit()


if __name__ == '__main__':
    print('Creating database tables')
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rushing.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.app_context().push()

    db.create_all()

    print('Loading data into database')
    __load_data()
    print('Done!')
