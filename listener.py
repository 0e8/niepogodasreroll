import os
import logging
import keyboard
from config import CONFIG

RUNNING = True

def cleanup_temporary_files():
    logging.info("Cleaning up temporary files...")
    for quest_number in range(1, 5):
        try:
            os.remove(f"quest{quest_number}.png")
        except FileNotFoundError:
            continue
    logging.info("Exiting...")

def start_killswitch_listener():
    global RUNNING
    keyboard.wait(CONFIG["kill_keybind"])
    RUNNING = False
    cleanup_temporary_files()
    os._exit(0)
