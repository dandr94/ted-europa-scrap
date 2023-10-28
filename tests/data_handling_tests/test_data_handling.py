import json
import os
import unittest

from data_handling import load_data, save_data, load_state, save_state


class DataHandlingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_data = [{"key1": "value1"}, {"key2": "value2"}]
        self.test_state = {"key1": "value1", "key2": "value2"}
        self.output_file = 'test_output.json'
        self.state_file = 'test_state.json'

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        if os.path.exists("test_state.json"):
            os.remove("test_state.json")

    # load_data

    def test_load_data_successful(self):
        with open(self.output_file, "w", encoding="utf-8") as test_file:
            json.dump(self.test_data, test_file, ensure_ascii=False)

        loaded_data = load_data(self.output_file)
        self.assertEqual(loaded_data, self.test_data)

    def test_load_data_file_not_found(self):
        loaded_data = load_data(self.output_file)

        self.assertEqual(loaded_data, [])

    # save_data

    def test_save_data_successful(self):
        save_data(self.test_data, self.output_file)

        self.assertTrue(os.path.exists(self.output_file))

        with open(self.output_file, "r", encoding="utf-8") as json_file:
            saved_data = json.load(json_file)

        self.assertEqual(saved_data, self.test_data)

    # load_state

    def test_load_state_successful(self):
        with open(self.state_file, "w", encoding="utf-8") as state_file:
            json.dump(self.test_state, state_file, ensure_ascii=False)

        loaded_state = load_state(self.state_file)

        self.assertEqual(loaded_state, self.test_state)

    def test_load_state_file_not_found(self):
        loaded_state = load_state(self.state_file)

        self.assertEqual(loaded_state, {})

    # save_state

    def test_save_state_successful(self):
        save_state(self.test_state, self.state_file)

        self.assertTrue(os.path.exists(self.state_file))

        with open(self.state_file, "r", encoding="utf-8") as json_file:
            saved_state = json.load(json_file)

        self.assertEqual(saved_state, self.test_state)
