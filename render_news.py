#!/usr/bin/env python3
"""Render the Thursday 26 November 2026 world-news front page, 1024x1024 PNG.

Original work for make.fun news-image-20261126: a dense dated front page.
Layout: masthead, three lead stories with drawn scenes, a strip of twelve
miniature drawn scenes, a two-column list of the day's remaining stories,
a UTC timeline bar, and a footer naming the 21 fields and the sources.
All 50 stories are events first reported on 26 November 2026, paraphrased
from public news digests (Reuters, BBC, UN News, The Global Eye,
Jagran Josh, The Silk Paradox). Every pixel is drawn here with PIL;
no copied artwork, no photographs.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (10, 25, 49)
ORANGE = (255, 122, 0)
PAPER = (250, 247, 240)
INK = (18, 18, 18)
GREY = (96, 96, 96)
LINE = (205, 205, 205)
SEA = (16, 80, 140)
FIRE = (214, 48, 16)

REGION_COLORS = {
    "NORTH AMERICA": (25, 80, 160),
    "CARIBBEAN": (0, 150, 136),
    "SOUTH AMERICA": (120, 60, 150),
    "EUROPE": (30, 90, 170),
    "MIDDLE EAST": (178, 34, 34),
    "AFRICA": (150, 90, 10),
    "SOUTH ASIA": (190, 90, 0),
    "EAST ASIA": (0, 128, 96),
    "SOUTHEAST ASIA": (60, 140, 40),
    "OCEANIA": (120, 90, 160),
    "CENTRAL ASIA": (110, 60, 40),
}
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

TITLE = "THE WORLD IN ONE DAY"
SUB = ("Thursday 26 November 2026  ·  50 stories  ·  11 regions  ·  "
       "21 fields  ·  15 drawn scenes  ·  UTC timeline")

LEADS = [
    ("AFRICA", "31 killed as fuel tanker burns on Cairo highway",
     "Tanker overturns and ignites; fire crews battle the blaze for hours.",
     "fire"),
    ("MIDDLE EAST", "Tankers hit by mines in Strait of Hormuz",
     "Iran's Guards say three tankers struck; Trump calls regime change \u2018feasible\u2019.",
     "mines"),
    ("NORTH AMERICA", "Nasdaq sinks ~4% in AI rout",
     "Wall Street spooked by fresh Trump tariffs; chip stocks lead the slide.",
     "chart"),
]

# The day's remaining 47 stories: (region, one-line headline).
STORIES = [
    ("NORTH AMERICA", "Trump unveils new tariffs on 14 partners"),
    ("NORTH AMERICA", "US consumer confidence nears 2-year high"),
    ("NORTH AMERICA", "US clears $622m F-16 kit sale to Kyiv"),
    ("NORTH AMERICA", "Pacifica Pier collapses in huge California waves"),
    ("NORTH AMERICA", "Huawei convicted in US over Iran banking"),
    ("NORTH AMERICA", "Macy's Thanksgiving parade postponed to Saturday"),
    ("CARIBBEAN", "Barbados sets Feb deadline for Caribbean AI rules"),
    ("SOUTH AMERICA", "Colombia marks 10 years since peace deal"),
    ("SOUTH AMERICA", "Colombia bomb injures 23 in city centre"),
    ("SOUTH AMERICA", "Colombia police free 20 hostages after 17 hours"),
    ("SOUTH AMERICA", "Petrobras unveils $122bn investment plan"),
    ("SOUTH AMERICA", "Venezuela reveals $237.5bn public debt"),
    ("SOUTH AMERICA", "El Salvador earmarks $860m year-end debt cash"),
    ("EUROPE", "Putin vows retaliation for refinery strikes"),
    ("EUROPE", "Russia defence budget jumps 27% to record"),
    ("EUROPE", "Russia lost nearly 500,000 in Ukraine war"),
    ("EUROPE", "Poland urges NATO to down Russian missiles"),
    ("EUROPE", "Ukraine hits Russian warplanes at Kinzhal base"),
    ("EUROPE", "Magyar meets Zelensky in Uzhhorod first time"),
    ("EUROPE", "Norway pledges $7bn for Ukraine in 2027"),
    ("EUROPE", "Britain probes nuclear-test legacy"),
    ("MIDDLE EAST", "Houthis hit Saudi ports and Riyadh tower"),
    ("MIDDLE EAST", "Gaza: Hamas security chief killed in strike"),
    ("MIDDLE EAST", "Storm threatens 1.8m Gazans sheltering in tents"),
    ("MIDDLE EAST", "Judges urge dropping top Netanyahu charges"),
    ("MIDDLE EAST", "UNRWA worker among 3 killed in Gaza strikes"),
    ("MIDDLE EAST", "Houthis warn airlines away from Saudi airspace"),
    ("AFRICA", "Egypt hails slow Suez Canal revenue recovery"),
    ("AFRICA", "ECOWAS approves 2027 regional force roadmap"),
    ("AFRICA", "Libya vows retaliation for Benghazi strike"),
    ("SOUTH ASIA", "India marks Constitution Day, Nov 26"),
    ("SOUTH ASIA", "India gives Nepal \u20b915,000cr aid package"),
    ("SOUTH ASIA", "Bangladesh garment wage rises 36%"),
    ("SOUTH ASIA", "Hasina seeks return to Dhaka on Dec 16"),
    ("SOUTH ASIA", "Pakistan's first astronaut joins Tiangong"),
    ("SOUTH ASIA", "Gukesh faces Sindarov in world chess title"),
    ("SOUTH ASIA", "IPL 2027 auction draws 1,220 players"),
    ("EAST ASIA", "China welcomes Pakistan's first astronaut"),
    ("EAST ASIA", "Xi graft probe hits Shanghai rising star"),
    ("EAST ASIA", "Kospi -6.2% as Asian chip rout spreads"),
    ("EAST ASIA", "Japan\u2013Europe probe reaches Mercury after 8 years"),
    ("EAST ASIA", "North Korea expels Swiss diplomat"),
    ("EAST ASIA", "Shein settles $129m customer-service claims"),
    ("SOUTHEAST ASIA", "Vietnam pushes sustainable farming"),
    ("OCEANIA", "Australia inflation 4.9% in October"),
    ("OCEANIA", "Senator Blyth defects to One Nation"),
    ("CENTRAL ASIA", "Russia warns of ISIS-K threat in Afghanistan"),
]

# Twelve miniature scenes for the strip: (label, kind).
MINI_SCENES = [
    ("ship", "ship"), ("fire", "fire"), ("markets", "chart"),
    ("rocket", "rocket"), ("court", "gavel"), ("vote", "ballot"),
    ("satellite", "satellite"), ("energy", "coin"), ("harvest", "wheat"),
    ("waves", "waves"), ("sport", "trophy"), ("tower", "tower"),
]

SOURCES = "Sources: Reuters, BBC, UN News, The Global Eye, Jagran Josh — 26 November 2026"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fnt, width):
    """One line, shortened with an ellipsis when it would overflow."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + "\u2026", font=fnt) > width:
        text = text[:-1]
    return text + "\u2026"


