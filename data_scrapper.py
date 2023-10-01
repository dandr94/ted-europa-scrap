import re
from typing import Dict
from requests.sessions import Session
from bs4 import BeautifulSoup
from helper import BASE_WEBSITE, fetch_response, cookies


def extract_document_main_page_url(soup: BeautifulSoup) -> str:
    """
    Extracts the URL of the document's main page from the given BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML page.

    Returns:
        str: The URL of the document's main page.
    """
    notice_tab_link = soup.find('li', {'class': 'noticeTab'})
    a_tag = notice_tab_link.find('a')
    return a_tag['href']


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


def scrape_ted_data(session: Session, url: str) -> Dict[str, str]:
    """
    Scrapes data from a TED document page.

    Args:
        session (Session): The requests.Session object for making HTTP requests.
        url (str): The URL of the TED document page.

    Returns:
        Dict[str, str]: A dictionary containing scraped data.
    """
    data_dict = {}

    response = fetch_response(session=session, cookies=cookies, url=url)
    soup = BeautifulSoup(response.text, 'html.parser')

    document_main_page_url = extract_document_main_page_url(soup)

    data_dict['URL'] = BASE_WEBSITE + document_main_page_url

    data_dict.update(extract_data_from_table(soup))

    return data_dict
