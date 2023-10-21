import os
import time
import logging
import requests
from dotenv import load_dotenv
from typing import Set, Optional

load_dotenv()


class TextFormatter:
    """
        A utility class for formatting text messages with ANSI color codes and symbols, making it easier to convey
        the meaning and status of messages in a visually distinguishable manner.
    """

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

    def format_message(self,
                       message: str,
                       color: str,
                       symbol: str) -> str:
        return f'{self.ANSI[color]}{self.symbols[symbol]} {message}{self.ANSI["reset"]}'

    def format_message_success(self, message: str) -> str:
        return self.format_message(message, 'green', 'success')

    def format_message_fail(self, message: str) -> str:
        return self.format_message(message, 'red', 'fail')

    def format_message_work_in_progress(self, message: str) -> str:
        return self.format_message(message, 'yellow', 'work_in_progress')

    def format_custom_message(self, message: str, color: str) -> str:
        return f'{self.ANSI[color]} {message}{self.ANSI["reset"]}'


# Logger class for handling logging
class Logger:
    """
    A class for logging messages to a file.
    """
    LOG_FILE_NAME = 'app.log'
    LOG_FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'

    def __init__(self):
        """
        Initialize the Logger class.

        This constructor sets up the logger with a specified format and file handler.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(self.LOG_FORMATTER)
        file_handler = logging.FileHandler(self.LOG_FILE_NAME)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_info(self, message: str) -> None:
        self.logger.info(message)

    def log_error(self, message: str) -> None:
        self.logger.error(message)

    def log_warning(self, message: str) -> None:
        self.logger.warning(message)


def create_session() -> requests.Session:
    session = requests.Session()

    return session


def get_cookies() -> dict:
    cookies = {
        'JSESSIONID': os.getenv('JSESSIONID'),
        'ln_pref': os.getenv('LG_PREF')
    }

    return cookies


def fetch_response(session: requests.Session,
                   url: str,
                   cookies: dict,
                   params: dict = None) -> Optional[requests.Response]:
    response = session.get(url, cookies=cookies, allow_redirects=False, params=params)

    if response.status_code == 200:
        return response

    return None


def get_current_time() -> str:
    return time.strftime("%H:%M:%S", time.localtime())


def time_left_until_all_data_is_fetched(documents_left: int) -> str:
    seconds = documents_left
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return f'{hours}h {minutes}m {seconds}s'


def state_file_exists() -> bool:
    return os.path.exists('state.json')


def url_is_scrapped(document_main_url: str,
                    existing_links: Set[str],
                    action: str) -> bool:
    return document_main_url in existing_links and action == '1'


def update_has_reach_last_scrapped_url(document_main_url: str,
                                       existing_links: Set[str],
                                       action: str) -> bool:
    return document_main_url in existing_links and action == '2'


def action_is_update(action: str) -> bool:
    return action == '2'
