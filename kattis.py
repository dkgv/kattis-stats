import os
import gspread
import requests
import datetime
from typing import List
from collections import namedtuple
from bs4 import BeautifulSoup

credentials = {
    'type': os.getenv('type'),
    'project_id': os.getenv('project_id'),
    'private_key_id': os.getenv('private_key_id'),
    'private_key': os.getenv('private_key').replace('\\n', '\n'),
    'client_email': os.getenv('client_email'),
    'client_id': os.getenv('client_id'),
    'auth_uri': os.getenv('auth_uri'),
    'token_uri': os.getenv('token_uri'),
    'auth_provider_x509_cert_url': os.getenv('auth_provider_x509_cert_url'),
    'client_x509_cert_url': os.getenv('client_x509_cert_url')
}

gc = gspread.service_account_from_dict(credentials)
sheet = gc.open('kattis-stats')
stats_table = sheet.worksheet('Stats')
users_table = sheet.worksheet('Users')

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


def find_all_user_ids() -> list:
    return users_table.col_values(1)


def fetch_for_user(uid: str) -> Profile:
    profile = _scrape_profile(uid)
    stats_table.append_row([
        uid,
        int(profile.rank),
        float(profile.score),
        str(datetime.date.today())
    ])
    return profile


if __name__ == '__main__':
    for uid in find_all_user_ids():
        fetch_for_user(uid)