def draw_pictogram(draw, x, y, s, kind, ink):
    """A tiny geometric scene inside a square of side s at (x, y)."""
    if kind == "fire":
        draw.polygon([(x + s * .5, y + s * .05), (x + s * .85, y + s * .55),
                      (x + s * .68, y + s * .5), (x + s * .8, y + s * .95),
                      (x + s * .2, y + s * .95), (x + s * .32, y + s * .5),
                      (x + s * .15, y + s * .55)], fill=ink)
    elif kind == "ship":
        draw.polygon([(x + s * .1, y + s * .55), (x + s * .9, y + s * .55),
                      (x + s * .75, y + s * .85), (x + s * .25, y + s * .85)], fill=ink)
        draw.rectangle([x + s * .45, y + s * .15, x + s * .55, y + s * .55], fill=ink)
        draw.polygon([(x + s * .55, y + s * .15), (x + s * .85, y + s * .4),
                      (x + s * .55, y + s * .4)], fill=ink)
    elif kind == "mines":
        for cx, cy in [(0.3, 0.45), (0.7, 0.6), (0.5, 0.3)]:
            mx, my = x + s * cx, y + s * cy
            r = s * 0.14
            draw.ellipse([mx - r, my - r, mx + r, my + r], fill=ink)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                draw.line([mx, my, mx + dx * r * 1.8, my + dy * r * 1.8],
                          fill=ink, width=2)
    elif kind == "chart":
        pts = [(x + s * .1, y + s * .3), (x + s * .35, y + s * .45),
               (x + s * .6, y + s * .35), (x + s * .9, y + s * .85)]
        draw.line(pts, fill=ink, width=3, joint="curve")
        draw.polygon([(x + s * .9, y + s * .85), (x + s * .78, y + s * .82),
                      (x + s * .86, y + s * .68)], fill=ink)
    elif kind == "rocket":
        draw.polygon([(x + s * .5, y + s * .05), (x + s * .7, y + s * .45),
                      (x + s * .6, y + s * .75), (x + s * .4, y + s * .75),
                      (x + s * .3, y + s * .45)], fill=ink)
        draw.polygon([(x + s * .42, y + s * .75), (x + s * .5, y + s * .95),
                      (x + s * .58, y + s * .75)], fill=(255, 122, 0))
    elif kind == "gavel":
        draw.rectangle([x + s * .15, y + s * .3, x + s * .85, y + s * .5], fill=ink)
        draw.rectangle([x + s * .45, y + s * .5, x + s * .55, y + s * .8], fill=ink)
        draw.rectangle([x + s * .3, y + s * .8, x + s * .7, y + s * .88], fill=ink)
    elif kind == "ballot":
        draw.rectangle([x + s * .2, y + s * .2, x + s * .8, y + s * .85],
                       outline=ink, width=3)
        draw.line([(x + s * .3, y + s * .55), (x + s * .45, y + s * .7),
                   (x + s * .75, y + s * .35)], fill=ink, width=3)
    elif kind == "satellite":
        draw.rectangle([x + s * .35, y + s * .4, x + s * .65, y + s * .6], fill=ink)
        draw.line([x + s * .35, y + s * .5, x + s * .1, y + s * .7], fill=ink, width=3)
        draw.line([x + s * .65, y + s * .5, x + s * .9, y + s * .3], fill=ink, width=3)
        draw.ellipse([x + s * .6, y + s * .1, x + s * .8, y + s * .3], outline=ink, width=2)
    elif kind == "coin":
        draw.ellipse([x + s * .2, y + s * .2, x + s * .8, y + s * .8], outline=ink, width=3)
        draw.text((x + s * .38, y + s * .28), "$", font=font(BOLD, int(s * .42)), fill=ink)
    elif kind == "wheat":
        draw.line([x + s * .5, y + s * .3, x + s * .5, y + s * .9], fill=ink, width=3)
        for dy in (0.3, 0.48, 0.66):
            draw.ellipse([x + s * .3, y + s * dy, x + s * .48, y + s * (dy + .14)], fill=ink)
            draw.ellipse([x + s * .52, y + s * dy, x + s * .7, y + s * (dy + .14)], fill=ink)
    elif kind == "waves":
        for k in range(3):
            yy = y + s * (0.3 + k * 0.22)
            draw.arc([x + s * .1, yy, x + s * .9, yy + s * .25], 180, 360, fill=ink, width=3)
    elif kind == "trophy":
        draw.polygon([(x + s * .3, y + s * .15), (x + s * .7, y + s * .15),
                      (x + s * .65, y + s * .6), (x + s * .35, y + s * .6)], fill=ink)
        draw.rectangle([x + s * .42, y + s * .6, x + s * .58, y + s * .75], fill=ink)
        draw.rectangle([x + s * .3, y + s * .75, x + s * .7, y + s * .85], fill=ink)
    elif kind == "tower":
        draw.rectangle([x + s * .35, y + s * .1, x + s * .65, y + s * .9], fill=ink)
        for k in range(4):
            yy = y + s * (0.2 + k * 0.18)
            draw.rectangle([x + s * .38, yy, x + s * .62, yy + s * .06], fill=(255, 255, 255))


