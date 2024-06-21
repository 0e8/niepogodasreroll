import re
import logging
from PIL import ImageGrab
import pytesseract
import cv2
from config import REGIONS, CONFIG

def get_quest_chest_count(quest_number):
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
