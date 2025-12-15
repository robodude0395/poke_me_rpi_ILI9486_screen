from flask import Flask, current_app, request
import time
import threading

from PIL import Image, ImageDraw, ImageFont

import Python_ILI9486 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from requests import get
from io import BytesIO
from PIL import Image
from webscraper import get_links_for_images
import time
from evdev import InputDevice, categorize, ecodes

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

# Measure the widest character (usually "W")
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

# Carousel state
carousel_images = []  # List of PIL Image objects
current_index = 0
carousel_lock = threading.Lock()


def load_image_from_url(url: str):
    """Load and prepare an image from URL, returns PIL Image object."""
    if url is not None:
        try:
            response = get(url)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content))

            # Check orientation
            width, height = image.size
            if width > height:
                # Landscape: rotate so the long edge is horizontal
                image = image.rotate(270, expand=True)

            # Resize after rotation
            new_size = (320, 480)
            image = image.resize(new_size, Image.LANCZOS)

            return image
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            return None
    return None


def display_current_image():
    """Display the current carousel image on the screen."""
    global current_index

    with carousel_lock:
        if carousel_images and 0 <= current_index < len(carousel_images):
            disp.display(carousel_images[current_index])
            print(f"Displaying image {current_index + 1}/{len(carousel_images)}")


def next_image():
    """Move to the next image in the carousel."""
    global current_index

    with carousel_lock:
        if carousel_images:
            current_index = (current_index + 1) % len(carousel_images)
            display_current_image()


def previous_image():
    """Move to the previous image in the carousel."""
    global current_index

    with carousel_lock:
        if carousel_images:
            current_index = (current_index - 1) % len(carousel_images)
            display_current_image()


def find_keyboard_device():
    """Find the keyboard input device."""
    import evdev
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if 'keyboard' in device.name.lower() or 'keys' in device.name.lower():
            print(f"Found keyboard: {device.name} at {device.path}")
            return device.path
    # Fallback to first event device
    if devices:
        print(f"Using default device: {devices[0].name} at {devices[0].path}")
        return devices[0].path
    return None


def keyboard_listener():
    """Listen for physical keyboard input to control the carousel."""
    print("\n=== Carousel Controls ===")
    print("Press Enter: Next image")
    print("Waiting for keyboard input...\n")

    try:
        device_path = find_keyboard_device()
        if not device_path:
            print("No keyboard device found!")
            return

        device = InputDevice(device_path)
        print(f"Listening to: {device.name}")
        print(f"Device path: {device.path}")
        print(f"Device capabilities: {device.capabilities()}")

        # Use grab to get exclusive access
        device.grab()
        print("Device grabbed - listening for events...")

        for event in device.read_loop():
            print(f"!!! EVENT DETECTED !!! type={event.type}, code={event.code}, value={event.value}")

            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                print(f"!!! KEY EVENT !!! {key_event.keycode}, state={key_event.keystate}")

                if key_event.keystate == 1:  # Key press
                    print(f"Key pressed: {key_event.keycode}")
                    next_image()

    except PermissionError:
        print("Permission denied! Run with sudo or add user to 'input' group:")
        print("  sudo usermod -a -G input $USER")
    except Exception as e:
        print(f"Keyboard listener error: {e}")
        import traceback
        traceback.print_exc()

@app.get("/")
def get_message():
    """Get carousel status."""
    with carousel_lock:
        return {
            "total_images": len(carousel_images),
            "current_index": current_index
        }, 200


@app.post("/")
def post_message():
    """Retrieve images from URL and populate carousel."""
    global carousel_images, current_index

    data = request.json

    url = data.get("url", None)

    if url is None:
        return {"message": "URL error"}, 400

    image_links = get_links_for_images(url)

    if not image_links or isinstance(image_links, dict):
        return {"message": "No images found at the provided URL"}, 404

    # Load images into carousel
    loaded_images = []
    for u in image_links:
        print(f"Loading image from: {u}")
        img = load_image_from_url(u)
        if img is not None:
            loaded_images.append(img)

    if not loaded_images:
        return {"message": "Failed to load any images"}, 500

    # Update carousel with new images
    with carousel_lock:
        carousel_images = loaded_images
        current_index = 0

    # Display the first image
    display_current_image()

    return {
        "message": "Images loaded successfully",
        "total_images": len(loaded_images),
        "image_urls": image_links
    }, 200


if __name__ == "__main__":
    disp.clear((0, 0, 0))
    disp.display()

    # Start keyboard listener in a separate thread
    keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
    keyboard_thread.start()

    app.config['TESTING'] = False
    app.config['DEBUG'] = False
    app.run(debug=True, host=RUNNING_IP, port=5000)