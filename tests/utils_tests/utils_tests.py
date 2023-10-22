import unittest
from unittest.mock import patch, mock_open
import requests
import requests_mock

from utils import action_is_update, update_has_reach_last_scrapped_url, url_is_scrapped, state_file_exists, \
    time_left_until_all_data_is_fetched, get_current_time, fetch_response, get_cookies, create_session, Logger, \
    TextFormatter


class UtilsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text_formatter = TextFormatter()
        self.existing_links = {"url1", "url2", "url3"}

    # TextFormatter
    def test_format_message_success(self):
        formatted_message = self.text_formatter.format_message_success("Test Message")
        self.assertEqual(formatted_message, '\033[92m\u2713 Test Message\033[0m')

    def test_format_message_fail(self):
        formatted_message = self.text_formatter.format_message_fail("Test Message")
        self.assertEqual(formatted_message, '\033[91m\u2717 Test Message\033[0m')

    def test_format_message_work_in_progress(self):
        formatted_message = self.text_formatter.format_message_work_in_progress("Test Message")
        self.assertEqual(formatted_message, '\033[93m\u21BB Test Message\033[0m')

    def test_format_custom_message(self):
        formatted_message = self.text_formatter.format_custom_message("Test Message", 'red')
        self.assertEqual(formatted_message, '\033[91m Test Message\033[0m')

    # Logger

    @patch('builtins.open', new_callable=mock_open)
    def test_log_info(self, mock_file):
        logger = Logger()
        message = "Test info message"
        logger.log_info(message)

        log_output = mock_file().write.mock_calls[0][1][0]
        self.assertIn(message, log_output)

    @patch('builtins.open', new_callable=mock_open)
    def test_log_error(self, mock_file):
        logger = Logger()
        message = "Test error message"
        logger.log_error(message)

        log_output = mock_file().write.mock_calls[0][1][0]
        self.assertIn(message, log_output)

    @patch('builtins.open', new_callable=mock_open)
    def test_log_warning(self, mock_file):
        logger = Logger()
        message = "Test warning message"
        logger.log_error(message)

        log_output = mock_file().write.mock_calls[0][1][0]
        self.assertIn(message, log_output)

    # create_session

    def test_create_session_returns_session_object(self):
        session = create_session()
        self.assertIsInstance(session, requests.Session)

    # get_cookies

    @patch('utils.load_dotenv')
    @patch('os.getenv')
    def test_get_cookies_with_valid_environment_variables(self, mock_getenv, mock_load_dotenv):
        mock_load_dotenv.return_value = None

        mock_getenv.side_effect = lambda x: {'JSESSIONID': 'example_jsessionid', 'LG_PREF': 'example_ln_pref'}.get(x)

        cookies = get_cookies()

        self.assertEqual(cookies, {'JSESSIONID': 'example_jsessionid', 'ln_pref': 'example_ln_pref'})

    @patch('utils.load_dotenv')
    @patch('os.getenv')
    def test_get_cookies_with_missing_environment_variable(self, mock_getenv, mock_load_dotenv):
        mock_load_dotenv.return_value = None

        mock_getenv.side_effect = lambda x: {'JSESSIONID': 'example_jsessionid'}.get(x)

        cookies = get_cookies()

        self.assertEqual(cookies, {'JSESSIONID': 'example_jsessionid', 'ln_pref': None})

    # fetch_response

    def test_fetch_response_with_successful_request(self):
        url = "http://example.com"
        cookies = {"session_id": "12345"}
        expected_response = "Test Response Data"

        with requests_mock.mock() as m:
            m.get(url, text=expected_response, status_code=200)

            with requests.Session() as session:
                response = fetch_response(session, url, cookies)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, expected_response)

    def test_fetch_response_with_unsuccessful_request(self):
        url = "http://example.com"
        cookies = {"session_id": "12345"}

        with requests_mock.mock() as m:
            m.get(url, status_code=404)

            with requests.Session() as session:
                response = fetch_response(session, url, cookies)

        self.assertIsNone(response)

    def test_fetch_response_with_params(self):
        url = "http://example.com"
        cookies = {"session_id": "12345"}
        params = {"key": "value"}
        expected_response = "Test Response Data"

        with requests_mock.mock() as m:
            m.get(url, text=expected_response, status_code=200)

            with requests.Session() as session:
                response = fetch_response(session, url, cookies, params=params)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, expected_response)

    # get_current_time

    def test_get_current_time_format(self):
        result = get_current_time()
        expected_format = r"\d{2}:\d{2}:\d{2}"

        self.assertRegex(result, expected_format)

    # time_left_until_all_data_is_fetched

    def test_time_left_until_all_data_is_fetched_with_seconds(self):
        result = time_left_until_all_data_is_fetched(12345)
        self.assertEqual(result, "3h 25m 45s")

    def test_time_left_until_all_data_is_fetched_with_zero_seconds(self):
        result = time_left_until_all_data_is_fetched(0)
        self.assertEqual(result, "0h 0m 0s")

    # state_file_exists

    @patch('os.path.exists')
    def test_state_file_exists_when_file_exists(self, mock_exists):
        mock_exists.return_value = True

        result = state_file_exists()
        self.assertTrue(result)

    @patch('os.path.exists')
    def test_state_file_exists_when_file_does_not_exist(self, mock_exists):
        mock_exists.return_value = False

        result = state_file_exists()
        self.assertFalse(result)

    # url_is_scrapped

    def test_url_is_scrapped_with_matching_inputs(self):
        document_main_url = "url1"
        action = "1"
        result = url_is_scrapped(document_main_url, self.existing_links, action)
        self.assertTrue(result)

    def test_url_is_scrapped_with_non_matching_document_url(self):
        document_main_url = "url4"
        action = "1"
        result = url_is_scrapped(document_main_url, self.existing_links, action)
        self.assertFalse(result)

    def test_url_is_scrapped_with_non_matching_action(self):
        document_main_url = "url2"
        action = "2"
        result = url_is_scrapped(document_main_url, self.existing_links, action)
        self.assertFalse(result)

    # update_has_reach_last_scrapped_url

    def test_update_has_reach_last_scrapped_url_with_matching_inputs(self):
        document_main_url = "url1"
        action = "2"
        result = update_has_reach_last_scrapped_url(document_main_url, self.existing_links, action)
        self.assertTrue(result)

    def test_update_has_reach_last_scrapped_url_with_non_matching_document_url(self):
        document_main_url = "url4"
        action = "2"
        result = update_has_reach_last_scrapped_url(document_main_url, self.existing_links, action)
        self.assertFalse(result)

    def test_update_has_reach_last_scrapped_url_with_non_matching_action(self):
        document_main_url = "url2"
        action = "1"
        result = update_has_reach_last_scrapped_url(document_main_url, self.existing_links, action)
        self.assertFalse(result)

    # action_is_update

    def test_action_is_update_with_matching_action(self):
        self.assertTrue(action_is_update('2'))

    def test_action_is_update_with_non_matching_action(self):
        self.assertFalse(action_is_update('1'))
        self.assertFalse(action_is_update('3'))
        self.assertFalse(action_is_update('update'))
