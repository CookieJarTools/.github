"""The organisation banner, with a light running along the shelf.

The background and the words never change between frames, so the only thing an encoder has to
store per frame is the tile that is lit, which keeps the file small and keeps the gradient from
banding.
"""

import io
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1000, 520
FRAMES = 40
MS = 70

BOLD = "C:/Windows/Fonts/segoeuib.ttf"
BOOK = "C:/Windows/Fonts/segoeui.ttf"

BG = (10, 11, 14)
ACCENT = (216, 169, 63)

TOOLS = [
    ("BB", (216, 169, 63), "Bakers Belt"),
    ("CK", (63, 169, 160), "CookBook"),
    ("CT", (127, 139, 214), "Crumb Trail"),
    ("ET", (224, 163, 63), "Editor Toast"),
    ("CB", (201, 121, 79), "Crumb Baker"),
    ("TR", (94, 106, 210), "CrumbTree"),
    ("GB", (76, 183, 130), "GameBridge"),
]

START_X, START_Y = 520, 92
CARD_W, CARD_H = 208, 62
GAP_X, GAP_Y = 16, 26


def card_box(i):
    col, row = i % 2, i // 2
    x = START_X + col * (CARD_W + GAP_X)
    y = START_Y + row * (CARD_H + GAP_Y)
    return x, y, x + CARD_W, y + CARD_H


def glow(size, box, colour, strength, blur):
    """A soft pool of light, drawn big and blurred so it has no edge."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius=16, fill=colour + (strength,))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def base():
    img = Image.new("RGB", (W, H), BG)

    # the warm wash behind the shelf
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(wash).ellipse([430, -130, 1270, 650], fill=ACCENT + (34,))
    img = Image.alpha_composite(img.convert("RGBA"), wash.filter(ImageFilter.GaussianBlur(120)))

    # the faintest grid, for texture rather than for reading
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(grid)
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 8))
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 8))
    img = Image.alpha_composite(img, grid)

    d = ImageDraw.Draw(img)
    mark = ImageFont.truetype(BOLD, 28)
    name = ImageFont.truetype(BOLD, 53)
    tag = ImageFont.truetype(BOOK, 18)
    pill = ImageFont.truetype(BOLD, 16)

    # the jar
    d.rounded_rectangle([64, 92, 124, 152], radius=17, fill=ACCENT + (235,))
    d.text((94, 122), "CJ", font=mark, fill=(255, 255, 255), anchor="mm")

    d.text((60, 184), "CookieJar", font=name, fill=(242, 243, 245))
    d.text((60, 240), "Tools", font=name, fill=ACCENT)

    d.text((64, 312), "Editor tools for Unity, and the odd", font=tag, fill=(148, 154, 166))
    d.text((64, 336), "desktop app, built while making games.", font=tag, fill=(148, 154, 166))

    words = "Free for commercial use"
    width = int(d.textlength(words, font=pill)) + 44
    d.rounded_rectangle([64, 382, 64 + width, 416], radius=8, fill=ACCENT)
    d.text((86, 391), words, font=pill, fill=(26, 20, 5))

    return img.convert("RGB")


def shelf(img, lit, strength):
    """Draws the seven tiles. `lit` is the one the light is passing over."""
    chip_font = ImageFont.truetype(BOLD, 20)
    name_font = ImageFont.truetype(BOLD, 15)

    for i, (mark, colour, title) in enumerate(TOOLS):
        x0, y0, x1, y1 = card_box(i)
        up = strength if i == lit else 0.0

        if up > 0:
            img.paste(
                Image.alpha_composite(
                    img.crop((x0 - 40, y0 - 40, x1 + 40, y1 + 40)).convert("RGBA"),
                    glow((x1 - x0 + 80, y1 - y0 + 80), [40, 40, x1 - x0 + 40, y1 - y0 + 40],
                         colour, int(165 * up), 30),
                ).convert("RGB"),
                (x0 - 40, y0 - 40),
            )

        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        edge = tuple(int(255 + (c - 255) * up) for c in colour)
        d.rounded_rectangle([x0, y0, x1, y1], radius=10,
                            fill=(255, 255, 255, 10 + int(30 * up)),
                            outline=edge + (26 + int(200 * up),), width=1 + int(round(up)))
        d.rounded_rectangle([x0 + 12, y0 + 13, x0 + 48, y0 + 49], radius=10,
                            fill=colour + (235,))
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))

        d = ImageDraw.Draw(img)
        d.text((x0 + 30, y0 + 31), mark, font=chip_font, fill=(255, 255, 255), anchor="mm")
        bright = int(227 + 28 * up)
        d.text((x0 + 60, y0 + 31), title, font=name_font,
               fill=(min(bright, 255), min(bright + 3, 255), min(bright + 10, 255)), anchor="lm")

    return img


def frames():
    ground = base()
    out = []
    for f in range(FRAMES):
        # the light steps from tile to tile, then rests before it starts again
        t = f / FRAMES
        run = 0.78
        lit, strength = -1, 0.0
        if t < run:
            place = (t / run) * len(TOOLS)
            lit = int(place)
            within = place - lit
            strength = math.sin(within * math.pi) ** 0.7
        out.append(shelf(ground.copy(), lit, strength))
    return out


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    made = frames()
    made[0].save(os.path.join(here, "banner.png"))
    made[0].save(
        os.path.join(here, "banner.gif"),
        save_all=True, append_images=made[1:], duration=MS, loop=0,
        optimize=True, disposal=2,
    )
    made[0].save(
        os.path.join(here, "banner-apng.png"),
        save_all=True, append_images=made[1:], duration=MS, loop=0,
    )
    for name in ("banner.gif", "banner-apng.png"):
        p = os.path.join(here, name)
        print("%-18s %8.1f KB" % (name, os.path.getsize(p) / 1024))
