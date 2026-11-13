"""flaui_kit — ชุดคุม UI ของแอป Windows ด้วย FlaUI (UIA3) ไฟล์เดียว ใช้ได้ทุกแอป

ใช้ได้ 2 แบบ (คำสั่งชุดเดียวกัน):
1) Robot Framework (ใน process เดียว ไม่ต้อง Run Process ทุกขั้น):
     Library    ${ISSUE_TESTS}/tools/flaui_kit.py    MyApp.exe
     Click      id:btnSave    window=FrmMain
2) CLI (หลายขั้นต่อการเรียก 1 ครั้ง คั่นด้วย ;):
     python -X utf8 flaui_kit.py --proc MyApp.exe [--exe <path>] click id:btnSave @FrmMain ; wait id:txtName @DlgEdit 10 ; message_box

Locator: "id:<AutomationId>" | "name:<Name>" | "type:<ControlType>" รวมกันด้วย | เช่น "type:Button|name:OK"
         ไม่มีคำนำหน้า = AutomationId · ต่อท้าย "#2" = ตัวที่ 2 ที่เจอ (ชื่อซ้ำ)
Window : AutomationId หรือ Name ของหน้าต่าง (รวม dialog ลูก) — CLI ใช้ "@<window>"

หลักที่ฝังไว้ (ดู SKILL.md "ประสิทธิภาพและเวลา"):
- หาหน้าต่างด้วย EnumWindows (~0.05 วิ) ไม่ใช้ Desktop.FindAllChildren
- รอแบบมีเงื่อนไข (wait / wait_gone / wait_window) ไม่ sleep ตายตัว
- คลิกแบบไม่ขยับเมาส์ (noclick.py: PostMessage + กันคลิกโดนหน้าต่างอื่น + ยกหน้าต่างเมื่อถูกบัง)
- เลือกรายการใน combo/dropdown ด้วย element จริง (ไม่ใช้พิกัด)
ไม่มีค่าเฉพาะแอป/เครื่องในไฟล์นี้ — ชื่อ process / exe ส่งเป็นพารามิเตอร์
"""
import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FlaUILibrary.pythonnetwrapper  # noqa: F401,E402  โหลด FlaUI ผ่าน pythonnet
from FlaUI.Core.Definitions import ControlType  # noqa: E402
from FlaUI.Core.Input import Keyboard  # noqa: E402
from FlaUI.Core.WindowsAPI import VirtualKeyShort  # noqa: E402
from FlaUI.UIA3 import UIA3Automation  # noqa: E402
from System import IntPtr, TimeSpan  # noqa: E402
from System.Diagnostics import Process  # noqa: E402

import noclick  # noqa: E402

u32 = ctypes.windll.user32
OK_NAMES = ("OK", "ตกลง", "&OK", "Yes", "ใช่")


def _g(f, d=None):
    try:
        return f()
    except Exception:  # noqa: BLE001
        return d


