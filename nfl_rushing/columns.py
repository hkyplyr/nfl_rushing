from flask import Markup

from nfl_rushing.models import Player


class Column:
    """ Object representation of a table column.

    Attribute
    ---------
    display: str
        The proper display name of the table column (ex. Player)
    sort_value: str
        The default sort_value for a table column (ex. yds)
    tooltip: str
        The longform tooltip description of a table column (ex. Total Rushing Touchdowns)
    column: db.Column
        A reference to the database column object; helpful for sorting
    asc: bool
        Indicates the default sort order for a column; True for ascending False for descending
    """
    def __init__(self, display, sort_value, tooltip, column, asc=False):
        self.display = display
        self.sort_value = sort_value
        self.tooltip = tooltip
        self.column = column
        self.asc = asc

    def get_display(self, current_sort):
        """Return the display name with the appropriate symbols.

        If the current column is not being used as the current sorting
        value, the app simply returns the normal display name. However,
        if the current column is being used for sorting the app should
        display an arrow indicating it is in use and the direction of the
        arrow indicates if the current sorting is ascending or descending.
        """
        current_sort, is_ascending = parse_current_sort(current_sort)

        if self.sort_value != current_sort:
            return self.display

        if is_ascending:
            return self.display + Markup('&#9652;')
        else:
            return self.display + Markup('&#9662;')

    def get_sort(self, current_sort):
        """Return the sort value with the appropriate asc/desc indicator.

        If the current column is not currently being used for sorting, the
        app needs to set the sorting parameter to the normal (non-ascending)
        sorting indicator. However, if the current column is being used for
        sorting, the opposite state of the current sorting should be returned
        in order for the app to create a link to flip the sorting rank.

        For example, if we are currently sorting yards in descending order,
        this method would return `yds-` so that the app can render a link to
        query for yards in ascending order, and vice versa.
        """
        current_sort, is_ascending = parse_current_sort(current_sort)

        if self.sort_value != current_sort:
            return self.sort_value

        if is_ascending:
            return self.sort_value
        else:
            return f'{self.sort_value}-'

    def get_order_by(self, is_ascending):
        """Return the order by clause for a SQL query.

        When building the SQL query the app needs to add an order by clause
        based on the current sorting parameter. Basically if the sorting
        parameter contains a dash its usually in ascending order, and if not
        its usually in descending order.

        One difference is when the current column is ascending by default so
        the sorting parameter logic must be inverted. If the sorting parameter
        is expecting ascending order and the default sort order for the column
        is descending, this method actual returns the column in descending order.

        """
        if is_ascending and self.asc or not is_ascending and not self.asc:
            return self.column.desc()
        else:
            return self.column.asc()


# This is a dictionary containing all of the supported columns for the data to
# be displayed in the application. The keys are the various sort values (ex. yds)
# for each column and the values are the instantiated column objects containing
# the display name, sort value, tooltip description, database_column, and default
# rank (is ascending or not).
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
    """Return the order by clause for a SQL query.

    This method is responsible for handling the case where no sorting parameter
    is provided and it should fall back to the default sort order. It is also
    responsible for retrieving the column to be sorted and calling get_order_by
    on that column and returning the result.
    """
    if not sort_value:
        return Player.yards.desc()

    current_sort, is_ascending = parse_current_sort(sort_value)
    return columns[current_sort].get_order_by(is_ascending)


def parse_current_sort(current_sort):
    """Helper method for parsing the sorting parameter string.

    Parses the incoming sorting parameter and returns the raw sort value to
    simplify lookups and transformations, and whether or not the sort parameter
    expects the data to be in ascending order.
    """
    current_sort = current_sort or 'yds'
    is_ascending = '-' in current_sort
    return current_sort.replace('-', ''), is_ascending
