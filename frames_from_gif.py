# frames_from_gif_safe.py

from typing import List
import gif2numpy
from PIL import Image
from ILI9486.Python_ILI9486.ILI9486 import image_to_data


def load_gif_frames_for_display(path: str, size=(320, 480)) -> List[list]:
    """
    Load a GIF from disk, extract each frame safely using gif2numpy,
    resize each frame, and convert it to the RGB byte array format
    required by ILI9486.data().

    Returns:
        List of frames, where each frame is a flat list of bytes
        ready for disp.data().
    """

    try:
        # Convert GIF to numpy arrays (H x W x 3 or 4)
        frames, _ = gif2numpy.convert(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"GIF not found: {path}")
    except Exception as e:
        raise RuntimeError(f"Failed to read GIF: {e}")

    frame_bytes_list = []

    for frame in frames:
        # Convert RGBA → RGB if needed
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]

        # Convert numpy array to Pillow Image for resizing
        img = Image.fromarray(frame).convert("RGB")
        img = img.resize(size, Image.LANCZOS)

        # Convert to byte array for ILI9486
        frame_bytes = image_to_data(img)
        frame_bytes_list.append(frame_bytes)

    return frame_bytes_list
