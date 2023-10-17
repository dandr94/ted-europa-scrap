from prettytable import PrettyTable
from utils import state_file_exists


def default_app_message(text_formatter, entries, last_processed_page, output_status, state_status):
    print(return_default_message_table(text_formatter, entries, last_processed_page, output_status, state_status))

    if state_file_exists():
        print(return_action_message_table())


def get_user_choice_for_action():
    return input('Choose an action: ')


def return_default_message_table(text_formatter, entries, last_processed_page, output_status, state_status):
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


def return_action_message_table():
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
