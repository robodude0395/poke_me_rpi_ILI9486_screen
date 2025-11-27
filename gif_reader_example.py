from PIL import Image

# Open the GIF
gif = Image.open("feddy.gif")

# Print GIF info
print(f"Format: {gif.format}, Size: {gif.size}, Frames: {gif.n_frames}")

# Iterate through frames
for frame_number in range(gif.n_frames):
    gif.seek(frame_number)  # Move to the frame
    frame = gif.copy()      # Copy the frame
    frame.save(f"frame_{frame_number}.png")  # Optional: save as PNG