class FlaUIKit:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self, process, exe=None, workdir=None):
        """process = ชื่อ process (มีหรือไม่มี .exe ก็ได้) · exe/workdir = ใช้ตอน Start App"""
        self.proc = process[:-4] if process.lower().endswith(".exe") else process
        self.exe, self.workdir = exe, workdir
        self.auto = UIA3Automation()
        self.auto.ConnectionTimeout = TimeSpan.FromSeconds(10)
        self.auto.TransactionTimeout = TimeSpan.FromSeconds(20)
        self.cf = self.auto.ConditionFactory

    # ---------------- process / windows ----------------
    def pids(self):
        return {p.Id for p in Process.GetProcessesByName(self.proc)}

    def is_running(self):
        return bool(self.pids())

    def start_app(self, wait_window=None, timeout=120, restart=False):
        """เปิดแอป (restart=True ปิดตัวเดิมก่อน) แล้วรอหน้าต่าง wait_window"""
        if restart:
            self.kill_app()
        if not self.is_running():
            if not self.exe:
                raise AssertionError("ไม่ได้ระบุ exe สำหรับเปิดแอป")
            subprocess.Popen([self.exe], cwd=self.workdir or os.path.dirname(self.exe))
        if wait_window:
            return self.wait_window(wait_window, timeout)

    def kill_app(self, graceful_seconds=0):
        if graceful_seconds:
            subprocess.run(["taskkill", "/IM", self.proc + ".exe"], capture_output=True)
            end = time.time() + float(graceful_seconds)
            while self.is_running() and time.time() < end:
                time.sleep(0.5)
        subprocess.run(["taskkill", "/F", "/IM", self.proc + ".exe"], capture_output=True)
        time.sleep(1)

    def _top_windows(self):
        pids, hs = self.pids(), []

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def cb(h, _):
            pid = wintypes.DWORD(); u32.GetWindowThreadProcessId(h, ctypes.byref(pid))
            if pid.value in pids and u32.IsWindowVisible(h):
                hs.append(h)
            return True
        u32.EnumWindows(cb, 0)
        return [w for w in (_g(lambda h=h: self.auto.FromHandle(IntPtr(h))) for h in hs) if w is not None]

    def _all_windows(self):
        """หน้าต่างบนสุด + dialog ลูก (เรียงจากบนสุดตาม z-order, dialog ลูกมาก่อนหน้าต่างแม่)"""
        out = []
        for w in self._top_windows():
            out += _g(lambda: list(w.FindAllChildren(self.cf.ByControlType(ControlType.Window))), []) or []
            out.append(w)
        return out

    @staticmethod
    def _wid(w):
        return _g(lambda: w.AutomationId) or "", _g(lambda: w.Name) or ""

    def windows(self):
        """รายชื่อหน้าต่าง (AutomationId | Name)"""
        return [f"{a}|{n}" for a, n in (self._wid(w) for w in self._all_windows())]

    def _window(self, key):
        if key.startswith("#") and key[1:].isdigit():  # หน้าต่างลำดับที่ N ตาม z-order (#0 = บนสุด) — ใช้กับ popup ไม่มีชื่อ
            ws = self._all_windows()
            return ws[int(key[1:])] if int(key[1:]) < len(ws) else None
        for w in self._all_windows():
            a, n = self._wid(w)
            if key in (a, n):
                return w
        return None

    def wait_window(self, window, timeout=15):
        w = self._until(lambda: self._window(window), timeout)
        if w is None:
            raise AssertionError(f"ไม่พบหน้าต่าง {window} ใน {timeout}s · มี: {self.windows()}")
        return w

    def wait_window_gone(self, window, timeout=15):
        if self._until(lambda: self._window(window) is None, timeout) is None:
            raise AssertionError(f"หน้าต่าง {window} ยังไม่ปิดใน {timeout}s")

    def window_should_exist(self, window, exists=True):
        has = self._window(window) is not None
        if has != (str(exists).lower() in ("true", "1", "yes")):
            raise AssertionError(f"หน้าต่าง {window} {'ไม่มี' if exists else 'ยังมีอยู่'} · มี: {self.windows()}")

    def close_window(self, window, timeout=5):
        """ปิดหน้าต่างด้วย WM_CLOSE (ไม่บล็อก) — ใช้แทนปุ่มยกเลิกที่รับคลิกไม่ติด"""
        w = self._window(window)
        if w is None:
            return "none"
        u32.PostMessageW(int(str(w.Properties.NativeWindowHandle.Value)), 0x0010, 0, 0)
        self.wait_window_gone(window, timeout)
        return "closed"

    # ---------------- find ----------------
    def _cond(self, locator):
        conds = []
        for part in locator.split("|"):
            k, _, v = part.partition(":") if ":" in part else ("id", None, part)
            if k == "id":
                conds.append(self.cf.ByAutomationId(v))
            elif k == "name":
                conds.append(self.cf.ByName(v))
            elif k == "type":
                conds.append(self.cf.ByControlType(getattr(ControlType, v)))
            else:
                raise AssertionError("locator ไม่รู้จัก: " + part)
        c = conds[0]
        for x in conds[1:]:
            c = c.And(x)
        return c

    def _activate_of(self, el):
        """ดึงหน้าต่างของ element ขึ้นหน้าสุด (ก่อนพิมพ์ — คีย์บอร์ดไปที่หน้าต่าง foreground เท่านั้น)"""
        cur, walker = el, self.auto.TreeWalkerFactory.GetControlViewWalker()
        for _ in range(30):
            h = _g(lambda: int(str(cur.Properties.NativeWindowHandle.Value)), 0)
            if h:
                return noclick.activate(h)
            cur = _g(lambda: walker.GetParent(cur))
            if cur is None:
                break
        return False

    def activate_window(self, window):
        """ดึงหน้าต่างขึ้นหน้าสุด"""
        return self._activate_of(self.wait_window(window, 5))

    def _find_now(self, locator, window=None):
        nth = 1
        if "#" in locator and locator.rsplit("#", 1)[1].isdigit():
            locator, nth = locator.rsplit("#", 1)[0], int(locator.rsplit("#", 1)[1])
        cond = self._cond(locator)
        roots = [self._window(window)] if window else self._all_windows()
        hits = []
        for r in roots:
            if r is None:
                continue
            for e in _g(lambda: list(r.FindAllDescendants(cond)), []) or []:
                if _g(lambda e=e: e.IsOffscreen, None) is not True:  # ซ่อนอยู่ = ข้าม · บอกสถานะไม่ได้ (เช่นช่องใน Save As) = รับ
                    hits.append(e)
            if len(hits) >= nth:
                return hits[nth - 1]
        return None

    @staticmethod
    def _until(fn, timeout, every=0.2):
        end = time.time() + float(timeout)
        while True:
            r = _g(fn)
            if r:
                return r
            if time.time() >= end:
                return None
            time.sleep(every)

    def find(self, locator, window=None, timeout=5):
        e = self._until(lambda: self._find_now(locator, window), timeout)
        if e is None:
            raise AssertionError(f"ไม่พบ {locator}" + (f" ในหน้าต่าง {window}" if window else "") + f" ({timeout}s)")
        return e

    def wait(self, locator, window=None, timeout=15):
        self.find(locator, window, timeout)
        return "OK"

    def wait_gone(self, locator, window=None, timeout=15):
        if self._until(lambda: self._find_now(locator, window) is None, timeout) is None:
            raise AssertionError(f"{locator} ยังอยู่หลัง {timeout}s")

    def element_should_exist(self, locator, window=None, exists=True):
        has = self._find_now(locator, window) is not None
        if has != (str(exists).lower() in ("true", "1", "yes")):
            raise AssertionError(f"{locator} {'ไม่มี' if exists else 'ยังมีอยู่'}")

    # ---------------- actions ----------------
    def click(self, locator, window=None, timeout=5, double=False):
        """คลิกแบบไม่ขยับเมาส์ (PostMessage) — ใช้ได้กับปุ่มที่เปิด modal ด้วย"""
        e = self.find(locator, window, timeout)
        r = e.BoundingRectangle
        noclick.click_xy(r.X + r.Width / 2, r.Y + r.Height / 2, double=str(double).lower() in ("true", "1"), pids=self.pids())
        return "clicked"

    def invoke(self, locator, window=None, timeout=5):
        """UIA Invoke — ห้ามใช้กับปุ่มที่เปิด modal (ค้าง) ให้ใช้ click"""
        self.find(locator, window, timeout).Patterns.Invoke.Pattern.Invoke()
        return "invoked"

    def type_text(self, locator, text, window=None, clear=True, timeout=5):
        """focus แล้วพิมพ์ (ไม่คลิก) · text = "" + clear ล้างช่อง"""
        e = self.find(locator, window, timeout)
        self._activate_of(e)
        e.Focus(); time.sleep(0.15)
        if str(clear).lower() in ("true", "1"):
            Keyboard.TypeSimultaneously(VirtualKeyShort.CONTROL, VirtualKeyShort.KEY_A)
            Keyboard.Type(VirtualKeyShort.DELETE)
        if text:
            Keyboard.Type(text)
        return "typed"

    def set_value(self, locator, text, window=None, timeout=5):
        e = self.find(locator, window, timeout)
        e.Patterns.Value.Pattern.SetValue(text)
        return self.get_value(locator, window)

    def press_keys(self, keys, locator=None, window=None):
        """keys คั่นด้วย | เช่น "M014|ENTER" · ชื่อปุ่มตัวใหญ่ = VirtualKeyShort · locator = focus ก่อน · window อย่างเดียว = ดึงหน้าต่างขึ้นก่อน"""
        if locator:
            e = self.find(locator, window)
            self._activate_of(e); e.Focus(); time.sleep(0.15)
        elif window:
            self.activate_window(window)
        for tok in keys.split("|"):
            Keyboard.Type(getattr(VirtualKeyShort, tok)) if hasattr(VirtualKeyShort, tok) else Keyboard.Type(tok)
            time.sleep(0.3)  # ช่องสแกน/ค้นหาหลายแอปทำงานตอน TextChanged — เร็วกว่านี้ ENTER มาก่อนประมวลผลเสร็จ
        return "pressed"

    def get_value(self, locator, window=None, timeout=5):
        e = self.find(locator, window, timeout)
        v = _g(lambda: e.Patterns.Value.Pattern.Value.Value)
        return v if v is not None else (_g(lambda: e.Name) or "")

    def select_item(self, combo, item, window=None, nth=1, timeout=8):
        """เลือกรายการใน combo/dropdown (WinForms / DevExpress) ด้วย element จริง
        1) ListItem ลูกของ combo → SelectionItem.Select()
        2) DevExpress LookUp: ล้างแล้วตั้งค่าข้อความ → popup ที่กรองแล้วเด้ง (หรือรับข้อความเป็นค่าเลย)
           DevExpress CheckedCombo (มี List ลูก) / WinForms: เปิดด้วยปุ่มลูก/ExpandCollapse → ติ๊ก CheckBox แล้วกด OK ของ popup
        หมายเหตุ: WinForms ComboBox แบบพิมพ์ได้ที่ชื่อซ้ำ แอปจะจับชื่อแรกเองตอนเสียโฟกัส — nth>1 อาจไม่มีผล (ข้อจำกัดของแอป)
        3) หา ListItem/CheckBox (ตาม Name) หรือ DataItem (ตาม Name/Value) ที่มองเห็นในทุกหน้าต่างของ process → คลิกตัวที่ nth
        คืนค่าที่ combo แสดงหลังเลือก"""
        c = self.find(combo, window)
        nth = int(nth)
        li = [x for x in _g(lambda: list(c.FindAllDescendants(self.cf.ByControlType(ControlType.ListItem))), []) or []
              if _g(lambda x=x: x.Name) == item]
        if len(li) >= nth and _g(lambda: li[nth - 1].Patterns.SelectionItem.Pattern.Select(), "x") is None:
            time.sleep(0.3)
            return self._combo_text(c)
        def visible_items():
            out = []
            for w in self._all_windows():
                for t in (ControlType.ListItem, ControlType.DataItem, ControlType.CheckBox):
                    for x in _g(lambda w=w, t=t: list(w.FindAllDescendants(self.cf.ByControlType(t))), []) or []:
                        if _g(lambda x=x: x.IsOffscreen, True) is not False:
                            continue
                        val = _g(lambda x=x: x.Patterns.Value.Pattern.Value.Value) if t == ControlType.DataItem else None
                        if item in (_g(lambda x=x: x.Name), val):
                            out.append(x)
            return out if len(out) >= nth else None
        # DevExpress LookUp/Combo: พิมพ์ค่าลงช่อง → popup ที่กรองแล้วเด้งเอง (ปุ่ม Open ใน edit รับคลิก PostMessage ไม่ติด)
        hits = None
        checked = _g(lambda: c.FindFirstChild(self.cf.ByControlType(ControlType.List))) is not None  # DevExpress CheckedComboBoxEdit
        if not checked:
            _g(lambda: c.Patterns.Value.Pattern.SetValue(""))  # ล้างก่อน — ตั้งค่าเดิมซ้ำ popup ไม่เด้ง
        if not checked and _g(lambda: c.Patterns.Value.Pattern.SetValue(item), "x") is None:
            hits = self._until(visible_items, 1.5)
            if not hits and nth == 1 and self._combo_text(c) == item:
                return item  # DevExpress LookUp รับข้อความที่ตรงรายการเป็นค่าที่เลือกแล้ว (ตรวจแล้ว: บันทึก ReasonId ถูก)
        if not hits:  # WinForms ComboBox / dropdown ทั่วไป: เปิดด้วยปุ่มลูกหรือ ExpandCollapse
            btn = _g(lambda: c.FindFirstChild(self.cf.ByControlType(ControlType.Button)))
            if btn is not None:
                noclick.click_el(btn, self.pids())
            else:
                _g(lambda: c.Patterns.ExpandCollapse.Pattern.Expand())
            hits = self._until(visible_items, timeout)
        if not hits:
            raise AssertionError(f"ไม่พบรายการ '{item}' (ตัวที่ {nth}) ใน dropdown ของ {combo}")
        h = hits[nth - 1]
        noclick.click_el(h, self.pids()); time.sleep(0.4)
        if _g(lambda: h.ControlType) == ControlType.CheckBox:  # checked combo: ติ๊กแล้วกด OK ของ popup
            ok = self._until(lambda: next((b for w in self._all_windows()
                                           for b in _g(lambda w=w: list(w.FindAllDescendants(self.cf.ByControlType(ControlType.Button))), []) or []
                                           if _g(lambda b=b: b.Name) in OK_NAMES and _g(lambda b=b: b.IsOffscreen, True) is False
                                           and _g(lambda b=b: b.BoundingRectangle.Y, 0) > _g(lambda: c.BoundingRectangle.Y, 0)), None), 3)
            if ok is not None:
                noclick.click_el(ok, self.pids()); time.sleep(0.4)
        return self._combo_text(c)

    @staticmethod
    def _combo_text(c):
        return _g(lambda: c.Patterns.Value.Pattern.Value.Value) or _g(lambda: c.Name) or ""

    # ---------------- dialogs ----------------
    def message_box(self, timeout=8, expected=None, known=None, screenshot=None, button=None):
        """รอกล่องข้อความ (หน้าต่าง/dialog ที่ไม่อยู่ใน known และมีปุ่ม) → อ่านข้อความ → (ถ่ายภาพ) → กดปุ่ม
        known = รายชื่อหน้าต่างหลักคั่นด้วย , ที่ไม่นับเป็นกล่องข้อความ · expected = ข้อความที่ต้องมี
        ไม่มีกล่องข้อความ → คืน "" (ถ้าระบุ expected จะ fail)"""
        known = set((known or "").split(",")) - {""}

        def box():
            for d in self._all_windows():
                a, n = self._wid(d)
                if a in known or n in known:
                    continue
                if _g(lambda d=d: d.FindFirstDescendant(self.cf.ByControlType(ControlType.Button))) is not None:
                    return d
        b = self._until(box, timeout)
        if b is None:
            if expected:
                raise AssertionError(f"ไม่มีกล่องข้อความ (คาด '{expected}')")
            return ""
        texts = [t for t in (_g(lambda x=x: x.Name) for x in b.FindAllDescendants(self.cf.ByControlType(ControlType.Text))) if t]
        msg = " / ".join(texts)
        if screenshot:
            _g(lambda: b.CaptureToFile(screenshot))
        names = (button,) if button else OK_NAMES
        btn = next((x for x in b.FindAllDescendants(self.cf.ByControlType(ControlType.Button)) if _g(lambda x=x: x.Name) in names), None)
        if btn is None:
            raise AssertionError(f"กล่องข้อความไม่มีปุ่ม {names}: {msg}")
        noclick.click_el(btn, self.pids()); time.sleep(0.5)
        if expected and expected not in msg:
            raise AssertionError(f"ข้อความ = '{msg}' ไม่มี '{expected}'")
        return msg

    def no_error_dialog(self, known):
        """ต้องไม่มีหน้าต่าง/dialog อื่นนอกจาก known (คั่นด้วย ,)"""
        known = set(known.split(","))
        extra = [f"{a}|{n}" for a, n in (self._wid(w) for w in self._all_windows())
                 if (a or n) and a not in known and n not in known]
        if extra:
            raise AssertionError("พบหน้าต่าง/dialog: " + "; ".join(extra))
        return "no dialog"

    # ---------------- read ----------------
    def grid_rows(self, grid, window=None):
        """อ่านแถวที่มองเห็นของ grid (DevExpress/WinForms) → list ของ dict {หัวคอลัมน์: ค่า} จาก DataItem "<หัว> row N" """
        g = self.find(grid, window)
        rows = {}
        for d in _g(lambda: list(g.FindAllDescendants(self.cf.ByControlType(ControlType.DataItem))), []) or []:
            nm = _g(lambda d=d: d.Name) or ""
            if " row " not in nm:
                continue
            head, _, n = nm.rpartition(" row ")
            rows.setdefault(n, {})[head] = _g(lambda d=d: d.Patterns.Value.Pattern.Value.Value) or ""
        return [rows[k] for k in sorted(rows, key=lambda x: int(x) if x.isdigit() else 0)]

    def screenshot(self, path, window=None, locator=None):
        """ถ่ายภาพ element / หน้าต่าง / หน้าต่างบนสุดของแอป"""
        if locator:
            el = self.find(locator, window)
        else:
            el = self._window(window) if window else (self._top_windows() or [None])[0]
        if el is None:
            raise AssertionError("ไม่มีหน้าต่างให้ถ่าย")
        el.CaptureToFile(path)
        return path

    def rect(self, locator, window=None, timeout=5):
        """กรอบของ element → [x, y, width, height] (ใช้ตรวจตำแหน่ง เช่นแผงที่เลื่อนเข้า/ออก)"""
        r = self.find(locator, window, timeout).BoundingRectangle
        return [int(r.X), int(r.Y), int(r.Width), int(r.Height)]

    @staticmethod
    def close_any_window(title, timeout=10):
        """รอหน้าต่างชื่อ title ของโปรเซสใดก็ได้ (เช่นกล่อง Send fail ของ service) แล้วปิด (IDOK → WM_CLOSE)
        ไม่บล็อก · ใช้แทน sleep ประมาณเวลา: คืนทันทีที่หน้าต่างขึ้นและถูกปิด · ไม่ขึ้นใน timeout → คืน 0"""
        def find():
            hits = []

            @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            def cb(h, _):
                n = u32.GetWindowTextLengthW(h)
                if n and u32.IsWindowVisible(h):
                    b = ctypes.create_unicode_buffer(n + 1); u32.GetWindowTextW(h, b, n + 1)
                    if b.value == title:
                        hits.append(h)
                return True
            u32.EnumWindows(cb, 0)
            return hits
        end, closed = time.time() + float(timeout), 0
        while time.time() < end:
            hs = find()
            if hs:
                for h in hs:
                    u32.PostMessageW(h, 0x0111, 1, 0); closed += 1  # WM_COMMAND IDOK
                time.sleep(0.8)
                for h in find():
                    u32.PostMessageW(h, 0x0010, 0, 0)  # WM_CLOSE
                break
            time.sleep(0.3)
        return closed

    def at_point(self, x, y, window=None):
        """element ที่จุด (x, y) — พิกัดภายในหน้าต่างถ้าระบุ window ไม่งั้นพิกัดจอ · ใช้แปลงพิกัดเดิมเป็น locator
        คืน id/name/type ของ element และบรรพบุรุษ 4 ชั้น"""
        from System.Drawing import Point
        x, y = int(x), int(y)
        if window:
            r = self.wait_window(window, 5).BoundingRectangle
            x, y = int(r.X) + x, int(r.Y) + y
        e = self.auto.FromPoint(Point(x, y))
        out, walker, cur = [], self.auto.TreeWalkerFactory.GetControlViewWalker(), e
        for i in range(5):
            if cur is None:
                break
            out.append(f"{'  ' * i}{_g(lambda: cur.ControlType)} id={_g(lambda: cur.AutomationId)} name={_g(lambda: cur.Name)} rect={_g(lambda: cur.BoundingRectangle)}")
            cur = _g(lambda: walker.GetParent(cur))
        return "\n".join(out)

    def dump(self, window=None, root=None, depth=6, save=None):
        """dump UI tree แบบจำกัดขอบเขต (หน้าต่างเดียว / element เดียว) — ใช้เฉพาะจุดที่แผนที่หน้าจอยังไม่มี แล้วบันทึกลงแผนที่"""
        start = self.find(root, window) if root else (self._window(window) if window else (self._top_windows() or [None])[0])
        out = []

        def walk(e, d):
            if _g(lambda: e.IsOffscreen) is True and d > 0:
                return
            v = _g(lambda: e.Patterns.Value.Pattern.Value.Value) if _g(lambda: e.Patterns.Value.IsSupported, False) else None
            out.append(f"{'  ' * d}{_g(lambda: e.ControlType)} id={_g(lambda: e.AutomationId)} name={_g(lambda: e.Name)}"
                       + (f" value={v}" if v not in (None, "") else ""))
            if d < int(depth):
                for c in _g(lambda: list(e.FindAllChildren()), []) or []:
                    walk(c, d + 1)
        walk(start, 0)
        text = "\n".join(out)
        if save:
            open(save, "w", encoding="utf-8").write(text + "\n")
        return text


