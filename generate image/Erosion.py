#an image link containing text with scattered white pixels (noise) around the characters.
from PIL import Image, ImageDraw, ImageFont
import random

def generate_noisy_text_image(text, font_size, noise_level):
  """Generates an image with text and noise using a default font.

  Args:
    text: The text to be added to the image.
    font_size: The font size.
    noise_level: The level of noise to add (0-1).

  Returns:
    The generated image.
  """

  # Create a new image
  img = Image.new('RGB', (400, 100), (0, 0, 0)) 

  # Create a drawing context
  draw = ImageDraw.Draw(img)

  # Use a default font
  font = ImageFont.load_default() 

  # Get text size using getmask().getbbox() (corrected line)
  text_width, text_height = font.getmask(text).getbbox()[2:]  

  # Draw the text 
  x = (img.width - text_width) / 2
  y = (img.height - text_height) / 2
  draw.text((x, y), text, font=font, fill=(255, 255, 255))

  # Add noise 
  pixels = img.load()
  for i in range(img.width):
    for j in range(img.height):
      if random.random() < noise_level:
        pixels[i, j] = (255, 255, 255)

  return img

# Example usage (same as before)
text = "This is a noisy text"
font_size = 36  # You might need to adjust this for the default font
noise_level = 0.1 

img = generate_noisy_text_image(text, font_size, noise_level)
img.show() 
img.save("noisy_text.png")