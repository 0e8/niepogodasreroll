import json
import sys
import logging

def load_json_file(filename):
    try:
        with open(filename, encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        logging.error("Error loading %s: %s", filename, error)
        sys.exit()

CONFIG = load_json_file("config.json")
REGIONS = load_json_file("regions.json")
