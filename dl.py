import psycopg2
from psycopg2 import Error
import json
from configparser import ConfigParser
from igdb.wrapper import IGDBWrapper
import requests


def config(section):
    parser = ConfigParser()
    parser.read('config.ini')

    db = {}
    params = parser.items(section)
    for param in params:
        db[param[0]] = param[1]
    
    return db


def get_all_games():
    sql = """SELECT * FROM games"""

    conn = None
    vendor_id = None
    try:
        params = config('postgresql')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute("SELECT * FROM games")
        results = []
        rows = cur.fetchall()
        for row in rows:
            result = {}
            result['id'] = row[0]
            result['name'] = row[1]
            result['url'] = row[2]
            result['img_url'] = row[3]
            results.append(result)

        cur.close()
        return results
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_game(game):
    sql = """INSERT INTO games(id, name, url) VALUES(%s, %s, %s)"""

    conn = None
    vendor_id = None
    try:
        params = config('postgresql')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(sql, (game['id'], game['name'], game['url']))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def update_game(game):
    sql = """ UPDATE games
                SET name = %s, url = %s, img_url = %s, img_width = %s, img_height = %s
                WHERE id = %s"""

    conn = None
    vendor_id = None
    try:
        params = config('postgresql')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(sql, (game['name'], game['url'], game['img_url'], game['img_width'], game['img_height'], game['id'] ))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def get_cover(game):
    global token, client_id

    headers = { 'Client-ID': client_id, 'Authorization': 'Bearer ' + token}
    query = 'fields *; where game=' + str(game['id']) + ';'
    print(game['name'])
    response = requests.post('https://api.igdb.com/v4/covers', headers=headers, data=query).json()[0]
    return response


def seed_init():
    for game in get_all_games():
        if game['img_url'] is not None:
            continue

        cover = get_cover(game)
        game['img_width'] = cover['width']
        game['img_height'] = cover['height']
        game['img_url'] = 'https:' + cover['url']
        update_game(game)

igdb_config = config('igdb')
client_id = igdb_config['id']
token = requests.post('https://id.twitch.tv/oauth2/token', { 'client_id': client_id, 'client_secret': igdb_config['secret'], 'grant_type': 'client_credentials' } ).json()['access_token']

games = get_all_games()
print(games)