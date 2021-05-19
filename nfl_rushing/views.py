import csv
import os

from flask import Blueprint, render_template, request, send_file

from nfl_rushing.columns import columns, get_order_by
from nfl_rushing.models import Player

bp = Blueprint('bp', __name__)


@bp.route('/')
def index():
    """ Endpoint to render the queried player data in the browser.

    Given the sorting, filtering, and paging query parameters, we retrieve a
    paginated set of data from the database and use the method 'render_template'
    render our html page with the player data in the table.

    See `nfl_rushing/templates/index.html` for the templated html.
    """
    sort = __get_sort_query_param()
    page = __get_page_query_param()
    name = __get_name_query_param()

    players = __get_base_query(name, sort).paginate(page, 15)

    return render_template('index.html', columns=columns.values(), players=players, name=name, sort=sort, page=page)


@bp.route('/download')
def download():
    """Endpoint to download the queried data as a csv file.

    Given the sorting and filtering query parameters, we retrieve all of the
    matching rows from the database and write them to a csv file to be returned
    to the requesting user.

    To avoid taking up extra space with duplicate files and making unnecessary
    database calls, this method checks if a file of the same name already exists
    and skips the part where it needs to query player data and write it to a file.

    This is possible because the data in this application is read only so it never
    changes and the sorting/filtering parameters can be used to indicate what
    data was written to a file in the form 'data-sort-{sort}-name-{name}.csv' where
    the sort or name sections are ommitted if the query parameter was not provided.

    One thing to note is that we have a `filepath` variable and a `base_file_path`
    variable because Flask looks for the files in a different place than they are
    written when using `with open(..)` if they use the same file name. The filepath
    variable is ued by Flask since it looks in the `nfl_rushing` directory by default
    while checking the existence and writing a new file requires the `base_filepath`
    variable which is pre-pended with the `nfl_rusing/` directory.
    """
    sort = __get_sort_query_param()
    name = __get_name_query_param()

    filepath, base_filepath = __get_file_paths(sort, name)

    if not os.path.exists(base_filepath):
        players = __get_base_query(name, sort).all()
        with open(base_filepath, 'w') as f:
            writer = csv.writer(f)
            writer.writerow([c.display for c in columns.values()])
            writer.writerows([player.to_table_data() for player in players])
    return send_file(filepath, as_attachment=True, max_age=-1)


def __get_file_paths(sort, name):
    filepath = 'reports/data'
    if sort:
        filepath += f'-sort-{sort}'
    if name:
        filepath += f'-name-{name}'
    filepath += '.csv'

    base_file_path = f'nfl_rushing/{filepath}'
    os.makedirs(os.path.dirname(base_file_path), exist_ok=True)
    return filepath, base_file_path


def __get_sort_query_param():
    return request.args.get('sort', default=None, type=str)


def __get_name_query_param():
    return request.args.get('name', default=None, type=str)


def __get_page_query_param():
    return request.args.get('page', default=1, type=int)


def __get_base_query(name, sort):
    base_query = Player.query.order_by(get_order_by(sort))
    if name:
        base_query = base_query.filter(Player.name.contains(name))
    return base_query
