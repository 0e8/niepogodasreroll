"""
This script handles the rerolling of chests for quests using OCR and simulated input actions.
"""

import re
import time
import threading
import json
import os
import logging
import sys
from PIL import ImageGrab
import pytesseract
import pydirectinput
import keyboard
import cv2

# Setup logging
LOG_FILENAME = "latest.log"
if os.path.exists(LOG_FILENAME):
    os.remove(LOG_FILENAME)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(LOG_FILENAME)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

# Load configuration
def load_json_file(filename):
    try:
        with open(filename, encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        logging.error("Error loading %s: %s", filename, error)
        sys.exit()

CONFIG = load_json_file("config.json")
REGIONS = load_json_file("regions.json")

DELAY = CONFIG["delay"]
START_KEYBIND = CONFIG["start_keybind"]
KILL_KEYBIND = CONFIG["kill_keybind"]

logging.info("Config and regions loaded successfully")

RUNNING = True

def get_quest_chest_count(quest_number):
    """
    Get the number of chests in a quest by performing OCR on the specified region.
    """
    bbox = REGIONS["regions"].get(f"quest{quest_number}")
    if not bbox:
        return ["0"]

    filename = f'quest{quest_number}.png'
    ImageGrab.grab(bbox=bbox).save(filename)

    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    cv2.imwrite(filename, thresh)

    try:
        ocr_result = pytesseract.image_to_string(thresh)
        chest_type = CONFIG["chest_type"].get(f"quest{quest_number}", "")
        filtered = [re.search(r'(\d+)', item).group(1) for item in ocr_result.split('\n') if chest_type.lower() in item.lower()]
    except Exception as error:
        logging.error("Error reading quest %d content: %s", quest_number, error)
        filtered = ["0"]

    return filtered or ["0"]

def perform_reroll(quest_number):
    """
    Perform the reroll action by clicking on the specified coordinates.
    """
    coordinates = REGIONS["buttons"].get(f"reroll{quest_number}")
    if not coordinates:
        return

    x_coord, y_coord = coordinates
    pydirectinput.moveTo(x_coord, y_coord)
    pydirectinput.moveTo(x_coord + 1, y_coord + 1)
    pydirectinput.click()

    logging.info("Rerolling chest %d... Waiting for contents to refresh...", quest_number)

def main_reroll_loop():
    """
    Main loop to start rerolling based on the start keybind.
    """
    global RUNNING
    logging.info("Script loaded! Press %s to start rerolling. Press %s to exit.", START_KEYBIND, KILL_KEYBIND)
    while RUNNING:
        time.sleep(0.001)
        if keyboard.is_pressed(START_KEYBIND):
            time.sleep(0.2)
            for quest_number in range(1, 5):
                if not REGIONS["regions"].get(f"quest{quest_number}"):
                    if quest_number == 4:
                        logging.info("No fourth Quest Selected")
                    else:
                        logging.info("Quest %d region not defined. Skipping.", quest_number)
                    continue

                while True:
                    chest_counts = get_quest_chest_count(quest_number)
                    if quest_number == 4 and chest_counts[0] == "0":
                        logging.info("No text detected for quest 4, stopping reroll attempts.")
                        break
                    if quest_number == 4 and not any(c.isdigit() for c in chest_counts[0]):
                        logging.info("No text detected at all for quest 4, stopping reroll attempts.")
                        break
                    if not chest_counts[0].isdigit():
                        break
                    chest_count = int(chest_counts[0])
                    if chest_count >= CONFIG["minimum_chests"][f"quest{quest_number}"]:
                        logging.info("Quest %d has enough chests: %d", quest_number, chest_count)
                        break
                    perform_reroll(quest_number)
                    time.sleep(DELAY)

def start_killswitch_listener():
    """
    Function to handle the termination of the script using a specified keybind.
    """
    global RUNNING
    keyboard.wait(KILL_KEYBIND)
    RUNNING = False
    cleanup_temporary_files()
    os._exit(0)

def cleanup_temporary_files():
    """
    Clean up temporary files before exiting.
    """
    logging.info("Cleaning up temporary files...")
    for quest_number in range(1, 5):
        try:
            os.remove(f"quest{quest_number}.png")
        except FileNotFoundError:
            continue
    logging.info("Exiting...")

if __name__ == "__main__":
    time.sleep(1)
    logging.info(" > niepogoda's reroll script < ")

    main_thread = threading.Thread(target=main_reroll_loop)
    main_thread.daemon = True
    main_thread.start()

    start_killswitch_listener()
