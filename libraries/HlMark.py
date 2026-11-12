"""รูปหลักฐานสำหรับรายงาน: ตัดเฉพาะบริเวณ + กรอบหนา + ป้ายข้อความบอกสิ่งที่ตรวจ / รูปตาราง (DB, API)
ใช้: import sys; sys.path.insert(0, r"<repo>\\libraries"); from HlMark import mark, table  (ดูแม่แบบ issues/_template/make_report.py)

mark(src, items, dst, crop=None)
  items = [((x1, y1, x2, y2), "ข้อความป้าย", "above|below|right|left", "pass|fail|info"), ...]  (สถานะไม่ใส่ = pass)
  พิกัดเป็นพิกัดของรูปต้นฉบับ (ก่อน crop) · crop = (x1, y1, x2, y2)
table(dst, title, head, rows, status="pass")   ตารางผล DB/API เป็นรูป
"""
from PIL import Image, ImageDraw, ImageFont

COL = {"pass": (22, 163, 74), "fail": (220, 38, 38), "info": (37, 99, 235), "warn": (217, 119, 6)}
FILL = {"pass": (232, 248, 236), "fail": (254, 226, 226), "info": (219, 234, 254), "warn": (254, 243, 199)}
FONT = ImageFont.truetype(r"C:\Windows\Fonts\tahoma.ttf", 15)
FONTB = ImageFont.truetype(r"C:\Windows\Fonts\tahomabd.ttf", 16)
PAD = 30


def mark(src, items, dst, crop=None):
    im = Image.open(src).convert("RGB")
    norm = []
    for it in items:
        r, label, where = it[0], it[1], it[2]
        st = it[3] if len(it) > 3 else "pass"
        if crop:
            r = (r[0] - crop[0], r[1] - crop[1], r[2] - crop[0], r[3] - crop[1])
        norm.append((r, label, where, st))
    if crop:
        im = im.crop(crop)
    c = Image.new("RGB", (im.width, im.height + 2 * PAD), "white")
    c.paste(im, (0, PAD))
    d = ImageDraw.Draw(c)
    for (x1, y1, x2, y2), label, where, st in norm:
        color = COL.get(st, COL["pass"])
        y1 += PAD; y2 += PAD
        for i in range(3):
            d.rectangle((x1 - i, y1 - i, x2 + i, y2 + i), outline=color)
        if label:
            tw = d.textlength(label, font=FONTB) + 12
            lx = min(max(0, x1), c.width - tw)
            ly = {"above": y1 - 28, "below": y2 + 4, "right": y1, "left": y1}.get(where, y1 - 28)
            if where == "right":
                lx = min(x2 + 8, c.width - tw)
            elif where == "left":
                lx = max(0, x1 - tw - 8)
            ly = max(0, min(ly, c.height - 24))
            d.rectangle((lx, ly, lx + tw, ly + 24), fill=color)
            d.text((lx + 6, ly + 3), label, font=FONTB, fill="white")
    c.save(dst)
    return dst


def table(dst, title, head, rows, status="pass"):
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    cw = [int(max([tmp.textlength(str(h), font=FONTB)] + [tmp.textlength(str(r[i]), font=FONT) for r in rows])) + 20
          for i, h in enumerate(head)]
    wd = max(sum(cw) + 20, int(tmp.textlength(title, font=FONTB)) + 30)
    im = Image.new("RGB", (wd, 50 + 28 * (len(rows) + 1) + 10), "white")
    d = ImageDraw.Draw(im)
    d.text((10, 10), title, font=FONTB, fill="black")
    y, x = 40, 10
    for i, h in enumerate(head):
        d.rectangle((x, y, x + cw[i], y + 28), fill=(230, 230, 230), outline=(160, 160, 160))
        d.text((x + 6, y + 5), str(h), font=FONTB, fill="black"); x += cw[i]
    for r in rows:
        y += 28; x = 10
        st = r[-1] if isinstance(r, tuple) and len(r) > len(head) else status
        for i in range(len(head)):
            d.rectangle((x, y, x + cw[i], y + 28), outline=(200, 200, 200), fill=FILL.get(st, FILL["pass"]))
            d.text((x + 6, y + 5), str(r[i]), font=FONT, fill="black"); x += cw[i]
    im.save(dst)
    return dst
