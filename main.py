import time

import requests
from bs4 import BeautifulSoup
import logging
from data_handling import load_existing_data, OUTPUT_FILE, load_state, save_state, save_data
from data_scrapper import scrape_ted_data, fetch_data, parse_url, get_last_page, SEARCH_URL, BASE_WEBSITE
from utils import fetch_response, create_session, get_cookies
from user_interface import print_last_processed_page_message

REQUEST_DELAY = 1


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='app.log',
        filemode='a'
    )


def main() -> None:
    configure_logging()

    session = create_session()
    cookies = get_cookies()

    all_data = load_existing_data(OUTPUT_FILE)
    state = load_state()
    last_processed_page = state.get('last_processed_page', 1)
    existing_links = set(entry['URL'] for entry in all_data)
    last_processed_flag = True

    if last_processed_page != 1:
        print_last_processed_page_message(last_processed_page)
        user_choice = input("Do you want to start from the last processed page? (y/n): ").strip().lower()

        if user_choice == 'n':
            last_processed_page = 1
            state['last_processed_page'] = last_processed_page
            save_state(state)
            last_processed_flag = False

    try:
        response = fetch_response(session, SEARCH_URL, cookies)

        if not response:
            print(f'Failed to retrieve the URL "{SEARCH_URL}".')
            logging.error(f'Failed to retrieve the URL "{SEARCH_URL}".')

            return

        soup = BeautifulSoup(response.text, 'html.parser')
        last_page_number = get_last_page(soup.find('div', class_='page-icon pagelast'))

        if not last_page_number:
            print('Failed to retrieve last page...stopping the process')
            logging.error('Failed to retrieve last page...stopping the process')
            return

        for page in range(last_processed_page, last_page_number):
            params = {'page': page}
            hrefs = fetch_data(session, SEARCH_URL, cookies, params)

            if not hrefs:
                print(f'Failed to retrieve page {page}! Status code: {response.status_code}')
                logging.warning(f'Failed to retrieve page {page}! Status code: {response.status_code}')
                continue

            state['last_processed_page'] = page
            save_state(state)

            for href in hrefs:
                current_url = parse_url(href)
                data_url = BASE_WEBSITE + current_url
                document_main_url = BASE_WEBSITE + href

                if document_main_url in existing_links and not last_processed_flag:
                    print(f'Data successfully updated.')
                    logging.info(f'Data successfully updated.')

                    return

                if document_main_url in existing_links and last_processed_flag:
                    print(f'Continuing to next url, because this one is already scrapped: {document_main_url}')
                    logging.info(
                        f'Continuing to the next URL, because this one is already scrapped: {document_main_url}')

                    continue

                print(f'Working on URL on page {page}: {current_url}...')

                data = scrape_ted_data(session, cookies, data_url, document_main_url)
                if data:
                    all_data.append(data)
                    curr_time = time.localtime()
                    print(
                        f'{time.strftime("%H:%M:%S", curr_time)}Successfully fetched data on page {page} from URL {data_url}')
                    logging.info(f'Successfully fetched data on page {page} from URL {data_url}')

                else:
                    print(
                        f'Impossible to fetch data from URL: {document_main_url} on page {page} because it does not '
                        f'have a data page')
                    logging.warning(
                        f'Impossible to fetch data from URL: {document_main_url} on page {page} because it does not '
                        f'have a data page')
                time.sleep(REQUEST_DELAY)

            save_data(all_data, OUTPUT_FILE)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving data collected so far.")
        logging.info("Process interrupted by user. Saving data collected so far.")

        save_data(all_data, OUTPUT_FILE)

    except Exception as e:
        print(f"An unexpected error occurred - {str(e)}")
        logging.error(f"An unexpected error occurred - {str(e)}")
        save_data(all_data, OUTPUT_FILE)


if __name__ == "__main__":
    main()
