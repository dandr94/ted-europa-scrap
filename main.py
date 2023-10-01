import json
import re
import time

import requests
from bs4 import BeautifulSoup
from data_scrapper import scrape_ted_data
from helper import cookies, BASE_WEBSITE, SEARCH_URL, fetch_response
from typing import List, Optional, Dict

REQUEST_DELAY = 1


def get_last_page(element: BeautifulSoup) -> int:
    """
    Get the last page number from the BeautifulSoup element.

    Args:
        element (BeautifulSoup): The BeautifulSoup element containing pagination information.

    Returns:
        int: The last page number.
    """
    last_page_link = element.find('a')
    match = re.search(r'page=(\d+)', last_page_link['href'])
    last_page_number = int(match.group(1))
    return last_page_number


def load_existing_data(filename: str) -> List[Dict[str, str]]:
    """
        Load existing data from a JSON file.

        Args:
            filename (str): The name of the JSON file to read data from.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the loaded data.
                An empty list is returned if the file is not found or an error occurs.
        """
    try:
        with open(filename, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
        return existing_data
    except FileNotFoundError:
        return []


def save_data(data: List[Dict[str, str]], filename: str) -> None:
    """
    Save scraped data to a JSON file.

    Args:
        data (List[Dict[str, str]]): List of dictionaries containing scraped data.
        filename (str): The name of the JSON file to save data to.
    """
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f'Data saved successfully to {filename}!')


def parse_url(href: str) -> str:
    """
    Parse and modify a URL.

    Args:
        href (str): The URL to be modified.

    Returns:
        str: The modified URL.
    """
    return href.replace("TEXT", "DATA").replace("src=0", "tabId=3")


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
    response = fetch_response(session, url, cookies, params)
    if not response:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    td_elements = soup.find_all('td', class_='nowrap')
    hrefs = [td.find('a')['href'] for td in td_elements if td.find('a')]
    return hrefs


def main() -> None:
    session = requests.Session()

    all_data = load_existing_data('output.json')

    try:
        response = fetch_response(session, SEARCH_URL, cookies)

        if not response:
            print(f'Failed to retrieve the URL "{SEARCH_URL}".')
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        last_page_number = get_last_page(soup.find('div', class_='page-icon pagelast'))

        for page in range(3, last_page_number):
            params = {'page': page}
            hrefs = fetch_data(session, SEARCH_URL, cookies, params)

            if not hrefs:
                print(f'Failed to retrieve page {page}! Status code: {response.status_code}')
                continue

            for href in hrefs:
                current_url = parse_url(href)
                print(f'Working on URL on page {page}: {current_url}...')

                data = scrape_ted_data(session, BASE_WEBSITE + current_url)
                if data:
                    all_data.append(data)
                    print(f'Successfully fetched data on page {page} from URL {current_url}')
                else:
                    print(
                        f'Impossible to fetch data from URL: {BASE_WEBSITE + href} on page {page} \
                        because it does not have a data page')
                time.sleep(REQUEST_DELAY)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving data collected so far.")
        save_data(all_data, 'output.json')
        return

    save_data(all_data, 'output.json')


if __name__ == "__main__":
    main()
