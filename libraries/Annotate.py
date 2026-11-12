"""ช่วยทำรูปหลักฐานให้สื่อชัด: แถบหัวรูป (TC + สิ่งที่ตรวจ + ผล) และกรอบเน้นตามพิกัด
ใช้ร่วมกันทุก issue (เว็บ / HQ Desktop / SSMS)
"""
from PIL import Image, ImageDraw, ImageFont

FONT = r"C:\Windows\Fonts\tahoma.ttf"
FONT_B = r"C:\Windows\Fonts\tahomabd.ttf"
COLORS = {"pass": (22, 128, 61), "fail": (200, 30, 30), "info": (30, 64, 175), "warn": (180, 110, 0)}


def _font(size, bold=False):
    try:
        return ImageFont.truetype(FONT_B if bold else FONT, size)
    except Exception:
        return ImageFont.load_default()


def add_banner(path, title, detail="", status="info"):
    """เพิ่มแถบหัวรูป: บรรทัดแรก title (ตัวหนา) บรรทัดสอง detail — สีตาม status (pass/fail/info/warn)"""
    img = Image.open(path).convert("RGB")
    color = COLORS.get(str(status).lower(), COLORS["info"])
    f1, f2 = _font(22, True), _font(17)
    lines = [l for l in str(detail).split("\n") if l.strip()] if detail else []
    h = 16 + 30 + 26 * len(lines) + 10
    out = Image.new("RGB", (img.width, img.height + h), "white")
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, img.width, h - 1], fill=color)
    d.text((16, 12), str(title), font=f1, fill="white")
    for i, l in enumerate(lines):
        d.text((16, 46 + 26 * i), l, font=f2, fill="white")
    out.paste(img, (0, h))
    out.save(path)
    return h


def draw_boxes(path, boxes, offset_y=0):
    """boxes = [(x, y, w, h, label, status), ...] พิกัดของรูปเดิม (ก่อนเพิ่มแถบหัว) -> วาดกรอบ + ป้าย"""
    img = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(img)
    f = _font(16, True)
    for x, y, w, h, label, status in boxes:
        c = COLORS.get(str(status).lower(), COLORS["fail"])
        y += offset_y
        for k in range(3):
            d.rectangle([x - 3 - k, y - 3 - k, x + w + 3 + k, y + h + 3 + k], outline=c)
        if label:
            tw = d.textlength(str(label), font=f)
            ty = y - 30 if y - 30 > offset_y else y + h + 6
            d.rectangle([x - 3, ty, x + tw + 10, ty + 24], fill=c)
            d.text((x + 3, ty + 3), str(label), font=f, fill="white")
    img.save(path)
