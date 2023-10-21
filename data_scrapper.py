import logging
import re
from typing import Dict, Union, Optional, List

import requests
from requests.sessions import Session
from bs4 import BeautifulSoup
from utils import fetch_response

BASE_WEBSITE = 'https://ted.europa.eu'

SEARCH_URL = "https://ted.europa.eu/TED/search/searchResult.do"

logger = logging.getLogger(__name__)


def extract_hrefs(response: requests.Response) -> List[str]:
    """
        Extract all document hrefs from current page.
    """

    soup = BeautifulSoup(response.text, 'html.parser')
    td_elements = soup.find_all('td', class_='nowrap')
    hrefs = [td.find('a')['href'] for td in td_elements if td.find('a')]
    return hrefs


def get_last_page(element: BeautifulSoup) -> int:
    """
        Get the last page number from the search result.
    """
    try:
        last_page_link = element.find('a')
        match = re.search(r'page=(\d+)', last_page_link['href'])
        last_page_number = int(match.group(1))
        return last_page_number
    except Exception as e:
        logger.error(f'An error occurred while getting the last page number: {str(e)}')
        return 0


def modify_url(href: str) -> str:
    """
        Modify a URL. Helps with constructing the data page url from the main document one.
    """
    return href.replace("TEXT", "DATA").replace("src=0", "tabId=3")


def data_page_exist_in_document(soup: BeautifulSoup) -> bool:
    """
       Check if a data page exists in the document.
    """
    try:
        data = soup.select_one('a.selected:-soup-contains("Data")')
        return bool(data)
    except AttributeError as e:
        logger.error(f'An error occurred while checking if a data page exists: {str(e)}')
        return False


def extract_data_from_table(soup: BeautifulSoup) -> Dict[str, str]:
    """
        Extracts data from the HTML table on the document's page.
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


def scrape_ted_data(session: Session,
                    cookies: dict,
                    document_data_page_url: str,
                    document_main_page_url) -> Union[Dict[str, str], None]:
    """
        Scrapes data from a TED document page.
    """

    data_dict = {}

    response = fetch_response(session=session, cookies=cookies, url=document_data_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    if not data_page_exist_in_document(soup):
        return None

    data_dict['URL'] = document_main_page_url

    data_dict.update(extract_data_from_table(soup))

    return data_dict
