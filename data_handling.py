import json
from typing import List, Dict

from utils import get_current_time, TextFormatter

OUTPUT_FILE = 'output.json'

STATE_FILE = 'state.json'

text_formatter = TextFormatter()


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
    print(text_formatter.format_message_success(f'[{get_current_time()}] - Data saved successfully to {filename}!'))


def load_state() -> Dict:
    """
        Load the application state from a JSON file.

        Returns:
            Dict: A dictionary containing the loaded application state.
                An empty dictionary is returned if the file is not found.
    """
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as state_file:
            state = json.load(state_file)
        return state
    except FileNotFoundError:
        return {}


def save_state(state: Dict) -> None:
    """
        Save the application state to a JSON file.

        Args:
            state (Dict): A dictionary containing the application state to be saved.
    """
    with open(STATE_FILE, 'w', encoding='utf-8') as state_file:
        json.dump(state, state_file, ensure_ascii=False, indent=4)
