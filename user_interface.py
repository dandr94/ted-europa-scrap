from prettytable import PrettyTable
from utils import state_file_exists, time_left_until_all_data_is_fetched, get_current_time, TextFormatter


class MessageProvider:
    """
    A class that provides a collection of static methods for generating messages and notifications and other
    messages. These messages are designed for use in logging, reporting, or displaying information to users during
    the execution of a data scraping process.
    """

    # Success
    @staticmethod
    def message_update_has_reach_last_scrapped_url() -> str:
        return 'Data successfully updated.'

    @staticmethod
    def message_work_in_progress(page: int, last_page_number: int, current_url: str) -> str:
        return f'Working on URL on page {page}/{last_page_number}: {current_url}...'

    @staticmethod
    def message_successfully_scrapped_data(page: int, data_url: str) -> str:
        return f'Successfully fetched data on page {page} from URL {data_url}'

    @staticmethod
    def message_successful_data_save(filename: str) -> str:
        return f'Data saved successfully to {filename}!'

    @staticmethod
    def message_url_is_scrapped(page: int, document_main_url: str) -> str:
        return f'Continuing to next URL on page {page}, because this one is already scrapped: {document_main_url}'

    # Fail
    @staticmethod
    def message_no_data_page(page: int, document_main_url: str) -> str:
        return f'Impossible to fetch data from URL: {document_main_url} on page {page} because it does not have a data page'

    @staticmethod
    def message_failed_to_retrieve_last_page() -> str:
        return 'Failed to retrieve last page...stopping the process'

    @staticmethod
    def message_failed_to_retrieve_page(page: int, status_code: int) -> str:
        return f'Failed to retrieve page {page}! Status code: {status_code}'

    @staticmethod
    def message_failed_to_retrieve_url(search_url: str) -> str:
        return f'Failed to retrieve the URL "{search_url}".'

    @staticmethod
    def message_unexpected_error_occurred(exception: Exception) -> str:
        return f"An unexpected error occurred - {str(exception)}"

    # Other
    @staticmethod
    def message_interrupted_by_user() -> str:
        return "Process interrupted by user. Saving data collected so far."

    @staticmethod
    def message_eta(documents_left: int) -> str:
        return f'Time left until all data is fetched: ~{time_left_until_all_data_is_fetched(documents_left)}'

    @staticmethod
    def construct_message_with_time_stamp(message: str) -> str:
        return f'[{get_current_time()}] - {message}'

    @staticmethod
    def default_app_message(text_formatter: TextFormatter,
                            entries: int,
                            last_processed_page: int,
                            output_status: bool,
                            state_status: bool) -> None:
        print(return_default_message_table(text_formatter, entries, last_processed_page, output_status, state_status))

        if state_file_exists():
            print(return_action_message_table())


def get_user_choice_for_action() -> str:
    return input('Choose an action: ')


def return_default_message_table(text_formatter: TextFormatter, entries: int, last_processed_page: int,
                                 output_status: bool, state_status: bool) -> PrettyTable:
    """
        Returns a PrettyTable object with information about data files and their existence.
    """
    table = PrettyTable()

    table.title = "Welcome to Ted-Europa data scrapper!"
    table.field_names = ["File", 'Status']

    separator = ["-" * len(table.title)] * len(table.field_names)

    table.add_row([text_formatter.format_custom_message(f"output.json (entries: {entries})", "yellow"),
                   text_formatter.format_message_success(
                       'Exist') if output_status else text_formatter.format_message_fail("Doesn't exist")])
    table.add_row(separator)
    table.add_row(
        [text_formatter.format_custom_message(f"state.json (last processed page {last_processed_page})", "yellow"),
         text_formatter.format_message_success(
             'Exist') if state_status else text_formatter.format_message_fail("Doesn't exist")])

    return table


def return_action_message_table() -> PrettyTable:
    """
        Returns a PrettyTable object with available actions.
    """
    table = PrettyTable()

    table.title = "Actions (type 1,2..etc):"
    table.field_names = ["Action", 'Info']

    separator = ["-" * len(table.title)] * len(table.field_names)

    table.add_row(['1. Continue', 'Continue fetching data from last processed page'])

    table.add_row(separator)
    table.add_row(['2. Update',
                   'Updates the already existing data with newest if possible\nuntil it meets an already existing '
                   'data in output.json'])
    return table
