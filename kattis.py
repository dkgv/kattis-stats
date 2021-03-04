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
Profile = namedtuple('Profile', ['name', 'uid', 'rank',
                                 'score', 'country', 'country_short', 'university', 'university_short'])


def _scrape_profile(uid: str) -> Profile:
    url = 'https://open.kattis.com/users/{}'.format(uid)
    r = requests.get(url, headers={
                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
                     })
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, 'lxml')
    name = soup.title.text.split(' – ')[0]

    country_a = soup.select_one('.text > a:nth-child(1)')
    country = '' if not country_a else country_a.text
    country_short = '' if not country_a else country_a['href'].split('/')[-1]

    uni_a = soup.select_one(
        '.university-logo > span:nth-child(2) > a:nth-child(1)')
    uni = '' if not uni_a else uni_a.text
    uni_short = '' if not uni_a else uni_a['href'].split(
        '/')[-1]

    row = soup.find('table').find_all('tr')[1]
    cols = row.find_all('td')

    rank = cols[0].text.strip()
    score = cols[1].text.strip()

    return Profile(name, uid, rank, score, country, country_short, uni, uni_short)


def find_all_history() -> List[Profile]:
    return [row['fields'] for row in stats_table.get_all()]


def find_all_user_ids() -> list:
    return [row['fields']['UserId'] for row in users_table.get_all()]


def fetch_for_user(uid: str) -> Profile:
    profile = _scrape_profile(uid)
    stats_table.insert({
        'UserId': uid,
        'Rank': int(profile.rank),
        'Score': float(profile.score),
        'Date': str(datetime.date.today()),
    })
    return profile


if __name__ == '__main__':
    for uid in find_all_user_ids():
        fetch_for_user(uid)
