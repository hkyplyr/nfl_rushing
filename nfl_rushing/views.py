import csv
from flask import render_template, request, send_file, url_for
from nfl_rushing.app import app
from nfl_rushing.models import Player


@app.route('/')
def index():
    sort = __get_sort_query_param()
    page = __get_page_query_param()
    name = __get_name_query_param()

    players = __get_base_query(name, sort).paginate(page, 15)

    sort_td_url = url_for('app.index', page=page, sort='td', name=name)
    sort_yds_url = url_for('app.index', page=page, sort='yds', name=name)
    sort_lng_url = url_for('app.index', page=page, sort='lng', name=name)
    download_url = url_for('app.download', sort=sort, name=name)
    next_url = url_for('app.index', page=players.next_num, sort=sort) if players.has_next else None
    prev_url = url_for('app.index', page=players.prev_num, sort=sort) if players.has_prev else None
    return render_template('index.html', players=players.items, prev_url=prev_url, next_url=next_url, sort_td_url=sort_td_url,
                           sort_yds_url=sort_yds_url, sort_lng_url=sort_lng_url, download_url=download_url)


@app.route('/download')
def download():
    sort = __get_sort_query_param()
    name = __get_name_query_param()

    players = __get_base_query(name, sort).all()

    filename = 'data.csv'
    with open(f'nfl_rushing/{filename}', 'w') as f:
        writer = csv.writer(f)
        headers = Player.__table__.columns.keys()
        writer.writerow(headers)
        for player in players:
            writer.writerow([getattr(player, c) for c in headers])

    return send_file(filename, attachment_filename=filename, as_attachment=True, cache_timeout=-1)


def __get_sort_query_param():
    return request.args.get('sort', default=None, type=str)


def __get_name_query_param():
    return request.args.get('name', default=None, type=str)


def __get_page_query_param():
    return request.args.get('page', default=1, type=int)


def __get_base_query(name, sort):
    if name:
        return Player.query \
                     .filter(Player.name.contains(name)) \
                     .order_by(Player.get_column_for_sort(sort).desc())
    else:
        return Player.query.order_by(Player.get_column_for_sort(sort).desc())
