def print_last_processed_page_message(last_processed_page):
    print(f"Last processed page: {last_processed_page}")
    print('You can processed from the last processed page and update your data from that page to the end.')
    print(
        'If you choose (n) it will start from page 1 and it will update your existing data until it meets an '
        'already visited url ')
    print(
        'If you want to start from page 1 and scrape all the data again, you need to delete the output.json and '
        'state.json')


def get_user_choice_for_last_processed_page():
    return input("Do you want to start from the last processed page? (y/n): ").strip().lower()
