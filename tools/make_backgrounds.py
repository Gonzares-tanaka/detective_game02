"""Generate original, character-free 256x100 pixel backgrounds (Pillow only).

These are replaceable provisional illustrations, not photographs. No characters,
portraits or mannequins are drawn. The statue is an abstract geometric object.
"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from main import PALETTE

COLORS = [f"#{c:06x}" for c in PALETTE]
FONT = ImageFont.truetype(str(ROOT / "assets/PixelMplus12-Regular.ttf"), 12)


class Canvas:
    def __init__(self, fill=0):
        self.image = Image.new("RGB", (256, 100), COLORS[fill])
        self.draw = ImageDraw.Draw(self.image)

    def rect(self, box, fill, outline=None):
        self.draw.rectangle(box, fill=COLORS[fill], outline=COLORS[outline] if outline is not None else None)

    def line(self, xy, fill, width=1):
        self.draw.line(xy, fill=COLORS[fill], width=width)

    def poly(self, points, fill):
        self.draw.polygon(points, fill=COLORS[fill])

    def ellipse(self, box, fill, outline=None):
        self.draw.ellipse(box, fill=COLORS[fill], outline=COLORS[outline] if outline is not None else None)

    def text(self, x, y, label, color=4):
        self.draw.text((x, y), label, font=FONT, fill=COLORS[color])

    def room(self, wall=8, floor=9):
        self.rect((0, 0, 255, 67), wall)
        self.rect((0, 68, 255, 99), floor)
        self.line((0, 67, 255, 67), 3)
        for x in range(-60, 310, 38):
            self.line((128, 64, x, 100), 8)
        self.line((0, 83, 255, 83), 8)

    def window(self, x, y, w, h):
        self.rect((x, y, x+w, y+h), 0, 3)
        for bx in range(x+5, x+w-5, 12):
            top = y + 8 + (bx * 7 % max(1, h-18))
            self.rect((bx, top, bx+8, y+h-3), 7)
            for by in range(top+3, y+h-4, 8):
                self.rect((bx+2, by, bx+3, by+2), 10)
        self.line((x+w//2, y, x+w//2, y+h), 3)

    def plant(self, x, y):
        self.rect((x-5, y-10, x+5, y), 10)
        self.line((x, y-10, x, y-36), 5, 2)
        for dx, dy in [(-8, -29), (8, -24), (-6, -18), (5, -35)]:
            self.ellipse((x+min(0, dx)-3, y+dy-4, x+max(0, dx)+3, y+dy+2), 5)

    def save(self, name):
        target = ROOT / "assets/backgrounds" / f"{name}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(target)
        return self.image


def office():
    c = Canvas(); c.room()
    c.window(9, 8, 46, 48)
    c.rect((75, 5, 199, 53), 2)
    c.rect((78, 8, 196, 49), 11)
    c.rect((82, 11, 192, 46), 4)
    c.rect((73, 3, 201, 6), 0)
    c.line((138, 54, 138, 62), 10)
    c.rect((137, 60, 140, 62), 3)
    # The screen is blank. Deliberately no projector anywhere in this room.
    c.rect((51, 70, 206, 80), 9, 10)
    c.rect((58, 81, 64, 99), 8); c.rect((193, 81, 199, 99), 8)
    c.rect((81, 64, 119, 69), 4); c.line((85, 65, 112, 65), 2)
    c.ellipse((157, 62, 170, 70), 0); c.rect((159, 58, 168, 67), 4)
    c.rect((221, 11, 248, 59), 9, 10)
    for y in (25, 41, 55):
        c.line((221, y, 248, y), 10)
    for x in range(225, 246, 5):
        c.rect((x, 15, x+2, 23), 13)
    c.plant(21, 92)
    return c


def bath():
    c = Canvas(); c.room(14, 13)
    for x in range(0, 256, 16): c.line((x, 0, x, 67), 13)
    for y in range(0, 68, 16): c.line((0, y, 255, y), 13)
    c.rect((18, 10, 73, 48), 7, 4)
    c.rect((21, 13, 70, 45), 14)
    c.line((166, 66, 166, 18, 194, 18), 4, 3)
    c.ellipse((184, 17, 206, 21), 2)
    for x in range(188, 204, 5):
        for y in range(28, 67, 12): c.line((x, y, x, y+4), 14)
    c.ellipse((162, 78, 190, 86), 0, 2)
    for x in range(168, 188, 4): c.line((x, 80, x, 84), 2)
    c.rect((95, 49, 105, 64), 4); c.rect((98, 44, 102, 49), 3)
    return c


def street():
    c = Canvas(13)
    for x, w, top in [(0, 42, 17), (45, 56, 4), (108, 42, 23), (155, 58, 11), (218, 38, 0)]:
        c.rect((x, top, x+w, 75), 8, 7)
        for wx in range(x+5, x+w-5, 12):
            for wy in range(top+6, 66, 14): c.rect((wx, wy, wx+5, wy+7), 10)
    c.rect((0, 74, 255, 83), 2)
    c.rect((0, 84, 255, 99), 0)
    for x in range(0, 256, 45): c.rect((x, 91, x+23, 92), 11)
    c.rect((172, 38, 210, 73), 4)
    c.text(173, 46, "SHOP", 0)
    c.plant(22, 80)
    return c


def boutique():
    c = Canvas(); c.room(11, 10)
    c.rect((12, 8, 70, 62), 9, 3); c.rect((17, 13, 65, 57), 14)
    c.line((23, 16, 55, 46), 4, 2)
    c.line((88, 26, 235, 26), 9, 2)
    c.line((88, 26, 88, 68), 9, 2); c.line((235, 26, 235, 68), 9, 2)
    for x, color in [(109, 5), (142, 4), (175, 6), (208, 13)]:
        c.line((x, 26, x, 31), 9)
        c.poly([(x, 30), (x-12, 37), (x+12, 37)], 9)
        c.poly([(x-6, 34), (x-15, 39), (x-11, 47), (x-7, 44), (x-8, 59),
                (x+8, 59), (x+7, 44), (x+11, 47), (x+15, 39), (x+6, 34)], color)
        c.line((x, 39, x, 57), 10)
    c.rect((25, 74, 107, 86), 9, 4); c.rect((32, 86, 38, 98), 9); c.rect((95, 86, 101, 98), 9)
    c.text(95, 6, "CLOSET / SELECT", 9)
    return c


def cafe():
    c = Canvas(); c.room(11, 9)
    c.window(10, 7, 80, 49)
    c.rect((108, 7, 245, 30), 0, 3)
    c.text(118, 12, "McDonald's", 3)
    c.rect((112, 38, 243, 58), 6)
    c.rect((121, 64, 243, 73), 10, 11)
    c.rect((130, 74, 137, 99), 8); c.rect((226, 74, 233, 99), 8)
    c.rect((143, 58, 221, 66), 8)
    # Food tray and a free glass of water, no human silhouettes.
    c.rect((150, 50, 162, 61), 14, 4); c.line((151, 55, 161, 55), 4)
    c.ellipse((177, 53, 199, 60), 3); c.rect((178, 59, 198, 62), 9)
    c.rect((33, 68, 86, 92), 6); c.line((32, 67, 87, 67), 3, 2)
    return c


def park():
    c = Canvas(14)
    c.rect((0, 53, 255, 99), 5)
    c.ellipse((196, 9, 214, 27), 11)
    for x in (18, 71, 231):
        c.rect((x, 19, x+4, 75), 9)
        c.ellipse((x-21, 0, x+25, 44), 7)
        c.ellipse((x-15, 0, x+19, 32), 5)
    c.poly([(119, 53), (142, 53), (195, 99), (61, 99)], 10)
    c.rect((109, 55, 191, 70), 9, 10)
    for y in (59, 65): c.line((111, y, 189, y), 3)
    c.rect((104, 72, 196, 77), 9, 10)
    c.rect((112, 78, 116, 91), 0); c.rect((183, 78, 187, 91), 0)
    return c


def metro():
    c = Canvas(); c.room(7, 2)
    c.rect((0, 9, 255, 69), 14, 4)
    c.rect((0, 54, 255, 59), 5)
    for x in (14, 66, 172, 223): c.rect((x, 20, x+31, 44), 1, 4)
    c.rect((108, 13, 160, 68), 11, 2)
    c.line((134, 14, 134, 68), 0, 2)
    c.rect((114, 22, 128, 44), 1, 4); c.rect((141, 22, 155, 44), 1, 4)
    c.rect((0, 73, 255, 78), 3)
    for x in range(0, 256, 7): c.rect((x, 74, x+2, 76), 9)
    c.text(10, 84, "NEXT STATION", 0)
    return c


def taxi():
    c = Canvas(0)
    c.poly([(14, 13), (241, 13), (227, 64), (27, 64)], 13)
    for x in range(23, 237, 24):
        c.rect((x, 25 + x % 13, x+16, 56), 8)
        c.rect((x+5, 31 + x % 13, x+8, 35 + x % 13), 3)
    c.poly([(113, 43), (142, 43), (178, 64), (77, 64)], 7)
    c.line((128, 45, 128, 63), 11)
    c.rect((12, 65, 244, 87), 1, 2)
    c.ellipse((37, 61, 91, 99), 0, 2); c.ellipse((43, 67, 85, 99), 1, 2)
    c.rect((145, 72, 186, 83), 0, 2); c.text(150, 72, "TAXI", 3)
    c.line((195, 74, 231, 74), 2)
    return c


def hotel():
    c = Canvas(); c.room(9, 11)
    c.rect((86, 8, 170, 67), 0, 3)
    c.rect((92, 18, 164, 67), 13, 10)
    c.line((128, 18, 128, 67), 3, 2)
    c.text(98, 4, "SHIGA", 4)
    for x in (21, 65, 188, 230):
        c.rect((x, 7, x+8, 66), 10)
        c.rect((x-3, 5, x+11, 9), 11); c.rect((x-3, 63, x+11, 67), 11)
    c.poly([(113, 68), (144, 68), (174, 99), (82, 99)], 6)
    c.line((111, 70, 86, 99), 3); c.line((146, 70, 170, 99), 3)
    c.line((127, 0, 127, 19), 3)
    c.ellipse((112, 17, 143, 23), 3)
    for x in (114, 124, 134, 142): c.ellipse((x-2, 22, x+2, 27), 4)
    c.plant(39, 86); c.plant(216, 86)
    return c


def cake():
    c = Canvas(); c.room(9, 8)
    c.rect((16, 15, 240, 47), 1, 3); c.text(40, 23, "RED KONJAC / PATISSERIE", 3)
    c.rect((7, 71, 249, 83), 10, 11)
    c.rect((18, 84, 24, 99), 9); c.rect((231, 84, 237, 99), 9)
    c.ellipse((42, 61, 125, 77), 4)
    c.rect((57, 52, 111, 67), 6); c.ellipse((57, 46, 111, 59), 4)
    for x,y in [(64,51),(83,49),(99,52)]: c.rect((x,y,x+5,y+4),6)
    c.rect((171, 43, 183, 69), 5); c.rect((174, 32, 180, 46), 5)
    c.rect((174, 30, 180, 34), 3); c.rect((172, 53, 182, 63), 11)
    c.ellipse((202, 45, 216, 57), 14, 4); c.line((209, 57, 209, 70), 4)
    c.line((204, 70, 214, 70), 4); c.ellipse((204, 51, 214, 56), 6)
    return c


def gallery():
    c = Canvas(); c.room(8, 9)
    for x in (8, 213):
        c.rect((x, 13, x+35, 48), 3); c.rect((x+3, 16, x+32, 45), 0)
        c.poly([(x+6, 40), (x+16, 22), (x+29, 40)], 5)
    c.rect((62, 9, 192, 67), 1, 7)
    c.poly([(119, 8), (136, 8), (172, 67), (83, 67)], 7)
    c.ellipse((92, 78, 166, 91), 8)
    c.rect((104, 59, 152, 86), 10, 11)
    c.rect((100, 57, 156, 62), 11)
    # Logos + sphere: an abstract artwork, never a human-shaped statue.
    c.ellipse((110, 25, 145, 53), 3, 11)
    c.ellipse((115, 28, 140, 49), 9)
    c.poly([(108, 41), (126, 18), (147, 43), (126, 56)], 3)
    c.poly([(122, 24), (127, 20), (142, 41), (135, 46)], 11)
    c.ellipse((121, 32, 135, 46), 0, 3)
    c.rect((118, 52, 138, 57), 3)
    c.rect((115, 69, 142, 78), 1); c.text(117, 68, "光", 4)
    for x in (78, 179):
        c.line((x, 64, x, 89), 3, 2); c.ellipse((x-3, 61, x+3, 66), 3)
    c.line((79, 70, 178, 70), 6)
    return c


def signature():
    c = Canvas(1)
    c.ellipse((31, 3, 229, 96), 3, 11)
    c.ellipse((41, 10, 220, 88), 9, 10)
    c.ellipse((49, 16, 213, 81), 10)
    c.text(83, 41, "KENTO", 0)
    c.line((83, 56, 147, 56), 9)
    c.line((173, 22, 203, 43), 11, 2)
    c.line((177, 20, 207, 41), 11)
    return c


def ceremony():
    c = Canvas(); c.room(6, 9)
    for x in range(0, 256, 12): c.line((x, 0, x, 66), 9, 2)
    c.rect((55, 8, 202, 36), 4, 3); c.text(76, 15, "事件解決 表彰式", 9)
    c.rect((28, 60, 228, 69), 11); c.rect((20, 69, 236, 79), 10)
    c.rect((11, 79, 246, 89), 9)
    # Empty stage, flowers, and the camera waiting in the foreground.
    for x in (29, 225):
        c.rect((x-5, 44, x+5, 59), 3)
        for dx,dy in [(-6,-6),(0,-10),(6,-5)]: c.ellipse((x+dx-4,42+dy-4,x+dx+4,42+dy+4),4)
    c.rect((111, 78, 151, 94), 0, 2); c.rect((119, 74, 132, 78), 2)
    c.ellipse((123, 79, 142, 94), 2); c.ellipse((127, 82, 138, 91), 0)
    c.line((128, 94, 117, 99), 2); c.line((135, 94, 146, 99), 2)
    return c


def build():
    images = []
    for name in ("office", "bath", "street", "boutique", "cafe", "park", "metro", "taxi", "hotel", "cake", "gallery", "signature", "ceremony"):
        images.append((name, globals()[name]().save(name)))
    sheet = Image.new("RGB", (256*3, 122*5), COLORS[0])
    draw = ImageDraw.Draw(sheet)
    for index, (name, picture) in enumerate(images):
        x, y = index % 3 * 256, index // 3 * 122
        sheet.paste(picture, (x, y)); draw.text((x+6, y+103), name, font=FONT, fill=COLORS[4])
    (ROOT / "verification").mkdir(exist_ok=True)
    sheet.save(ROOT / "verification/backgrounds.png")
    print(f"Generated {len(images)} backgrounds, each 256x100; no characters.")


if __name__ == "__main__":
    build()
