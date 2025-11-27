from typing import List
import imageio.v2 as imageio
from PIL import Image

from ILI9486.Python_ILI9486.ILI9486 import image_to_data


def load_gif_frames_for_display(path: str,
                                size=(320, 480)) -> List[list]:
    """
    Load a GIF from disk using imageio (safer on Raspberry Pi),
    extract each frame, resize it with Pillow, and convert each frame
    into the RGB byte array format required by ILI9486.data().

    Returns:
        List of frames, where each frame is a flat list of bytes ready for disp.data().
    """

    try:
        reader = imageio.get_reader(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"GIF not found: {path}")

    frames = []

    for frame in reader:
        # frame arrives as a numpy array → convert to Pillow Image
        img = Image.fromarray(frame).convert("RGB")

        # Resize for your display
        img = img.resize(size, Image.LANCZOS)

        # Convert to byte array for the ILI9486 driver
        frame_bytes = image_to_data(img)

        frames.append(frame_bytes)

    return frames
