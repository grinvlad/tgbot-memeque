import csv
import datetime
import sqlite3
import pytz
import random
from typing import Any
from functools import wraps
from typing import NamedTuple

from custom_exceptions import MemeException
import db


class Meme(NamedTuple):
    id: int
    user_id: int
    meme_type: str
    comment: str
    file_id: str


meme_que: list[Meme] = []


def init_que(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not meme_que:
            _make_random_que()
        return func(*args, **kwargs)
    return wrapper


@init_que
def get_next_meme() -> Meme:
    return meme_que.pop()


@init_que
def length() -> int:
    return len(meme_que)


def add_meme(file_info: dict[str, Any]) -> Meme:
    try:
        meme_id = db.insert('meme', {
            'user_id': file_info['user_id'],
            'created': _get_now_formatted(),
            'meme_type': file_info['meme_type'],
            'comment': file_info['comment'],
            'file_id': file_info['file_id'],
            'file_unique_id': file_info['file_unique_id'],
            'file_size': file_info['file_size']
        })
    except sqlite3.IntegrityError:
        raise MemeException('Такой мем уже есть в сборнике')

    meme = Meme(id=meme_id,
                user_id=file_info['user_id'],
                meme_type=file_info['meme_type'],
                comment=file_info['comment'],
                file_id=file_info['file_id'])
    meme_que.append(meme)
    return meme


def delete_meme_from_db(row_id: int, user_id: int) -> str:
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute(f'DELETE '
                   f'FROM meme '
                   f'WHERE id={row_id} AND user_id={user_id}')
    connection.commit()
    if cursor.rowcount == 1:
        return 'Удалил из сборника.'
    else:
        raise MemeException('Либо мема с таким id в сборнике нет, либо он не твой.')


@init_que
def delete_meme_from_que(row_id: int, user_id: int) -> str:
    for index, meme in enumerate(meme_que):
        if meme.id == row_id and meme.user_id == user_id:
            meme_que.pop(index)
            return 'Удалил из очереди.'
    raise MemeException('Либо мема с таким id в очереди нет, либо он не твой.')


def get_db_stats(file_name: str) -> None:
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT meme_type, COUNT(*) as N, SUM(file_size) / 1000000 as MB '
                   'FROM meme '
                   'GROUP BY meme_type '
                   'ORDER BY N DESC, MB DESC')
    rows = cursor.fetchall()
    rows += [('total', sum(row[1] for row in rows), sum(row[2] for row in rows))]
    with open(f'{file_name}', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Meme type', 'Quantity', 'Size (MB)'])
        writer.writerows(rows)


def _make_random_que() -> None:
    global meme_que
    memes: list[dict] = db.fetch_all('meme',
                                     'id user_id meme_type comment file_id'.split())
    result: list[Meme] = []
    for meme in memes:
        result.append(Meme(id=meme['id'],
                           user_id=meme['user_id'],
                           meme_type=meme['meme_type'],
                           comment=meme['comment'],
                           file_id=meme['file_id']))
    if not result:
        raise MemeException('Сборник с мемами пустой :(')
    meme_que = random.sample(result, len(result))


def _get_now_formatted() -> str:
    return _get_now_datetime().strftime('%Y-%m-%d %H:%M:%S')


def _get_now_datetime() -> datetime.datetime:
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now(tz)
    return now
