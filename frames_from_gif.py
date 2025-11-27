from PIL import Image
from typing import List

from ILI9486.Python_ILI9486.ILI9486 import image_to_data


def load_gif_frames_for_display(path: str,
                                size=(320, 480)) -> List[list]:
    """
    Load a GIF from disk, extract each frame, resize it, and convert
    each frame into the RGB byte array format required by ILI9486.data().

    Returns:
        List of frames, where each frame is a flat list of bytes ready for
        disp.data().
    """

    try:
        gif = Image.open(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"GIF not found: {path}")

    frames = []

    frame_index = 0
    while True:
        try:
            gif.seek(frame_index)
        except EOFError:
            break  # No more frames

        # Convert palette → RGB to avoid issues
        frame = gif.convert("RGB")

        # Resize to match your display
        frame = frame.resize(size, Image.LANCZOS)

        # Convert to byte array with your helper
        frame_bytes = image_to_data(frame)

        frames.append(frame_bytes)
        frame_index += 1

    return frames