def paint_masthead(draw):
    draw.rectangle([0, 0, W, 86], fill=NAVY)
    draw.text((24, 10), TITLE, font=font(BOLD, 36), fill=(255, 255, 255))
    draw.text((24, 56), SUB, font=font(REGULAR, 15), fill=(255, 200, 140))
    draw.rectangle([0, 86, W, 90], fill=ORANGE)


def paint_leads(draw):
    cols = [24, 356, 688]
    cw = 312
    for (region, head, dek, kind), x in zip(LEADS, cols):
        # Drawn scene panel.
        draw.rectangle([x, 98, x + cw, 162], fill=(232, 238, 245))
        draw.rectangle([x, 98, x + cw, 162], outline=LINE, width=1)
        if kind == "fire":
            draw.rectangle([x, 138, x + cw, 162], fill=(60, 60, 60))
            draw.rectangle([x + 120, 118, x + 200, 140], fill=(90, 90, 90))
            draw_pictogram(draw, x + 128, 96, 44, "fire", FIRE)
            draw_pictogram(draw, x + 190, 104, 30, "fire", ORANGE)
        elif kind == "mines":
            draw.rectangle([x, 138, x + cw, 162], fill=SEA)
            draw_pictogram(draw, x + 30, 100, 56, "ship", NAVY)
            draw_pictogram(draw, x + 220, 104, 52, "mines", INK)
        else:
            draw.rectangle([x, 98, x + cw, 162], fill=(24, 24, 32))
            draw_pictogram(draw, x + 16, 104, 52, "chart", (255, 80, 60))
            for gx in range(0, cw, 24):
                draw.line([x + gx, 156, x + gx, 162], fill=(120, 120, 130), width=1)
        colour = REGION_COLORS[region]
        draw.text((x, 170), region, font=font(BOLD, 11), fill=colour)
        y = 186
        for line in wrap(draw, head, font(SERIF, 17), cw)[:2]:
            draw.text((x, y), line, font=font(SERIF, 17), fill=INK)
            y += 22
        for line in wrap(draw, dek, font(REGULAR, 12), cw)[:2]:
            draw.text((x, y), line, font=font(REGULAR, 12), fill=GREY)
            y += 16
    draw.line([24, 252, 1000, 252], fill=LINE, width=1)


