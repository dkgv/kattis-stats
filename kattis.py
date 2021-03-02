import os
import requests
import datetime
from typing import List
from collections import namedtuple
from airtable import Airtable
from bs4 import BeautifulSoup


def _get_airtable(table: str) -> Airtable:
    api_key = os.environ['AIRTABLE_API_KEY']
    return Airtable('app6pZ1s8sxjhqGH6', api_key=api_key, table_name=table)

stats_table = _get_airtable('Stats')
users_table = _get_airtable('Users')
Stats = namedtuple('Stats', ['profile_id', 'rank', 'score'])


def _scrape_stats(uid: str) -> Stats:
    url = 'https://open.kattis.com/users/{}'.format(uid)
    r = requests.get(url, headers={
                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
                     })
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, 'lxml')
    name = soup.select_one('.fullname > h1:nth-child(1)')

    row = soup.find('table').find_all('tr')[1]
    cols = row.find_all('td')

    rank = cols[0].text.strip()
    score = cols[1].text.strip()

    return Stats(name.text.strip(), rank, score)


def find_all_history() -> List[Stats]:
    return [row['fields'] for row in stats_table.get_all()]


def find_all_user_ids() -> list:
    return [row['fields']['UserId'] for row in users_table.get_all()]


def fetch_for_user(uid: str) -> None:
    stats = _scrape_stats(uid)
    stats_table.insert({
        'UserId': uid,
        'Rank': int(stats.rank),
        'Score': float(stats.score),
        'Date': str(datetime.date.today())
    })


if __name__ == '__main__':
    for uid in find_all_user_ids():
        fetch_for_user(uid)
