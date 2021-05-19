from flask import Markup

from nfl_rushing.models import Player


class Column:
    def __init__(self, display, sort_value, tooltip, column, asc=False):
        self.display = display
        self.sort_value = sort_value
        self.tooltip = tooltip
        self.column = column
        self.asc = asc

    def get_display(self, current_sort):
        current_sort, is_ascending = parse_current_sort(current_sort)

        if self.sort_value != current_sort:
            return self.display

        if is_ascending:
            return self.display + Markup('&#9652;')
        else:
            return self.display + Markup('&#9662;')

    def get_sort(self, current_sort):
        current_sort, is_ascending = parse_current_sort(current_sort)

        if self.sort_value != current_sort:
            return self.sort_value

        if is_ascending:
            return self.sort_value
        else:
            return f'{self.sort_value}-'

    def get_order_by(self, is_ascending):
        if is_ascending and self.asc or not is_ascending and not self.asc:
            return self.column.desc()
        else:
            return self.column.asc()


columns = {
    column.sort_value: column for column in [
        Column('Player', 'ply', 'Player\'s name', Player.name, asc=True),
        Column('Team', 'tm', 'Player\'s team abbreviation', Player.team, asc=True),
        Column('Pos', 'pos', 'Player\'s Position', Player.position, asc=True),
        Column('Att', 'att', 'Rushing Attempts', Player.attempts),
        Column('Att/G', 'apg', 'Rushing Attempts Per Game Average', Player.attempts_per_game),
        Column('Yds', 'yds', 'Total Rushing Yards', Player.yards),
        Column('Avg', 'avg', 'Average Rushing Yards Per Attempt', Player.yards_per_carry),
        Column('Yds/G', 'ypg', 'Rushing Yards Per Game', Player.yards_per_game),
        Column('TD', 'td', 'Total Rushing Touchdowns', Player.touchdowns),
        Column('Lng', 'lng', 'Longest Rush (T indicates Touchdown)', Player.longest_run),
        Column('1st', 'fd', 'Rushing First Downs', Player.first_downs),
        Column('1st%', 'fdp', 'Rushing First Down Percentage', Player.first_down_percentage),
        Column('20+', 'otw', 'Rushing 20+ Yards Each', Player.over_twenty),
        Column('40+', 'ofo', 'Rushing 40+ Yards Each', Player.over_forty),
        Column('FUM', 'fum', 'Rushing Fumbles', Player.fumbles)
    ]
}


def get_order_by(sort_value):
    if not sort_value:
        return Player.yards.desc()

    current_sort, is_ascending = parse_current_sort(sort_value)
    return columns[current_sort].get_order_by(is_ascending)


def parse_current_sort(current_sort):
    current_sort = current_sort or 'yds'
    is_ascending = '-' in current_sort
    return current_sort.replace('-', ''), is_ascending
