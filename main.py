import time

from bs4 import BeautifulSoup
from data_handling import load_existing_data, OUTPUT_FILE, load_state, save_state, save_data
from data_scrapper import scrape_ted_data, extract_hrefs, modify_url, get_last_page, SEARCH_URL, BASE_WEBSITE
from utils import fetch_response, create_session, get_cookies, TextFormatter, url_is_scrapped, Logger, \
    update_has_reach_last_scrapped_url, action_is_update
from user_interface import get_user_choice_for_action, MessageProvider

REQUEST_DELAY = 1
MAXIMUM_DOCUMENTS_PER_PAGE = 25


def main() -> None:
    logger = Logger()
    message_provider = MessageProvider()
    text_formatter = TextFormatter()

    session = create_session()
    cookies = get_cookies()

    all_data = load_existing_data(OUTPUT_FILE)
    state = load_state()

    last_processed_page = state.get('last_processed_page', 1)
    existing_links = {entry['URL'] for entry in all_data}

    message_provider.default_app_message(text_formatter,
                                         len(existing_links),
                                         last_processed_page,
                                         bool(all_data),
                                         bool(state))

    action = None

    if state:
        action = get_user_choice_for_action()

        if action_is_update(action):
            last_processed_page = 1

    try:
        response = fetch_response(session, SEARCH_URL, cookies)

        if not response:
            print(text_formatter.format_message_fail(message_provider.message_failed_to_retrieve_url(SEARCH_URL)))
            logger.log_error(message_provider.message_failed_to_retrieve_url(SEARCH_URL))

            return

        soup = BeautifulSoup(response.text, 'html.parser')
        last_page_number = get_last_page(soup.find('div', class_='page-icon pagelast'))

        if not last_page_number:
            print(text_formatter.format_message_fail(message_provider.message_failed_to_retrieve_last_page()))

            logger.log_error(message_provider.message_failed_to_retrieve_last_page())

            return

        for page in range(last_processed_page, last_page_number):
            params = {'page': page}

            response = fetch_response(session, SEARCH_URL, cookies, params)

            if not response:
                print(text_formatter.format_message_fail(message_provider.message_failed_to_retrieve_url(SEARCH_URL)))
                logger.log_error(message_provider.message_failed_to_retrieve_url(SEARCH_URL))

                return

            hrefs = extract_hrefs(response)

            if not hrefs:
                print(text_formatter.format_message_fail(
                    message_provider.message_failed_to_retrieve_page(page, response.status_code)))

                logger.log_warning(message_provider.message_failed_to_retrieve_page(page, response.status_code))

                continue

            state['last_processed_page'] = page

            save_state(state)

            for href in hrefs:
                current_url = modify_url(href)
                data_url = BASE_WEBSITE + current_url
                document_main_url = BASE_WEBSITE + href

                if url_is_scrapped(document_main_url, existing_links, action):
                    print(text_formatter.format_message_work_in_progress(
                        message_provider.message_url_is_scrapped(page, document_main_url)))

                    logger.log_info(message_provider.message_url_is_scrapped(page, document_main_url))

                    continue

                if update_has_reach_last_scrapped_url(document_main_url, existing_links, action):
                    print(text_formatter.format_message_success(
                        message_provider.message_update_has_reach_last_scrapped_url()))

                    logger.log_info(message_provider.message_update_has_reach_last_scrapped_url())

                    return

                print(text_formatter.format_message_work_in_progress(message_provider.construct_message_with_time_stamp(
                    message_provider.message_work_in_progress(page, last_page_number, current_url))))

                data = scrape_ted_data(session, cookies, data_url, document_main_url)

                if data:
                    all_data.append(data)

                    print(text_formatter.format_message_success(message_provider.construct_message_with_time_stamp(
                        message_provider.message_successfully_scrapped_data(page, data_url))))

                    logger.log_info(message_provider.message_successfully_scrapped_data(page, data_url))

                    save_data(all_data, OUTPUT_FILE)

                    print(text_formatter.format_message_success(message_provider.construct_message_with_time_stamp(
                        message_provider.message_successful_data_save(OUTPUT_FILE))))

                    logger.log_info(message_provider.message_successful_data_save(OUTPUT_FILE))
                else:
                    print(text_formatter.format_message_fail(message_provider.construct_message_with_time_stamp(
                        message_provider.message_no_data_page(page, document_main_url))))

                    logger.log_warning(message_provider.message_no_data_page(page, document_main_url))

                save_state(state)

                time.sleep(REQUEST_DELAY)

            if not action_is_update(action):  # ETA but bad way of doing it
                pages_remaining = last_page_number - state['last_processed_page']
                documents_left = pages_remaining * (MAXIMUM_DOCUMENTS_PER_PAGE * REQUEST_DELAY)
                print(text_formatter.format_message_work_in_progress(message_provider.message_eta(documents_left)))

    except KeyboardInterrupt:
        print(message_provider.message_interrupted_by_user())
        logger.log_info(message_provider.message_interrupted_by_user())

    except Exception as e:
        print(text_formatter.format_message_fail(message_provider.message_unexpected_error_occurred(e)))
        logger.log_error(message_provider.message_unexpected_error_occurred(e))
        save_data(all_data, OUTPUT_FILE)


if __name__ == "__main__":
    main()
