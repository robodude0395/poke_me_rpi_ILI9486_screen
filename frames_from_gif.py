from PIL import Image, ImageSequence
from typing import List
from ILI9486.Python_ILI9486.ILI9486 import image_to_data


def load_gif_frames_for_display(path: str, size=(320, 480)) -> List[list]:
    """
    Load frames from a GIF file safely using Pillow.
    Returns a list of frames in byte array format ready for ILI9486.
    """
    try:
        img = Image.open(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"GIF not found: {path}")

    frames_bytes = []

    try:
        # Iterate over all frames
        for frame in ImageSequence.Iterator(img):
            frame_rgb = frame.convert("RGB").resize(size, Image.LANCZOS)
            frames_bytes.append(list(image_to_data(frame_rgb)))
    except Exception:
        # If single frame GIF or error, fallback to one frame
        frame_rgb = img.convert("RGB").resize(size, Image.LANCZOS)
        frames_bytes.append(list(image_to_data(frame_rgb)))

    return frames_bytes
