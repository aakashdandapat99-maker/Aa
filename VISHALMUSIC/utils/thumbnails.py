import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from VISHALMUSIC.core.dir import CACHE_DIR

# ------------------------- Constants -------------------------
PANEL_W, PANEL_H = 800, 560
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 80
TRANSPARENCY = 180
INNER_OFFSET = 40

THUMB_W, THUMB_H = 560, 280
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET

TITLE_X = PANEL_X + 50
META_X = PANEL_X + 50
TITLE_Y = THUMB_Y + THUMB_H + 15
META_Y = TITLE_Y + 50

BAR_X, BAR_Y = PANEL_X + 60, META_Y + 50
BAR_TOTAL_LEN = 500
BAR_RED_LEN = 300

ICONS_W, ICONS_H = 450, 50
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 60

MAX_TITLE_WIDTH = PANEL_W - 100

# ------------------------- Helper Functions -------------------------
def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    """Trim text with ellipsis if it exceeds max width"""
    ellipsis = "…"
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis
    return ellipsis

async def download_image(url: str, path: str) -> bool:
    """Download image asynchronously and save to path"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(path, "wb") as f:
                        await f.write(await resp.read())
                    return True
    except Exception:
        pass
    return False

# ------------------------- Main Function -------------------------
async def get_thumb(videoid: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_premium.png")
    if os.path.exists(cache_path):
        return cache_path

    # ---------------- Fetch YouTube Data ----------------
    results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
    try:
        results_data = results.next()  # py_yt sync
        result_items = results_data.get("result", [])
        if not result_items:
            raise ValueError("No results found")
        data = result_items[0]

        title = re.sub(r"\W+", " ", data.get("title", "Unsupported Title")).title()
        thumbnail_url = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration")
        views = data.get("viewCount", {}).get("short", "Unknown Views")
    except Exception:
        title, thumbnail_url, duration, views = "Unsupported Title", YOUTUBE_IMG_URL, None, "Unknown Views"

    is_live = not duration or str(duration).strip().lower() in {"", "live", "live now"}
    duration_text = "Live" if is_live else duration or "Unknown"

    # ---------------- Download Thumbnail ----------------
    thumb_path = os.path.join(CACHE_DIR, f"temp_{videoid}.png")
    if not await download_image(thumbnail_url, thumb_path):
        return YOUTUBE_IMG_URL

    # ---------------- Create Premium Base Image ----------------
    base = Image.open(thumb_path).resize((1280, 720)).convert("RGBA")
    bg = ImageEnhance.Brightness(base.filter(ImageFilter.BoxBlur(12))).enhance(0.5)

    # Frosted Glass Panel
    panel_area = bg.crop((PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H))
    overlay = Image.new("RGBA", (PANEL_W, PANEL_H), (255, 255, 255, TRANSPARENCY))
    frosted = Image.alpha_composite(panel_area, overlay)
    mask = Image.new("L", (PANEL_W, PANEL_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, PANEL_W, PANEL_H), 50, fill=255)
    bg.paste(frosted, (PANEL_X, PANEL_Y), mask)

    # ---------------- Fonts ----------------
    try:
        title_font = ImageFont.truetype("VISHALMUSIC/assets/thumb/font2.ttf", 36)
        regular_font = ImageFont.truetype("VISHALMUSIC/assets/thumb/font.ttf", 20)
    except OSError:
        title_font = regular_font = ImageFont.load_default()

    draw = ImageDraw.Draw(bg)

    # ---------------- Video Thumbnail ----------------
    thumb = base.resize((THUMB_W, THUMB_H))
    tmask = Image.new("L", thumb.size, 0)
    ImageDraw.Draw(tmask).rounded_rectangle((0, 0, THUMB_W, THUMB_H), 25, fill=255)
    bg.paste(thumb, (THUMB_X, THUMB_Y), tmask)

    # ---------------- Draw Text ----------------
    draw.text((TITLE_X, TITLE_Y), trim_to_width(title, title_font, MAX_TITLE_WIDTH), fill="black", font=title_font)
    draw.text((META_X, META_Y), f"YouTube | {views}", fill="black", font=regular_font)

    # ---------------- Progress Bar ----------------
    draw.line([(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)], fill="red", width=8)
    draw.line([(BAR_X + BAR_RED_LEN, BAR_Y), (BAR_X + BAR_TOTAL_LEN, BAR_Y)], fill="gray", width=6)
    draw.ellipse([(BAR_X + BAR_RED_LEN - 8, BAR_Y - 8), (BAR_X + BAR_RED_LEN + 8, BAR_Y + 8)], fill="red")
    draw.text((BAR_X, BAR_Y + 20), "00:00", fill="black", font=regular_font)
    draw.text((BAR_X + BAR_TOTAL_LEN - (90 if is_live else 60), BAR_Y + 20),
              duration_text, fill="red" if is_live else "black", font=regular_font)

    # ---------------- Play Icons ----------------
    icons_path = "VISHALMUSIC/assets/thumb/play_icons.png"
    if os.path.isfile(icons_path):
        icons = Image.open(icons_path).resize((ICONS_W, ICONS_H)).convert("RGBA")
        r, g, b, a = icons.split()
        black_icons = Image.merge("RGBA", (r.point(lambda *_: 0),
                                           g.point(lambda *_: 0),
                                           b.point(lambda *_: 0), a))
        bg.paste(black_icons, (ICONS_X, ICONS_Y), black_icons)

    # ---------------- Cleanup & Save ----------------
    try:
        os.remove(thumb_path)
    except OSError:
        pass

    bg.save(cache_path)
    return cache_path