flaui_kit = FlaUIKit  # Robot: Library  .../flaui_kit.py  <process>  (ชื่อ class ต้องตรงชื่อไฟล์)


# ---------------- CLI ----------------
def _cli(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not argv or argv[0] != "--proc":
        sys.exit(__doc__)
    rest, exe = argv[2:], None
    if rest[:1] == ["--exe"]:
        exe, rest = rest[1], rest[2:]
    kit = FlaUIKit(argv[1], exe)
    cmds, cur = [], []
    for t in rest:
        if t == ";":
            cmds.append(cur); cur = []
        else:
            cur.append(t)
    cmds.append(cur)
    t0, rc = time.time(), 0
    for cm in (c for c in cmds if c):
        name, args, kw = cm[0], [], {}
        for a in cm[1:]:
            if a.startswith("@"):
                kw["window"] = a[1:]
            elif "=" in a and a.split("=", 1)[0].isidentifier() and not a.startswith(("id:", "name:", "type:")):
                k, v = a.split("=", 1); kw[k] = v
            else:
                args.append(a)
        print(f">> [{time.time() - t0:.1f}s] {' '.join(cm)}", flush=True)
        if name == "sleep":
            time.sleep(float(args[0])); continue
        try:
            fn = getattr(kit, name)
            import inspect
            free = [p for p in inspect.signature(fn).parameters if p not in kw]
            kw.update(dict(zip(free, args)))  # positional ตามลำดับพารามิเตอร์ที่ยังไม่ระบุ (ข้าม window ที่ให้ด้วย @)
            r = fn(**kw)
            if r not in (None, ""):
                print(r if not isinstance(r, list) else "\n".join(map(str, r)))
        except Exception as e:  # noqa: BLE001
            print(f"ERR {type(e).__name__}: {e}"); rc = 1
            break
    print(f"done {time.time() - t0:.1f}s")
    sys.exit(rc)


if __name__ == "__main__":
    _cli(sys.argv[1:])
