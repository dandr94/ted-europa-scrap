import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()


class TextFormatter:
    def __init__(self):
        self.symbols = {
            'success': '\u2713',
            'fail': '\u2717',
            'work_in_progress': '\u21BB'
        }

        self.ANSI = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'reset': '\033[0m'
        }

    def format_message(self, message, color, symbol=None):
        return f'{self.ANSI[color]}{self.symbols[symbol]} {message}{self.ANSI["reset"]}'

    def format_message_success(self, message):
        return self.format_message(message, 'green', 'success')

    def format_message_fail(self, message):
        return self.format_message(message, 'red', 'fail')

    def format_message_work_in_progress(self, message):
        return self.format_message(message, 'yellow', 'work_in_progress')


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


def get_current_time():
    return time.strftime("%H:%M:%S", time.localtime())


def time_left_until_all_data_is_fetched(documents_left):
    seconds = documents_left
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return f'{hours}h {minutes}m {seconds}s'
