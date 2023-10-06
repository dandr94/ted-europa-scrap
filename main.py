import time

from bs4 import BeautifulSoup
import logging
from data_handling import load_existing_data, OUTPUT_FILE, load_state, save_state, save_data
from data_scrapper import scrape_ted_data, fetch_hrefs, parse_url, get_last_page, SEARCH_URL, BASE_WEBSITE
from utils import fetch_response, create_session, get_cookies, get_current_time, time_left_until_all_data_is_fetched, \
    TextFormatter
from user_interface import print_last_processed_page_message, get_user_choice_for_last_processed_page

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
    text_formatter = TextFormatter()

    session = create_session()
    cookies = get_cookies()

    all_data = load_existing_data(OUTPUT_FILE)
    state = load_state()
    last_processed_page = state.get('last_processed_page', 1)
    existing_links = set(entry['URL'] for entry in all_data)
    last_processed_flag = True

    if last_processed_page != 1:
        print_last_processed_page_message(last_processed_page)
        user_choice = get_user_choice_for_last_processed_page()

        if user_choice == 'n':
            last_processed_page = 1
            state['last_processed_page'] = last_processed_page
            save_state(state)
            last_processed_flag = False

    try:
        response = fetch_response(session, SEARCH_URL, cookies)

        if not response:
            print(text_formatter.format_message_fail(f'Failed to retrieve the URL "{SEARCH_URL}".'))
            logging.error(f'Failed to retrieve the URL "{SEARCH_URL}".')

            return

        soup = BeautifulSoup(response.text, 'html.parser')
        last_page_number = get_last_page(soup.find('div', class_='page-icon pagelast'))

        if not last_page_number:
            print(text_formatter.format_message_fail('Failed to retrieve last page...stopping the process'))
            logging.error('Failed to retrieve last page...stopping the process')
            return

        for page in range(last_processed_page, last_page_number):
            params = {'page': page}
            hrefs = fetch_hrefs(session, SEARCH_URL, cookies, params)

            if not hrefs:
                print(text_formatter.format_message_fail(
                    f'Failed to retrieve page {page}! Status code: {response.status_code}'))
                logging.warning(f'Failed to retrieve page {page}! Status code: {response.status_code}')
                continue

            state['last_processed_page'] = page
            save_state(state)

            for href in hrefs:
                current_url = parse_url(href)
                data_url = BASE_WEBSITE + current_url
                document_main_url = BASE_WEBSITE + href

                if document_main_url in existing_links and not last_processed_flag:
                    print(text_formatter.format_message_success('Data successfully updated.'))
                    logging.info('Data successfully updated.')
                    return

                if document_main_url in existing_links and last_processed_flag:
                    print(text_formatter.format_message_work_in_progress(
                        f'Continuing to next URL on page {page}, because this one is already scrapped: {document_main_url}'))

                    logging.info(
                        f'Continuing to the next URL on page {page}, because this one is already scrapped: {document_main_url}')

                    continue
                print(text_formatter.format_message_work_in_progress(
                    f'[{get_current_time()}] - Working on URL on page {page}/{last_page_number}: {current_url}...'))

                data = scrape_ted_data(session, cookies, data_url, document_main_url)

                if data:
                    all_data.append(data)
                    print(text_formatter.format_message_success(
                        f'[{get_current_time()}] - Successfully fetched data on page {page} from URL {data_url}'))

                    logging.info(f'Successfully fetched data on page {page} from URL {data_url}')

                else:
                    print(text_formatter.format_message_fail(
                        f'[{get_current_time()}] - Impossible to fetch data from URL: {document_main_url} on page {page} because it does not '
                        f'have a data page'))

                    logging.warning(
                        f'Impossible to fetch data from URL: {document_main_url} on page {page} because it does not '
                        f'have a data page')

                time.sleep(REQUEST_DELAY)

            save_data(all_data, OUTPUT_FILE)

            logging.info(f'[{get_current_time()}] - Data saved successfully to {OUTPUT_FILE}!')

            if last_processed_flag:
                pages_remaining = last_page_number - state['last_processed_page']
                documents_left = pages_remaining * 25
                print(text_formatter.format_message_work_in_progress(
                    f'[{get_current_time()}] - Time left until all data is fetched: ~{time_left_until_all_data_is_fetched(documents_left)}'))

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving data collected so far.")
        logging.info("Process interrupted by user. Saving data collected so far.")

        save_data(all_data, OUTPUT_FILE)

    except Exception as e:
        print(text_formatter.format_message_fail(f"An unexpected error occurred - {str(e)}"))
        logging.error(f"An unexpected error occurred - {str(e)}")
        save_data(all_data, OUTPUT_FILE)


if __name__ == "__main__":
    main()
