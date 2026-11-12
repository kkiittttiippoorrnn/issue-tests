"""แม่แบบรายงานผลเทส — คัดลอกไปกับ issues\\_template แล้วแก้ส่วน "ข้อมูล" ด้านล่าง
รัน: python -X utf8 make_report.py   → TestResult_<ID>.html + TestNote_<ID>.html (รูปฝังในไฟล์ ส่งต่อได้ไฟล์เดียว)

รูปแบบ (ดู SKILL.md หัวข้อ "รายงาน HTML"):
- บล็อก TEST PASS = TC ที่ผ่าน + ส่วนที่ผ่านของ TC ที่ผลปนกัน
- บล็อก TEST FAIL = เฉพาะส่วนที่ไม่ผ่าน (ไม่มี FAIL → ไม่มีบล็อกนี้)
- ข้อสังเกตแยกไฟล์ TestNote
"""
import base64, html, io, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "libraries"))
from HlMark import mark, table  # noqa: E402

EV = os.path.join(HERE, "evidence"); HL = os.path.join(EV, "hl")
os.makedirs(HL, exist_ok=True)
S = lambda n: os.path.join(EV, n); H = lambda n: os.path.join(HL, n)

# ====================== ข้อมูล (แก้ส่วนนี้) ======================
ID = "0000"
DATE = "dd / mm / yyyy"
VERSION = "<ชื่อแอป> <เวอร์ชัน (build)>"
TESTER = "<ชื่อผู้ทดสอบ>"
DATA = "ข้อมูลทดสอบ: <option / ข้อมูลที่ใช้ เขียนสั้นๆ>"

# รูปหลักฐาน: mark(ต้นฉบับ, [((x1,y1,x2,y2), "ป้าย", "above|below|left|right", "pass|fail|info")], ปลายทาง, crop=(...))
# mark(S("tc1.png"), [((100, 200, 600, 240), "ค่าที่ตรวจ = ถูกต้อง", "below", "pass")], H("tc1.png"), crop=(0, 0, 1920, 1080))
# table(H("tc1_db.png"), "DB ก่อน → หลัง", ["ตาราง/คอลัมน์", "ก่อน", "หลัง", ""], [("Table.Col", "1", "2", "ถูกต้อง", "pass")])

# แต่ละ TC: (เลข, ชื่อ, [Step], [ผลลัพธ์ที่คาดหวัง], [ผลรายข้อ], [รูป])
#   ผลรายข้อ = ("PASS" | "FAIL" | "N/A", ข้อความ) · รูป = (ไฟล์ใน evidence\hl, คำบรรยาย, "PASS" | "FAIL")
TCS = [
    (1, "<ชื่อ Test Case>",
     ["เข้าสู่ระบบ → เมนู → หน้า", "ทำ ..."],
     ["..."],
     [("PASS", "ผลที่เห็นจริง + หลักฐาน (ID, ค่าใน DB)")],
     []),
]

# ข้อสังเกต: (หัวข้อ, [Step], ผลจริง, ผลกระทบ/ให้ SA ยืนยัน, "ข้อมูลในรูป: ...", [(รูป, คำบรรยาย)])
OBS = []
# ================================================================

SEP = "-" * 102
COLOR = {"PASS": "#16803d", "FAIL": "#b91c1c", "N/A": "#6b7280"}


def img(name, cap="", W=760):
    im = Image.open(H(name)).convert("RGB")
    if im.width > W:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=55, optimize=True, progressive=True, subsampling=2)
    c = f"<div style='color:#555;font-size:12px'>{html.escape(cap)}</div>" if cap else ""
    return f"<div style='margin:6px 0'>{c}<img src='data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}' style='max-width:{W}px;border:1px solid #ccc'></div>"


def head(status):
    return [f"<div>Test Status : <b style='color:{COLOR['PASS' if status == 'PASS' else 'FAIL']}'>TEST {status}</b></div>",
            f"<div>Test on Date : {DATE}</div>", f"<div>Test Version : {html.escape(VERSION)}</div>", f"<div>Test By : {html.escape(TESTER)}</div>",
            f"<div style='color:#555'>{html.escape(DATA)}</div>"]


def tc_status(results):
    st = {s for s, _ in results}
    if st == {"N/A"}:
        return "N/A"
    if "FAIL" in st:
        return "FAIL (ผ่านบางส่วน)" if "PASS" in st else "FAIL"
    return "PASS"


def section(block):
    """block = "PASS" หรือ "FAIL" — เลือกเฉพาะผล/รูปของบล็อกนั้น"""
    out = []
    for no, title, steps, expect, results, imgs in TCS:
        mine = [(s, t) for s, t in results if (s == "FAIL") == (block == "FAIL")]
        if not mine:
            continue
        st = tc_status(results); mixed = st.startswith("FAIL (")
        out.append(f"<div>{SEP}</div><div><b>Test Case {no}</b> : {html.escape(title)} — "
                   f"<b style='color:{COLOR.get(st.split()[0], '#000')}'>{st}</b></div><div>Step</div><ol>")
        out += [f"<li>{html.escape(x)}</li>" for x in steps]
        out.append("</ol><div>ผลลัพธ์ที่คาดหวัง</div><ol>")
        out += [f"<li>{html.escape(x)}</li>" for x in expect]
        out.append("</ol><div>ผลการทดสอบ</div>")
        if mixed:
            out.append(f"<div style='color:{COLOR[block]}'><b>{'ผลที่ผ่าน (PASS)' if block == 'PASS' else 'ผลที่ไม่ผ่าน (FAIL)'}</b></div>")
        out.append("<ul>")
        out += [f"<li>{html.escape(t)}</li>" for _, t in mine]
        out.append("</ul>")
        out += [img(n, c) for n, c, *s in imgs if (s[0] if s else "PASS") == ("FAIL" if block == "FAIL" else "PASS")]
    return out


def write(name, title, body):
    p = os.path.join(HERE, name)
    open(p, "w", encoding="utf-8").write("\n".join(
        [f"<html><head><meta charset='utf-8'><title>{title}</title></head><body style='font-family:Tahoma,sans-serif;font-size:14px'>"]
        + body + ["</body></html>"]))
    print(name, round(os.path.getsize(p) / 1e6, 2), "MB")


body = head("PASS") + section("PASS")
fail = section("FAIL")
if fail:
    body += [f"<div>{SEP}</div><br>"] + head("FAIL") + fail
if OBS:
    body.append(f"<div>{SEP}</div><div style='color:#555'>ข้อสังเกตแยกไว้ในไฟล์ TestNote_{ID}.html</div>")
write(f"TestResult_{ID}.html", f"Test Result #{ID}", body)

if OBS:
    nb = [f"<div><b>Test Note #{ID}</b> — ข้อสังเกต</div>"] + head("PASS")[1:]
    for i, (t, st, act, imp, ref, imgs) in enumerate(OBS, 1):
        nb.append(f"<div>{SEP}</div><div><b>ข้อสังเกต {i}</b> : {html.escape(t)}</div><div>Step</div><ol>")
        nb += [f"<li>{html.escape(x)}</li>" for x in st]
        nb.append(f"</ol><div>ผลจริง</div><ul><li>{html.escape(act)}</li></ul><div>ผลกระทบ / ให้ SA ยืนยัน</div><ul><li>{html.escape(imp)}</li></ul>")
        if ref:
            nb.append(f"<div style='color:#555;font-size:12px'>{html.escape(ref)}</div>")
        nb += [img(n, c) for n, c in imgs]
    write(f"TestNote_{ID}.html", f"Test Note #{ID}", nb)
