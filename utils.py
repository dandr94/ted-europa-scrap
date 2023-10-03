import os
import requests
from dotenv import load_dotenv

load_dotenv()


def create_session() -> requests.Session:
    session = requests.Session()
    return session


def get_cookies() -> dict:
    cookies = {
        'cck1': os.getenv('CCK1'),
        'JSESSIONID': os.getenv('JSESSIONID'),
        'ln_pref': os.getenv('LG_PREF')
    }

    return cookies


def fetch_response(session, url, cookies, params=None):
    response = session.get(url, cookies=cookies, allow_redirects=False, params=params)

    if response.status_code == 200:
        return response
    return None
