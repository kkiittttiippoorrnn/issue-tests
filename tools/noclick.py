"""คลิกแบบไม่ขยับเมาส์ — PostMessage WM_LBUTTONDOWN/UP ไปที่หน้าต่างลูก ณ จุดนั้น (เหมือนเมาส์คลิก แต่เคอร์เซอร์อยู่ที่เดิม)
- ไม่บล็อก (ต่างจาก UIA Invoke ที่ค้างเมื่อปุ่มเปิด modal)
- ใช้ได้กับ WinForms/DevExpress (control มี hwnd ของตัวเอง) — โปรเซสต้องสิทธิ์เท่ากัน (Admin ↔ Admin)
- ฟีเจอร์ที่นับ idle (Auto Logout) จะไม่นับเป็น input — ใช้ Click จริงแทน
import แล้วจะตั้ง FlaUI Mouse ให้กระโดดทันที (ไม่ลาก) สำหรับจุดที่ยังใช้ el.Click()
env FLAUI_REAL_MOUSE=1 = กลับไปใช้เมาส์จริง
"""
import ctypes
import os
import time
from ctypes import wintypes

u32 = ctypes.windll.user32
u32.WindowFromPoint.argtypes = [wintypes.POINT]
u32.WindowFromPoint.restype = wintypes.HWND
WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON = 0x0200, 0x0201, 0x0202, 0x0001
REAL = bool(os.environ.get("FLAUI_REAL_MOUSE"))

try:  # จุดที่ยังเรียก el.Click()/Mouse.Click → กระโดดทันที ไม่ลาก
    from FlaUI.Core.Input import Mouse
    Mouse.MovePixelsPerMillisecond = 100000.0
except Exception:  # noqa: BLE001
    pass


def _pid(h):
    pid = wintypes.DWORD(); u32.GetWindowThreadProcessId(h, ctypes.byref(pid)); return pid.value


def _raise(x, y, pids):
    """ยกหน้าต่างบนสุดของ pids ที่ครอบจุด (x, y) ขึ้นมาบนสุด (TOPMOST แล้ว NOTOPMOST — ไม่ติดกฎ SetForegroundWindow)"""
    hits = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h, _):
        if u32.IsWindowVisible(h) and _pid(h) in pids:
            r = wintypes.RECT(); u32.GetWindowRect(h, ctypes.byref(r))
            if r.left <= x < r.right and r.top <= y < r.bottom:
                hits.append(h)
        return True
    u32.EnumWindows(cb, 0)
    for h in reversed(hits):  # EnumWindows เรียงบน→ล่าง: ยกตัวล่างก่อน ตัวบนสุด (เช่น dialog) จบบนสุด
        for flag in (-1, -2):  # HWND_TOPMOST, HWND_NOTOPMOST
            u32.SetWindowPos(h, flag, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)  # NOSIZE|NOMOVE|NOACTIVATE
    time.sleep(0.3)


def _lp(x, y):
    return (y & 0xFFFF) << 16 | (x & 0xFFFF)


def click_xy(x, y, double=False, pids=None):
    """คลิกที่พิกัดจอ (x, y) โดยไม่ขยับเมาส์ — คืน hwnd ที่ได้รับข้อความ
    pids = โปรเซสที่ยอมให้รับคลิก (กันคลิกโดนหน้าต่างอื่นที่บังอยู่ เช่น Chrome)"""
    x, y = int(x), int(y)
    if REAL:
        from FlaUI.Core.Input import Mouse
        from System.Drawing import Point
        (Mouse.DoubleClick if double else Mouse.Click)(Point(x, y)); return 0
    h = u32.WindowFromPoint(wintypes.POINT(x, y))
    if not h:
        raise RuntimeError(f"ไม่มีหน้าต่างที่ ({x},{y})")
    if pids and _pid(h) not in pids:
        _raise(x, y, pids)  # มีหน้าต่างอื่นบัง (เช่น terminal ที่สั่งรัน) → ดึงหน้าต่างของแอปขึ้นบนสุดแล้วลองใหม่
        h = u32.WindowFromPoint(wintypes.POINT(x, y))
        if _pid(h) not in pids:
            raise RuntimeError(f"จุด ({x},{y}) ถูกหน้าต่างของโปรเซสอื่นบัง (pid {_pid(h)}) — ย้ายหน้าต่างนั้นออก")
    pt = wintypes.POINT(x, y); u32.ScreenToClient(h, ctypes.byref(pt)); lp = _lp(pt.x, pt.y)
    for _ in range(2 if double else 1):
        u32.PostMessageW(h, WM_MOUSEMOVE, 0, lp)
        u32.PostMessageW(h, WM_LBUTTONDOWN, MK_LBUTTON, lp)
        u32.PostMessageW(h, WM_LBUTTONUP, 0, lp)
    time.sleep(0.15)
    return h


def click_el(el, pids=None):
    """คลิกกลาง element (FlaUI AutomationElement) โดยไม่ขยับเมาส์"""
    r = el.BoundingRectangle
    if r.Width <= 0 or r.Height <= 0:
        raise RuntimeError("element ไม่มีพื้นที่บนจอ (ถูกซ่อน?)")
    return click_xy(r.X + r.Width / 2, r.Y + r.Height / 2, pids=pids)
