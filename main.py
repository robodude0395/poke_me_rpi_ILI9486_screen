from flask import Flask, current_app, request
import time

from PIL import Image, ImageDraw, ImageFont

import Python_ILI9486 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from messages import Messages, get_message_line_count

app = Flask(__name__)

message_board = Messages(json_path="messages.json")

# IMAGE DISPLAY BRANCH

# RUNNING IP
RUNNING_IP = "0.0.0.0"

# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

# Screen config
MAX_CHAR_WIDTH = 18
MAX_CHAR_HEIGHT = 25

# Create TFT LCD display class.
disp = TFT.ILI9486(DC, rst=RST, spi=SPI.SpiDev(
    SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

# Initialize display
disp.begin()
disp.clear((0, 0, 0))

# Get screen dimensions (portrait mode)
SCREEN_WIDTH, SCREEN_HEIGHT = disp.width, disp.height

# Load your font
font = ImageFont.truetype('fonts/monocraft.ttf', 18)

# Measure the widest character (usually “W”)
tmp_img = Image.new("RGB", (100, 100))
tmp_draw = ImageDraw.Draw(tmp_img)
bbox = tmp_draw.textbbox((0, 0), "W", font=font)
char_width = (bbox[2] - bbox[0])
char_height = bbox[3] - bbox[1]

# Compute how many fit
MAX_CHAR_WIDTH = SCREEN_WIDTH // char_width
MAX_CHAR_HEIGHT = SCREEN_HEIGHT // char_height

print(
    f"Max chars per line: {MAX_CHAR_WIDTH}, lines per screen: {MAX_CHAR_HEIGHT}")

# Define a function to create rotated text.  Unfortunately PIL doesn't have good
# native support for rotated fonts, but this function can be used to make a
# text image and rotate it so it's easy to paste in the buffer.


def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    """
    Draw rotated text onto an image without clipping descenders.
    Handles all fonts and rotations cleanly.
    """
    # Create a temporary draw object
    draw = ImageDraw.Draw(image)

    # Get text bounding box with offsets
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    # Add padding to prevent clipping of descenders/ascenders
    pad_x, pad_y = 4, 6
    text_w = width + pad_x * 2
    text_h = height + pad_y * 2

    # Create transparent RGBA image for text
    text_img = Image.new("RGBA", (text_w, text_h), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)

    # Draw text centered with padding
    text_draw.text((pad_x - bbox[0], pad_y - bbox[1]),
                   text, font=font, fill=fill)

    # Rotate text
    rotated = text_img.rotate(angle, expand=True)

    # Paste into main image (mask keeps transparency)
    image.paste(rotated, position, rotated)


def validate_data(data: dict):
    if isinstance(data, dict) and all([isinstance(v, str) for v in data.values()]) and "from" in data and "message" in data:
        return data, 200

    return {"error": True, "message": "Invalid message content"}, 403


@app.get("/messages")
def get_message():
    return message_board.get_messages()


@app.post("/messages")
def post_message():
    data = request.json

    data, status_code = validate_data(data)

    if status_code == 200:
        # print update and display message board
        message_board.push_message(data)
        disp.clear((0, 0, 0))

        x, y = 0, 0

        for msg in message_board.get_messages():
            message_string = msg['message']
            draw_rotated_text(disp.buffer, f"From:", (x, y),
                              0, font, fill=(255, 255, 0))
            x = char_width*6
            draw_rotated_text(
                disp.buffer, f"{msg['from']}", (x, y), 0, font, fill=(255, 255, 255))
            x = 0
            y += char_height + 3
            draw_rotated_text(disp.buffer, message_string,
                              (x, y), 0, font, fill=(255, 255, 255))
            y += char_height * get_message_line_count(message_string)

        disp.display()

    return data, 200


if __name__ == "__main__":
    disp.clear((0, 0, 0))
    x, y = 0, 0
    for msg in message_board.get_messages():
        message_string = msg['message']
        draw_rotated_text(disp.buffer, f"From:", (x, y),
                          0, font, fill=(255, 255, 0))
        x = char_width*6
        draw_rotated_text(
            disp.buffer, f"{msg['from']}", (x, y), 0, font, fill=(255, 255, 255))
        x = 0
        y += char_height + 3
        draw_rotated_text(disp.buffer, message_string,
                          (x, y), 0, font, fill=(255, 255, 255))
        y += char_height * get_message_line_count(message_string)
    disp.display()
    app.config['TESTING'] = False
    app.config['DEBUG'] = False
    app.run(debug=True, host=RUNNING_IP, port=5000)
