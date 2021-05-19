import json
import os
import shutil

from flask import request

from nfl_rushing.app import create_app

flask_app = create_app()


def test_index_sort_param():
    with flask_app.test_request_context('/?sort=yds'):
        assert request.args['sort'] == 'yds'

    with flask_app.test_request_context('/?sort=td'):
        assert request.args['sort'] == 'td'

    with flask_app.test_request_context('/?sort=lng'):
        assert request.args['sort'] == 'lng'


def test_sorted_by_yds():
    page_one_players = ['Ezekiel Elliot', 'Jordan Howard', 'DeMarco Murray', 'Jay Ajayi', 'Le&#39;Veon Bell',
                        'LeSean McCoy', 'David Johnson', 'LeGarrette Blount', 'Devonta Freeman', 'Lamar Miller',
                        'Mark Ingram', 'Frank Gore', 'Melvin Gordon', 'Carlos Hyde', 'Isaiah Crowell']
    page_two_players = ['Spencer Ware', 'Todd Gurley', 'Jeremy Hill', 'Jonathan Stewart', 'Matt Forte',
                        'Latavius Murray', 'Terrance West', 'Bilal Powell', 'Rob Kelley', 'Ryan Mathews',
                        'Devontae Booker', 'Rashad Jennings', 'Tyrod Taylor', 'Mike Gillislee', 'Jacquizz Rodgers']
    with flask_app.test_client() as test_client:
        page_one_default = test_client.get('/?page=1')
        page_two_default = test_client.get('/?page=2')
        page_one_explicit = test_client.get('/?page=1&sort=yds')
        page_two_explicit = test_client.get('/?page=2&sort=yds')
        for player in page_one_players:
            assert player.encode() in page_one_default.data
            assert player.encode() in page_one_explicit.data
            assert player.encode() not in page_two_default.data
            assert player.encode() not in page_two_explicit.data
        for player in page_two_players:
            assert player.encode() in page_two_default.data
            assert player.encode() in page_two_explicit.data
            assert player.encode() not in page_one_default.data
            assert player.encode() not in page_one_explicit.data


def test_sorted_by_yds_asc():
    page_one_players = ['Sam Koch', 'DeMarcus Ayers', 'Eli Manning', 'Taiwan Jones', 'James Wright',
                        'Ryan Mallet', 'Travis Kelce', 'Nick Foles', 'Landry Jones', 'Brandon Burks',
                        'Reggie Bush', 'Jordan Berry', 'Matt McGloin', 'Travis Benjamin', 'Drew Stanton']
    page_two_players = ['Will Fuller', 'Brett Hundley', 'Brandon LaFell', 'Valentino Blake', 'Matt Schaub',
                        'Chad Henne', 'Mark Sanchez', 'Brian Hoyer', 'Jamison Crowder', 'Cardale Jones',
                        'Matt Moore', 'Kellen Clemens', 'Jeremy Maclin', 'Sean Mannion', 'Donte Moncrief']
    with flask_app.test_client() as test_client:
        page_one = test_client.get('/?page=1&sort=yds-')
        page_two = test_client.get('/?page=2&sort=yds-')
        for player in page_one_players:
            assert player.encode() in page_one.data
            assert player.encode() not in page_two.data
        for player in page_two_players:
            assert player.encode() in page_two.data
            assert player.encode() not in page_one.data


def test_sorted_by_tds():
    page_one_players = ['LeGarrette Blount', 'David Johnson', 'Ezekiel Elliot', 'LeSean McCoy', 'Latavius Murray',
                        'Devonta Freeman', 'Melvin Gordon', 'Jeremy Hill', 'Jonathan Stewart', 'DeMarco Murray',
                        'Jay Ajayi', 'Tevin Coleman', 'Ryan Mathews', 'Mike Gillislee', 'Robert Turbin']
    page_two_players = ['Matt Forte', 'Le&#39;Veon Bell', 'Isaiah Crowell', 'Mark Ingram', 'Tyrod Taylor',
                        'Matt Asiata', 'Todd Gurley', 'Dak Prescott', 'Rob Kelley', 'Carlos Hyde',
                        'Jordan Howard', 'Alex Smith', 'Terrance West', 'Cam Newton', 'Derrick Henry']
    with flask_app.test_client() as test_client:
        page_one = test_client.get('/?page=1&sort=td')
        page_two = test_client.get('/?page=2&sort=td')
        for player in page_one_players:
            assert player.encode() in page_one.data
            assert player.encode() not in page_two.data
        for player in page_two_players:
            assert player.encode() in page_two.data
            assert player.encode() not in page_one.data


