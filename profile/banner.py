"""The organisation banner: each tool's own UI, taking itself apart as the next one builds.

The left column and the background never change between frames, so the only thing an encoder
has to store per frame is the window on the right and the words beside it. That, and holding
far longer than it moves, is what keeps an animation this long down to a sane file size.

Nothing here is drawn twice. The UI in the window is lifted straight out of each tool's own
banner, and the accent beside it is read off the badge on that same banner, so a tool that
gets restyled only has to be rebuilt here, never re-described.

The panel boxes were read off each banner by eye, then widened or shortened to the window's
own aspect so that fitting one crops nothing. Finding them by brightness was tried and
abandoned: the banners carry a soft wash that a threshold either swallows whole or clips down
to whichever label happens to be the brightest thing on screen.
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1000, 520
MS = 70

# A frame that holds costs an encoder almost nothing, while every frame of a handover redraws
# the whole window. Measured on the real thing: 8 and 6 comes out a third smaller than 6 and 8
# and lengthening the hold is free on top of that, because an encoder keeps one copy of a
# frame that repeats and simply shows it for longer.
HOLD, TRANS = 16, 6
COLOURS = 256

BOLD = "C:/Windows/Fonts/segoeuib.ttf"
BOOK = "C:/Windows/Fonts/segoeui.ttf"

BG = (10, 11, 14)
GOLD = (216, 169, 63)
INK = (242, 243, 245)
MUTE = (148, 154, 166)

WX, WY, WW, WH = 520, 62, 430, 400
BAR = 34
CW, CH = WW, WH - BAR

BANDS = 28
SPAN = 0.40
LAG = 0.30
SLIDE = 26

TOOLS = [
    ("TR", "CrumbTree", "A desktop git client with a clear, vertical commit graph.",
     "Windows", "crumbtree.png", (442, 56, 987, 520)),
    ("GB", "GameBridge", "One launcher for your Unity, Unreal and custom engine projects.",
     "Windows", "F:/Dev/GameBridge/docs/banner.png", (470, 83, 956, 497)),
    ("CK", "CookBook", "Documentation that lives in the editor, so the answer is where the work is.",
     "Unity 6000.0+", "F:/Dev/CookieJar/Assets/CookieJarTools/Cookbook/Documentation~/hero.png",
     (510, 64, 1000, 481)),
    ("BB", "Bakers Belt", "The editor shortcuts you reach for most, on Unity's main toolbar.",
     "Unity 6000.3+", "F:/Dev/CookieJar/Assets/CookieJarTools/BakersBelt/Documentation~/hero.png",
     (520, 62, 1000, 470)),
    ("ET", "Editor Toast", "Says what just finished without stopping what you are doing.",
     "Unity 6000.0+", "F:/Dev/CookieJar/Assets/CookieJarTools/EditorToast/Documentation~/hero.png",
     (427, 66, 897, 466)),
    ("CT", "Crumb Trail", "A to do list inside the editor, so the next job is written down where the work is.",
     "Unity 6000.0+", "F:/Dev/CookieJar/Assets/CookieJarTools/CrumbTrail/Documentation~/hero.png",
     (468, 66, 926, 456)),
    ("SF", "Sifter", "A console worth reading, with every part of a stack trace coloured for what it is.",
     "Unity 6000.0+", "F:/Dev/CookieJar/Assets/CookieJarTools/Sifter/Documentation~/hero.png",
     (516, 42, 985, 478)),
]

HERE = os.path.dirname(os.path.abspath(__file__))

F_WORD = ImageFont.truetype(BOLD, 21)
F_NAME = ImageFont.truetype(BOLD, 44)
F_DESC = ImageFont.truetype(BOOK, 16)
F_PILL = ImageFont.truetype(BOLD, 15)
F_MARK = ImageFont.truetype(BOLD, 13)
F_JAR = ImageFont.truetype(BOLD, 19)


def accent_of(im):
    """
    The tool's accent, taken from the badge in the corner of its own banner.

    The median of the saturated pixels rather than the brightest one, which would land on a
    highlight and come back several shades too light.
    """
    px = im.load()
    picked = []
    for x in range(20, 190, 2):
        for y in range(30, 270, 2):
            r, g, b = px[x, y]
            if max(r, g, b) - min(r, g, b) > 45 and max(r, g, b) > 70:
                picked.append((r, g, b))

    if not picked:
        return GOLD
    picked.sort(key=sum)
    return picked[len(picked) // 2]


def fit(cut):
    """
    Cover the window rather than stretch to it.

    The panels are all a little squarer than the window, and a screenshot that has been
    squashed sideways is the first thing anyone notices.
    """
    scale = max(CW / cut.width, CH / cut.height)
    grown = cut.resize((max(CW, int(cut.width * scale)), max(CH, int(cut.height * scale))),
                       Image.LANCZOS)
    x = (grown.width - CW) // 2
    y = (grown.height - CH) // 2
    return grown.crop((x, y, x + CW, y + CH)).convert("RGBA")


def read(path, box):
    im = Image.open(path if os.path.isabs(path) else os.path.join(HERE, path)).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return fit(im.crop(box)), accent_of(im)


PANELS, ACCENT = {}, {}
for _t in TOOLS:
    PANELS[_t[0]], ACCENT[_t[0]] = read(_t[4], _t[5])


def mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def clamp(v):
    return min(max(v, 0.0), 1.0)


def wrap(text, font, width, draw):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def base():
    """Everything that never moves: the wash, the grid, the jar and the standing pill."""
    img = Image.new("RGB", (W, H), BG)

    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(wash).ellipse([380, -170, 1200, 620], fill=GOLD + (30,))
    img = Image.alpha_composite(img.convert("RGBA"), wash.filter(ImageFilter.GaussianBlur(130)))

    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(grid)
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 8))
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 8))
    img = Image.alpha_composite(img, grid).convert("RGB")

    d = ImageDraw.Draw(img)
    d.rounded_rectangle([64, 48, 104, 88], radius=12, fill=GOLD)
    d.text((84, 68), "CJ", font=F_JAR, fill=(255, 255, 255), anchor="mm")
    d.text((116, 58), "CookieJar", font=F_WORD, fill=INK)
    d.text((116 + d.textlength("CookieJar", font=F_WORD), 58), "Tools", font=F_WORD, fill=GOLD)

    say = "Free for commercial use"
    width = int(d.textlength(say, font=F_PILL)) + 36
    soft = ImageDraw.Draw(img, "RGBA")
    soft.rounded_rectangle([64, 318, 64 + width, 350], radius=8,
                           outline=(255, 255, 255, 46), width=1)
    soft.text((82, 327), say, font=F_PILL, fill=MUTE)
    return img


def words(tool, accent):
    """The name, the sentence and the version pill, on their own layer so they can fade."""
    _, name, blurb, version, _, _ = tool
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    lines = wrap(name, F_NAME, 420, d)
    for i, line in enumerate(lines):
        d.text((64, 140 + i * 50), line, font=F_NAME, fill=INK + (255,))

    top = 140 + len(lines) * 50 + 14
    for i, line in enumerate(wrap(blurb, F_DESC, 400, d)):
        d.text((64, top + i * 23), line, font=F_DESC, fill=MUTE + (255,))

    width = int(d.textlength(version, font=F_PILL)) + 36
    d.rounded_rectangle([64, 272, 64 + width, 304], radius=8, fill=accent + (255,))
    d.text((82, 281), version, font=F_PILL, fill=(20, 18, 12, 255))
    return layer


def dim(layer, alpha, dy):
    """One layer, faded and nudged, which is the whole of how the words change over."""
    if alpha <= 0:
        return None
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(layer, (0, int(round(dy))))
    out.putalpha(out.getchannel("A").point(lambda a: int(a * alpha)))
    return out


def strip(into, ui, i, alpha, dx):
    if alpha <= 0:
        return
    y0, y1 = int(i * CH / BANDS), int((i + 1) * CH / BANDS)
    piece = ui.crop((0, y0, CW, y1))
    piece.putalpha(piece.getchannel("A").point(lambda a, l=alpha: int(a * l)))
    into.alpha_composite(piece, (int(round(dx)), y0))


def handover(old, new, p):
    """
    The old UI coming apart from the bottom up while the new one builds from the top down.

    The two overlap on purpose. Emptying the window and then filling it reads as a wipe;
    letting the new rows land while the last old ones are still leaving reads as one thing
    turning into another.
    """
    out = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    for i in range(BANDS):
        going = clamp((p - ((BANDS - 1 - i) / BANDS) * (1 - SPAN)) / SPAN)
        strip(out, old, i, 1.0 - going, going * SLIDE)

    for i in range(BANDS):
        coming = clamp((p - LAG - (i / BANDS) * (1 - SPAN - LAG)) / SPAN)
        strip(out, new, i, coming, (1 - coming) * SLIDE)
    return out


def still(ui):
    out = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    out.alpha_composite(ui)
    return out


def window(content, tool, accent, alpha):
    """The chrome around the UI, with the tool named in its bar."""
    layer = Image.new("RGBA", (WW, WH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([0, 0, WW - 1, WH - 1], radius=14, fill=(255, 255, 255, 12),
                        outline=(255, 255, 255, 30), width=1)
    d.line([(1, BAR), (WW - 2, BAR)], fill=(255, 255, 255, 22))
    layer.alpha_composite(content, (0, BAR))

    if alpha > 0:
        bar = Image.new("RGBA", (WW, BAR), (0, 0, 0, 0))
        b = ImageDraw.Draw(bar)
        b.rounded_rectangle([14, 9, 32, 27], radius=5, fill=accent + (255,))
        b.text((23, 18), tool[0], font=F_MARK, fill=(255, 255, 255, 255), anchor="mm")
        b.text((44, 18), tool[1], font=F_PILL, fill=INK + (255,), anchor="lm")
        bar.putalpha(bar.getchannel("A").point(lambda a, l=alpha: int(a * l)))
        layer.alpha_composite(bar, (0, 0))

    mask = Image.new("L", (WW, WH), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, WW - 1, WH - 1], radius=14, fill=255)
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", (WW, WH), 0), mask))
    return layer


def dots(img, index, accent):
    """Six marks along the bottom, so the shelf says how much of it there is."""
    d = ImageDraw.Draw(img, "RGBA")
    x = 64
    for i in range(len(TOOLS)):
        if i == index:
            d.rounded_rectangle([x, 382, x + 22, 389], radius=4, fill=accent + (255,))
            x += 32
        else:
            d.ellipse([x, 382, x + 7, 389], fill=(255, 255, 255, 48))
            x += 17


def compose(ground, said, content, tool, accent, alpha, dy, active):
    img = ground.copy()
    layer = dim(said[tool[0]], alpha, dy)
    if layer is not None:
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

    img = img.convert("RGBA")
    img.alpha_composite(window(content, tool, accent, alpha), (WX, WY))
    img = img.convert("RGB")
    dots(img, active, accent)
    return img


def frames():
    ground = base()
    said = {t[0]: words(t, ACCENT[t[0]]) for t in TOOLS}
    out = []

    for index, tool in enumerate(TOOLS):
        after = (index + 1) % len(TOOLS)
        nxt = TOOLS[after]
        a, b = ACCENT[tool[0]], ACCENT[nxt[0]]

        for _ in range(HOLD):
            out.append(compose(ground, said, still(PANELS[tool[0]]), tool, a, 1.0, 0, index))

        for f in range(TRANS):
            p = (f + 1) / TRANS
            content = handover(PANELS[tool[0]], PANELS[nxt[0]], p)

            # The two fades overlap rather than meeting at zero. Handing straight over at the
            # midpoint left one frame with no name on it at all, which read as a flicker.
            # Whichever side is stronger is the one drawn, so the names never sit on top of
            # each other either.
            going = clamp(1 - p / 0.55)
            coming = clamp((p - 0.30) / 0.55)
            if going >= coming:
                shown, alpha, dy, active = tool, going, -(1 - going) * 16, index
            else:
                shown, alpha, dy, active = nxt, coming, (1 - coming) * 16, after

            out.append(compose(ground, said, content, shown, mix(a, b, p), alpha, dy, active))

    return out


def flatten(made):
    """
    Every frame onto one shared palette, which is what lets this ship at all.

    A PNG carries a single palette for the whole file, so it cannot be built per frame: it is
    taken from a spread of frames instead. Dithering is off because these are screenshots of
    flat UI, and dither turns their large even areas into visible noise.
    """
    sample = made[::6]
    across = 3
    down = (len(sample) + across - 1) // across
    montage = Image.new("RGB", (W * across, H * down))
    for i, frame in enumerate(sample):
        montage.paste(frame, ((i % across) * W, (i // across) * H))

    shared = montage.quantize(colors=COLOURS, method=Image.MEDIANCUT)
    return [frame.quantize(palette=shared, dither=Image.Dither.NONE) for frame in made]


if __name__ == "__main__":
    made = flatten(frames())
    out = os.path.join(HERE, "banner.png")
    made[0].save(out, save_all=True, append_images=made[1:], duration=MS, loop=0)
    print("%-12s %3d frames  %.1f s  %.0f KB"
          % ("banner.png", len(made), len(made) * MS / 1000, os.path.getsize(out) / 1024))
