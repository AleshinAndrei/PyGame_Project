from PIL import Image
from PIL import ImageDraw
from colorsys import hsv_to_rgb

new_image = Image.new('RGB', (50, 50), (0, 0, 0))
draw = ImageDraw.Draw(new_image)
for i in range(50):
    color = tuple(map(lambda x: int(x * 255), hsv_to_rgb(i / 50, 0.3, 0.6)))
    draw.line((i, 0, i, 50), fill=color, width=1)

color = (72, 72, 72)
for i in range(1, 7):
    draw.line((16 * i + 5, -5, -5, i * 16 + 5), fill=color, width=7)
    draw.line((-5, 45 - (16 * i), i * 16 + 5, 55), fill=color, width=7)

for i in range(50):
    if i in {0, 49}:
        len_ = 50
    else:
        len_ = 0
    color = tuple(map(lambda x: int(x * 255), hsv_to_rgb(i / 50, 0.3, 0.6)))
    draw.line((i, 0, i, len_), fill=color, width=1)
    draw.line((i, 49, i, 49), fill=color, width=1)


new_image.save("data/ground.png")
