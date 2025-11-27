from flask import Flask, current_app, request
import time

from PIL import Image, ImageDraw, ImageFont

import Python_ILI9486 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from requests import get
from io import BytesIO
from PIL import Image
import time
from frames_from_gif import load_gif_frames_for_display

app = Flask(__name__)

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


@app.get("/")
def get_message():
    pass


@app.post("/")
def post_message():
    data = request.json

    url = data.get("url", None)

    if url is None:
        return {"message": "URL error"}, 400

    frames = load_gif_frames_for_display("feddy.gif")

    for f in frames:
        disp.send(f)
        time.sleep(0.01)


if __name__ == "__main__":
    frames = load_gif_frames_for_display(path="feddy.gif")

    for f in frames:
        disp.set_window()
        disp.data(f)
        time.sleep(0.01)

    # disp.clear((0, 0, 0))
    # disp.display()
    # app.config['TESTING'] = False
    # app.config['DEBUG'] = False
    # app.run(debug=True, host=RUNNING_IP, port=5000)
