from pathlib import Path
from PIL import Image, ImageDraw

SIZE = 1024
BG = (255, 250, 240, 255)
BLACK = (41, 41, 41, 255)
ORANGE = (255, 172, 0, 255)

here = Path(__file__).resolve().parent
target = here / "build" / "icon.png"
target.parent.mkdir(parents=True, exist_ok=True)

image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Warm-white app tile. The operating system applies its final icon mask.
draw.rounded_rectangle((18, 18, 1006, 1006), radius=218, fill=BG)

# Four connected SBS brand blocks.
draw.rounded_rectangle((92, 92, 510, 510), radius=94, fill=BLACK)
draw.rounded_rectangle((552, 92, 932, 510), radius=94, fill=ORANGE)
draw.rounded_rectangle((92, 552, 510, 932), radius=94, fill=ORANGE)
draw.rounded_rectangle((552, 552, 932, 932), radius=94, fill=BLACK)

# Interlocking inward curves, matching the supplied mark.
draw.ellipse((370, 370, 654, 654), fill=BG)
draw.ellipse((370, 410, 654, 694), fill=BG)
draw.ellipse((410, 370, 694, 654), fill=BG)

image.save(target, "PNG", optimize=True)
print(f"Generated {target} ({image.size[0]}x{image.size[1]})")
