import json
from typing import List, Dict

OUTPUT_FILE = 'output.json'

STATE_FILE = 'state.json'


def load_data(filename: str) -> List[Dict[str, str]]:
    """
        Load existing data from a JSON file.
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
    """
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def load_state(filename: str) -> Dict:
    """
        Load the application state from a JSON file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as state_file:
            state = json.load(state_file)
        return state
    except FileNotFoundError:
        return {}


def save_state(state: Dict, filename: str) -> None:
    """
        Save the application state to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as state_file:
        json.dump(state, state_file, ensure_ascii=False, indent=4)
