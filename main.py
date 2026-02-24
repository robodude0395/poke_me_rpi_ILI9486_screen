from flask import Flask, current_app, request
import time

from PIL import Image, ImageDraw, ImageFont

import Python_ILI9486 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from messages import Messages, get_message_line_count

app = Flask(__name__)

message_board = Messages(json_path="messages.json")

#RUNNING IP
RUNNING_IP = "0.0.0.0"

# Display mode: "portrait" or "landscape"
DISPLAY_MODE = "landscape"  # Change to "landscape" for landscape orientation

# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

#Screen config
MAX_CHAR_WIDTH = 18
MAX_CHAR_HEIGHT = 25

# Create TFT LCD display class.
disp = TFT.ILI9486(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

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

print(f"Max chars per line: {MAX_CHAR_WIDTH}, lines per screen: {MAX_CHAR_HEIGHT}")

# Define a function to create rotated text.  Unfortunately PIL doesn't have good
# native support for rotated fonts, but this function can be used to make a
# text image and rotate it so it's easy to paste in the buffer.
def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255), max_width=None, max_height=None):
    """
    Draw rotated text onto an image without clipping descenders.
    Handles all fonts and rotations cleanly.
    Wraps text based on max_width and max_height parameters.
    Returns the total height used for the text block.
    """
    # Use provided parameters or fall back to global values
    if max_width is None:
        max_width = MAX_CHAR_WIDTH
    if max_height is None:
        max_height = MAX_CHAR_HEIGHT

    # Wrap text based on max_width
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())

    # Limit to max_height lines
    lines = lines[:max_height]

    # Draw each line
    total_height = 0
    x_offset, y_offset = position

    for line_idx, line in enumerate(lines):
        # Create a temporary draw object
        draw = ImageDraw.Draw(image)

        # Get text bounding box with offsets
        bbox = draw.textbbox((0, 0), line, font=font)
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
        text_draw.text((pad_x - bbox[0], pad_y - bbox[1]), line, font=font, fill=fill)

        # Rotate text
        rotated = text_img.rotate(angle, expand=True)

        # Paste into main image (mask keeps transparency)
        y_pos = y_offset + (line_idx * (height + 3))
        image.paste(rotated, (x_offset, y_pos), rotated)

        total_height += height + 3

    return total_height

def render_messages(display_mode="portrait"):
    """
    Render messages in the specified display mode.
    display_mode: "portrait" or "landscape"
    """
    disp.clear((0, 0, 0))
    x, y = 0, 0

    if display_mode == "landscape":
        # Landscape mode: rotated 270 degrees
        # Screen is rotated, so we draw columns from right to left
        # Text flows downward on the screen
        # Constraints are swapped: max_width uses MAX_CHAR_HEIGHT, max_height uses MAX_CHAR_WIDTH

        x = SCREEN_HEIGHT - char_height * 2  # Start from right side

        for msg in message_board.get_messages():
            message_string = msg['message']
            y = char_height  # Start from top, draw downward

            # Draw "From:" label in yellow (rotated 270)
            height = draw_rotated_text(disp.buffer, f"From:", (x, y), 270, font, fill=(255,255,0), max_width=MAX_CHAR_HEIGHT, max_height=MAX_CHAR_WIDTH)
            y += 60

            # Draw sender name in white (rotated 270)
            height = draw_rotated_text(disp.buffer, f"{msg['from']}", (x, y), 270, font, fill=(255,255,255), max_width=MAX_CHAR_HEIGHT, max_height=MAX_CHAR_WIDTH)
            y -= 60
            y += height + 10
            x -= height + 5

            # Draw message text in white (rotated 270) with text wrapping
            height = draw_rotated_text(disp.buffer, message_string, (x, y), 270, font, fill=(255,255,255), max_width=MAX_CHAR_HEIGHT, max_height=MAX_CHAR_WIDTH)
            y += height

            # Move to next column (move left since we start from right)
            x -= char_height * 4

            # Stop if we run out of horizontal space
            if x < char_height * 2:
                break
    else:
        # Portrait mode: vertical orientation
        for msg in message_board.get_messages():
            message_string = msg['message']
            draw_rotated_text(disp.buffer, f"From:", (x, y), 0, font, fill=(255,255,0), max_width=MAX_CHAR_WIDTH, max_height=MAX_CHAR_HEIGHT)
            x = char_width*6
            draw_rotated_text(disp.buffer, f"{msg['from']}", (x, y), 0, font, fill=(255,255,255), max_width=MAX_CHAR_WIDTH, max_height=MAX_CHAR_HEIGHT)
            x = 0
            y += char_height + 3
            draw_rotated_text(disp.buffer, message_string, (x, y), 0, font, fill=(255,255,255), max_width=MAX_CHAR_WIDTH, max_height=MAX_CHAR_HEIGHT)
            y += char_height * get_message_line_count(message_string)

    disp.display()

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
        #print update and display message board
        message_board.push_message(data)
        render_messages(DISPLAY_MODE)

    return data, 200

if __name__ == "__main__":
    render_messages(DISPLAY_MODE)
    app.config['TESTING'] = False
    app.config['DEBUG'] = False
    app.run(debug=True, host=RUNNING_IP, port=5000)
