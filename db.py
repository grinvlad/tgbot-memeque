import os
import sqlite3

connection = sqlite3.connect(os.path.join('db', 'memes.db'))
cursor = connection.cursor()


def fetch_all(table: str, attributes: list[str]) -> list[dict]:
    attributes_joined = ', '.join(attributes)
    cursor.execute(f'SELECT {attributes_joined} FROM {table}')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, attribute in enumerate(attributes):
            dict_row[attribute] = row[index]
        result.append(dict_row)
    return result


def insert(table: str, attributes: dict) -> int:
    placeholders = ', '.join('?' * len(attributes.values()))
    cursor.execute(
        f'INSERT INTO {table} ({", ".join(attributes.keys())})'
        f'VALUES ({placeholders})',
        tuple(attributes.values()))
    connection.commit()
    return cursor.lastrowid


def get_connection():
    return connection


def _init_db():
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    connection.commit()


def check_db_exists():
    cursor.execute("SELECT name "
                   "FROM sqlite_master "
                   "WHERE type='table' AND name='meme'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
