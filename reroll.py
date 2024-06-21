import time
import logging
import pydirectinput
import keyboard
from config import CONFIG, REGIONS
from ocr import get_quest_chest_count

DELAY = CONFIG["delay"]
START_KEYBIND = CONFIG["start_keybind"]
KILL_KEYBIND = CONFIG["kill_keybind"]

RUNNING = True

def perform_reroll(quest_number):
    coordinates = REGIONS["buttons"].get(f"reroll{quest_number}")
    if not coordinates:
        return

    x_coord, y_coord = coordinates
    pydirectinput.moveTo(x_coord, y_coord)
    pydirectinput.moveTo(x_coord + 1, y_coord + 1)
    pydirectinput.click()

    logging.info("Rerolling chest %d... Waiting for contents to refresh...", quest_number)

def main_reroll_loop():
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