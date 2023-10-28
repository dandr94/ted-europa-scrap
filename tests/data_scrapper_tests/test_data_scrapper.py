import unittest
from unittest.mock import patch, Mock

import requests
import requests_mock
from bs4 import BeautifulSoup

from data_scrapper import extract_hrefs, get_last_page, modify_url, data_page_exist_in_document, \
    extract_data_from_table, scrape_ted_data
from utils import fetch_response


class DataScrapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_url = 'http://test-example-mock.com'

    def test_extract_hrefs_with_valid_response(self):
        with requests_mock.Mocker() as m:
            html_content = """
            <html>
                <body>
                    <table>
                        <tr>
                            <td class="nowrap"><a href="link1">Link 1</a></td>
                            <td class="nowrap"><a href="link2">Link 2</a></td>
                            <td class="nowrap">No link here</td>
                        </tr>
                    </table>
                </body>
            </html>
            """
            m.register_uri('GET', self.mock_url, text=html_content)

            response = requests.get(self.mock_url)

            hrefs = extract_hrefs(response)

            expected_hrefs = ["link1", "link2"]
            self.assertEqual(hrefs, expected_hrefs)

    def test_extract_hrefs_with_empty_response(self):
        with requests_mock.Mocker() as m:
            m.register_uri('GET', self.mock_url, text='')

            response = requests.get(self.mock_url)

            hrefs = extract_hrefs(response)

            self.assertEqual(hrefs, [])

    def test_get_last_page_with_valid_element(self):
        html_content = """
        <html>
            <body>
                <div>
                    <a href="http://example.com/search?page=3">Page 3</a>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        last_page_number = get_last_page(soup)

        expected_last_page = 3
        self.assertEqual(last_page_number, expected_last_page)

    def test_get_last_page_with_invalid_element(self):
        html_content = """
        <html>
            <body>
                <div>
                    <p>No link here</p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        last_page_number = get_last_page(soup)

        self.assertEqual(last_page_number, 0)

    def test_get_last_page_with_exception(self):
        html_content = """
        <html>
            <body>
                <div>
                    Invalid Link
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        last_page_number = get_last_page(soup)

        self.assertEqual(last_page_number, 0)

    # modify_url

    def test_modify_url(self):
        input_url = "https://example.com/TEXT?src=0"
        modified_url = modify_url(input_url)

        expected_url = "https://example.com/DATA?tabId=3"
        self.assertEqual(modified_url, expected_url)

    # data_page_exist_in_document

    def test_data_page_exist_in_document_with_data_page(self):
        html_content = """
        <html>
            <body>
                <a class="selected">Data</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        data_page_exists = data_page_exist_in_document(soup)

        self.assertTrue(data_page_exists)

    def test_document_without_data_page(self):
        html_content = """
        <html>
            <body>
                <a class="selected">Other Page</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        data_page_exists = data_page_exist_in_document(soup)

        self.assertFalse(data_page_exists)

    # extract_data_from_table

    def test_extract_data_from_table_with_valid_table(self):
        html_content = """
        <html>
            <body>
                <table class="data">
                    <tbody>
                        <tr>
                            <th>Test-Th</th>
                            <td>Title-Key</td>
                            <td>Title-Value</td>
                        </tr>
                        <tr>
                            <th>Test-Th2</th>
                            <td>Title-Key2</td>
                            <td>Title-Value2</td>
                        </tr>
                        <tr>
                            <th>Test-Th3</th>
                            <td>Title-Key3</td>
                            <td>
                                50830000 - Test
                                <br>
                                98315000 - Test
                                <br>
                                98311000 - Test
                                <br>
                                98300000 - Test
                                <br>
                                98310000 - Test
                            </td>
                        </tr>
                    </tbody>
                </table>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        data_dict = extract_data_from_table(soup)

        expected_data = {
            "Title-Key": "Title-Value",
            "Title-Key2": "Title-Value2",
            "Title-Key3": "50830000 - Test, 98315000 - Test, 98311000 - Test, 98300000 - Test, 98310000 - Test"
        }
        self.assertEqual(data_dict, expected_data)

    # scrape_test_data
    def test_no_data_page_in_document(self):
        response_text = '<html><body>No Data Page</body></html>'
        result = scrape_ted_data(response_text, 'main_page_url')
        self.assertIsNone(result)

    def test_set_url(self):
        html_content = """
                <html>
                    <body>
                        <a class="selected">Data</a>
                    </body>
                </html>
                """
        result = scrape_ted_data(html_content, 'main_page_url')

        expected_result = {
            'URL': 'main_page_url',
        }

        self.assertEqual(result, expected_result)
