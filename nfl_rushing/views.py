import csv
import os

from flask import Blueprint, render_template, request, send_file

from nfl_rushing.columns import columns, get_order_by
from nfl_rushing.models import Player

bp = Blueprint('bp', __name__)


@bp.route('/')
def index():
    sort = __get_sort_query_param()
    page = __get_page_query_param()
    name = __get_name_query_param()
    players = __get_base_query(name, sort).paginate(page, 15)

    return render_template('index.html', columns=columns.values(), players=players, name=name, sort=sort, page=page)


@bp.route('/download')
def download():
    sort = __get_sort_query_param()
    name = __get_name_query_param()

    filepath, base_file_path = __get_file_paths(sort, name)

    if not os.path.exists(base_file_path):
        players = __get_base_query(name, sort).all()
        with open(base_file_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow([c.display for c in columns.values()])
            writer.writerows([player.table_data() for player in players])
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
