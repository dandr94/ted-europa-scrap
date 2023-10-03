import logging
import re
from typing import Dict, Union, Optional, List

import requests
from requests.sessions import Session
from bs4 import BeautifulSoup
from utils import fetch_response

BASE_WEBSITE = 'https://ted.europa.eu'

SEARCH_URL = "https://ted.europa.eu/TED/search/searchResult.do?page=1"

logger = logging.getLogger(__name__)


def fetch_data(session: requests.Session, url: str, cookies: dict, params: Optional[dict] = None) -> List[str]:
    """
    Fetch and extract data from a webpage.

    Args:
        session (requests.Session): The session for making HTTP requests.
        url (str): The URL to fetch data from.
        cookies (dict): Cookies to be used in the request.
        params (dict, optional): Query parameters for the request.

    Returns:
        List[str]: List of extracted URLs.
    """
    try:
        response = fetch_response(session, url, cookies, params)
        if not response:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        td_elements = soup.find_all('td', class_='nowrap')
        hrefs = [td.find('a')['href'] for td in td_elements if td.find('a')]
        return hrefs
    except Exception as e:
        logger.error(f'An error occurred while fetching data from {url}: {str(e)}')
        return []


def get_last_page(element: BeautifulSoup) -> int:
    """
    Get the last page number from the BeautifulSoup element.

    Args:
        element (BeautifulSoup): The BeautifulSoup element containing pagination information.

    Returns:
        int: The last page number.
    """
    try:
        last_page_link = element.find('a')
        match = re.search(r'page=(\d+)', last_page_link['href'])
        last_page_number = int(match.group(1))
        return last_page_number
    except Exception as e:
        logger.error(f'An error occurred while getting the last page number: {str(e)}')
        return 0


def parse_url(href: str) -> str:
    """
    Parse and modify a URL.

    Args:
        href (str): The URL to be modified.

    Returns:
        str: The modified URL.
    """
    return href.replace("TEXT", "DATA").replace("src=0", "tabId=3")


def data_page_exist_in_document(soup: BeautifulSoup) -> bool:
    """
       Check if a data page exists in the document.

       Args:
           soup (BeautifulSoup): The BeautifulSoup object representing the HTML content of the document.

       Returns:
           bool: True if a data page exists in the document, False otherwise.
    """
    try:
        data = soup.select_one('a.selected:-soup-contains("Data")')
        return True if data else False
    except AttributeError as e:
        logger.error(f'An error occurred while checking if a data page exists: {str(e)}')
        return False


def extract_data_from_table(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extracts data from the HTML table on the document's page.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML page.

    Returns:
        Dict[str, str]: A dictionary containing extracted data.
    """
    data_dict = {}
    table = soup.find('table', {'class': 'data'})

    if table:
        rows = table.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            if len(tds) == 2:
                key = tds[0].text.strip()
                value = re.sub(r'\s+', ' ', tds[1].text.strip())
                matches = re.split(r'(\d+ - [^\d]+)', value)
                data_dict[key] = ', '.join(match.strip() for match in matches if match.strip())

    return data_dict


def scrape_ted_data(session: Session, cookies, document_data_page_url: str, document_main_page_url) -> \
        Union[Dict[str, str], None]:
    """
    Scrapes data from a TED document page.

    Args:
        session (Session): The requests.Session object for making HTTP requests.
        url (str): The URL of the TED document page.

    Returns:
        Dict[str, str]: A dictionary containing scraped data.
    """
    data_dict = {}

    response = fetch_response(session=session, cookies=cookies, url=document_data_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    if not data_page_exist_in_document(soup):
        return None

    data_dict['URL'] = document_main_page_url

    data_dict.update(extract_data_from_table(soup))

    return data_dict