def test_sorted_by_lng():
    page_one_players = ['Isaiah Crowell', 'Mark Ingram', 'LeSean McCoy', 'Devonta Freeman', 'Tyler Locket',
                        'Jalen Richard', 'DeMarco Murray', 'Jeremy Hill', 'C.J. Prosise', 'Tyreek Hill',
                        'Jordan Howard', 'Rob Kelley', 'Justin Forsett', 'Jay Ajayi', 'Ty Montgomery']
    page_two_players = ['Mack Brown', 'Ezekiel Elliot', 'Darrius Heyward-Bey', 'David Johnson', 'Matt Jones',
                        'Corey Grant', 'J.J. Nelson', 'Tevin Coleman', 'Albert Wilson', 'Tyrod Taylor',
                        'Kerwynn Williams', 'Melvin Gordon', 'Jonathan Stewart', 'Carlos Hyde', 'Spencer Ware']
    with flask_app.test_client() as test_client:
        page_one = test_client.get('/?page=1&sort=lng')
        page_two = test_client.get('/?page=2&sort=lng')
        for player in page_one_players:
            assert player.encode() in page_one.data
            assert player.encode() not in page_two.data
        for player in page_two_players:
            assert player.encode() in page_two.data
            assert player.encode() not in page_one.data


def test_filter_by_name():
    players_named_brown = ['Mack Brown', 'Malcolm Brown', 'John Brown', 'Antonio Brown', 'Corey Brown']
    players_named_eli = ['Eli Rogers', 'Eli Manning']
    with flask_app.test_client() as test_client:
        brown_search = test_client.get('/?name=brown')
        eli_search = test_client.get('/?name=eli')
        for player in players_named_brown:
            assert player.encode() in brown_search.data
            assert player.encode() not in eli_search.data
        for player in players_named_eli:
            assert player.encode() in eli_search.data
            assert player.encode() not in brown_search.data


def test_filter_by_name_case_insensitive():
    players_named_eli = ['Eli Rogers', 'Eli Manning']
    with flask_app.test_client() as test_client:
        upper_search = test_client.get('/?name=ELI')
        mixed_search = test_client.get('/?name=eLi')
        for player in players_named_eli:
            assert player.encode() in upper_search.data
            assert player.encode() in mixed_search.data


def test_download():
    with flask_app.test_client() as test_client:
        with open('rushing.json', 'r') as f:
            expected_players = [d['Player'] for d in json.load(f)]

        response_data = test_client.get('/download').data.decode()
        for player in expected_players:
            assert player in response_data


def test_download_exists():
    with flask_app.test_client() as test_client:
        response_one = test_client.get('/download').data.decode()
        response_two = test_client.get('/download').data.decode()
        assert response_one == response_two


def test_download_filtered():
    players_named_eli = ['Eli Rogers', 'Eli Manning']
    with flask_app.test_client() as test_client:
        response = test_client.get('/download?name=eli')
        response_data = response.data.decode()
        assert 'data-name-eli.csv' in response.headers['content-disposition']
        for player in players_named_eli:
            assert player in response_data


def test_download_sorted():
    with flask_app.test_client() as test_client:
        with open('rushing.json', 'r') as f:
            expected_players = [d['Player'] for d in json.load(f)]
        response = test_client.get('/download?sort=td')
        response_data = response.data.decode()
        assert 'data-sort-td.csv' in response.headers['content-disposition']
        for player in expected_players:
            assert player in response_data


def teardown_module():
    directory_name = 'nfl_rushing/reports'
    if os.path.exists(directory_name):
        shutil.rmtree(directory_name)
