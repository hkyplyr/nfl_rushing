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

    def to_table_data(self):
        return [
            self.name,
            self.team,
            self.position,
            self.attempts,
            self.attempts_per_game,
            self.yards,
            self.yards_per_carry,
            self.yards_per_game,
            self.touchdowns,
            self.longest_run if not self.long_is_touchdown else f'{self.longest_run}T',
            self.first_downs,
            self.first_down_percentage,
            self.over_twenty,
            self.over_forty,
            self.fumbles
        ]

    @staticmethod
    def to_database_model(json):
        longest_run = str(json['Lng'])
        long_is_touchdown = 'T' in longest_run
        longest_run = int(longest_run.replace('T', ''))

        return Player(
            name=json['Player'],
            team=json['Team'],
            position=json['Pos'],
            attempts=json['Att'],
            attempts_per_game=json['Att/G'],
            yards=json['Yds'],
            yards_per_carry=json['Avg'],
            yards_per_game=json['Yds/G'],
            touchdowns=json['TD'],
            longest_run=longest_run,
            long_is_touchdown=long_is_touchdown,
            first_downs=json['1st'],
            first_down_percentage=json['1st%'],
            over_twenty=json['20+'],
            over_forty=json['40+'],
            fumbles=json['FUM'])
