from PIL import Image
from PIL import ImageDraw
from colorsys import hsv_to_rgb

new_image = Image.new('RGB', (50, 50), (0, 0, 0))
draw = ImageDraw.Draw(new_image)
for i in range(50):
    color = tuple(map(lambda x: int(x * 255), hsv_to_rgb(i / 50, 0.4, 0.85)))
    draw.line((i, 0, i, 50), fill=color, width=1)

# 6 кирпичей
color = (0, 0, 0)
for i in range(5):
    for j in range(3):
        if i % 2 == 0:
            draw.rectangle([j * 25, i * 10 + 1, j * 25 + 23, i * 10 + 9], fill=color)
        else:
            draw.rectangle([j * 25 - 12, i * 10 + 1, j * 25 + 11, i * 10 + 9], fill=color)

new_image.save('wall.png', 'PNG')