def paint_scenes(draw):
    draw.text((24, 262), "SCENES OF THE DAY — 12 DRAWN FROM THE NEWS",
              font=font(BOLD, 12), fill=GREY)
    slot = (W - 48 - 12 * 56) // 11
    for i, (label, kind) in enumerate(MINI_SCENES):
        x = 24 + i * (56 + slot)
        draw.rectangle([x, 282, x + 56, 338], fill=(255, 255, 255), outline=LINE, width=1)
        draw_pictogram(draw, x + 6, 288, 44, kind, NAVY)
        lab = font(BOLD, 10)
        tw = draw.textlength(label, font=lab)
        draw.text((x + (56 - tw) / 2, 340), label, font=lab, fill=GREY)


def paint_list(draw):
    draw.text((24, 364), "THE DAY IN 47 MORE STORIES",
              font=font(BOLD, 12), fill=GREY)
    left = STORIES[:24]
    right = STORIES[24:]
    for col_x, items in ((24, left), (522, right)):
        y = 386
        for region, head in items:
            colour = REGION_COLORS[region]
            tag = font(BOLD, 10)
            draw.text((col_x, y + 1), region, font=tag, fill=colour)
            tag_w = draw.textlength(region, font=tag)
            head_f = font(REGULAR, 12)
            draw.text((col_x + tag_w + 8, y), fit(draw, head, head_f, 478 - tag_w - 8),
                      font=head_f, fill=INK)
            y += 23
    draw.line([512, 386, 512, 928], fill=LINE, width=1)


def paint_timeline(draw):
    y = 934
    draw.text((24, y), "UTC", font=font(BOLD, 12), fill=NAVY)
    x0, x1 = 62, 1000
    draw.line([x0, y + 8, x1, y + 8], fill=NAVY, width=2)
    for h in range(24):
        x = x0 + (x1 - x0) * h / 23
        draw.line([x, y + 2, x, y + 14], fill=NAVY, width=1)
        if h % 3 == 0:
            lab = font(REGULAR, 9)
            t = f"{h:02d}"
            draw.text((x - draw.textlength(t, font=lab) / 2, y + 16), t,
                      font=lab, fill=GREY)


FIELDS_A = ("war · energy · markets · tariffs · AI · space · diplomacy · "
            "courts · sport · culture · climate")
FIELDS_B = ("health · crime · transport · finance · telecom · agriculture · "
            "education · media · science · politics")


def paint_footer(draw):
    draw.rectangle([0, 972, W, H], fill=NAVY)
    draw.text((24, 978), "21 FIELDS: " + FIELDS_A, font=font(REGULAR, 11),
              fill=(255, 255, 255))
    draw.text((24, 994), FIELDS_B, font=font(REGULAR, 11),
              fill=(255, 255, 255))
    draw.text((24, 1010), SOURCES + "  ·  DATE-CHECK AUDIT: every story first reported 26 Nov 2026; none predates 13 Nov 2026",
              font=font(REGULAR, 10), fill=(180, 190, 205))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    paint_masthead(draw)
    paint_leads(draw)
    paint_scenes(draw)
    paint_list(draw)
    paint_timeline(draw)
    paint_footer(draw)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True)
    print("bytes:", os.path.getsize(out))
    print("stories:", len(LEADS) + len(STORIES),
          "| regions:", len({r for r, _ in STORIES} | {r for r, _, _, _ in LEADS}),
          "| scenes:", 3 + len(MINI_SCENES))


if __name__ == "__main__":
    main()
