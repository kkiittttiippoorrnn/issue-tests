"""ตัวกด UI แบบสั้น (FlaUI/UIA3) — ใช้สำรวจ/เทสเร็วโดยไม่ต้องเขียน .robot · รวมหลายขั้นในคำสั่งเดียว

ใช้: python -X utf8 tools\\ui_step.py --proc <ชื่อ process ไม่มี .exe> [--ev <โฟลเดอร์ภาพ>] <step> [<step> ...]
     (แอปรันแบบ Admin → เรียกผ่าน tools\\admin-runner\\run_as_admin.py)
step:
  state                         รายชื่อหน้าต่างของ process (+ หน้าต่างลูก/dialog)
  click:<id>[@win]              คลิก (Button = เมาส์จริง, อื่นๆ ลอง Invoke/Select ก่อน)
  mclick:<id>[@win]             คลิกเมาส์จริงเสมอ (ปุ่มที่เปิด modal — Invoke จะค้าง)
                                id ขึ้นต้น name: = หาด้วยชื่อที่แสดง เช่น mclick:name:บันทึก
  type:<id>[@win]=<ข้อความ>      คลิกช่องแล้วพิมพ์ด้วยคีย์บอร์ดจริง (ใส่ |ENTER ท้ายเพื่อกด Enter)
  front:<win>                   ดึงหน้าต่างขึ้นหน้า
  sleep:<วินาที>                 รอเฉยๆ (ใช้ตอนรอฟีเจอร์นับเวลาว่าง — ห้ามเรียก UIA ระหว่างรอ)
  idle:<วินาที>                  รอพร้อมพิมพ์สถานะทุก 5 วิ (ช้ากว่าเวลาที่ตั้ง เพราะเรียก UIA)
  jiggle                        กด Shift 1 ครั้ง = input จริง (รีเซ็ตเวลาว่างของระบบ)
  find:<ชื่อ>                    แสดงทุก element ที่ชื่อนี้ (id, enabled, offscreen, ตำแหน่ง)
  tog:<id>[@win]                สถานะ checkbox
  snap:<tag>                    รายชื่อหน้าต่าง + ภาพทุกจอ → <ev>\\<tag>.png

หมายเหตุ: Invoke และ Mouse.MoveBy ไม่นับเป็น input ของ GetLastInputInfo — ฟีเจอร์ Auto Logout จะเห็นเครื่องว่างตลอด
"""
import os
import sys
import time

import FlaUILibrary.pythonnetwrapper  # noqa: F401  (pip install robotframework-flaui)
from FlaUI.UIA3 import UIA3Automation
from FlaUI.Core.Definitions import ControlType
from FlaUI.Core.Input import Keyboard, Wait
from FlaUI.Core.WindowsAPI import VirtualKeyShort
from System import TimeSpan
from System.Diagnostics import Process

auto = UIA3Automation()
auto.ConnectionTimeout = TimeSpan.FromSeconds(10)
auto.TransactionTimeout = TimeSpan.FromSeconds(20)
cf = auto.ConditionFactory
PROC, EV = None, os.path.join(os.getcwd(), "evidence")


def safe(f, d=""):
    try:
        return f()
    except Exception:
        return d


def wins(wid=None):
    pids = {p.Id for p in Process.GetProcessesByName(PROC)}
    ws = [w for w in safe(lambda: list(auto.GetDesktop().FindAllChildren()), [])
          if safe(lambda: w.Properties.ProcessId.Value, -1) in pids]
    return ws if wid in (None, "") else [w for w in ws if safe(lambda: w.AutomationId) == wid]


def find(target, wid=None, wait=10):
    cond = cf.ByName(target[5:]) if target.startswith("name:") else cf.ByAutomationId(target)
    end = time.time() + wait
    while True:
        for w in wins(wid):
            el = safe(lambda: w.FindFirstDescendant(cond), None)
            if el is not None:
                return el
        if time.time() > end:
            raise RuntimeError(f"ไม่พบ {target}" + (f" ในหน้าต่าง {wid}" if wid else ""))
        time.sleep(0.5)


def split_target(s):
    tgt, _, wid = s.partition("@")
    return tgt, wid or None


def idle_ms():
    import ctypes

    class LII(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    li = LII(); li.cbSize = ctypes.sizeof(LII)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li))
    return ctypes.windll.kernel32.GetTickCount() - li.dwTime


def window_lines():
    out = []
    for w in wins():
        out.append(f"top id={safe(lambda: w.AutomationId)} name={safe(lambda: w.Name)} rect={safe(lambda: w.BoundingRectangle)}")
        for c in safe(lambda: list(w.FindAllChildren(cf.ByControlType(ControlType.Window))), []):
            out.append(f"   child id={safe(lambda: c.AutomationId)} name={safe(lambda: c.Name)}")
    return out


def snap(tag):
    print(f"--- snap {tag} @ {time.strftime('%H:%M:%S')}")
    for line in window_lines():
        print("   ", line)
    try:
        from PIL import ImageGrab
        os.makedirs(EV, exist_ok=True)
        p = os.path.join(EV, f"{tag}.png")
        ImageGrab.grab(all_screens=True).save(p)
        print("    shot", p)
    except Exception as e:
        print("    shot fail", e)


def do(step):
    kind, _, arg = step.partition(":")
    if step == "state":
        print("\n".join(window_lines()) or "(ไม่พบหน้าต่างของ process)")
    elif kind in ("click", "mclick"):
        el = find(*split_target(arg))
        if kind == "mclick" or safe(lambda: str(el.ControlType)) == "Button":
            el.Click(True); print("OK mouse", arg)
            return
        for how in ("invoke", "select"):
            try:
                (el.Patterns.Invoke.Pattern.Invoke() if how == "invoke" else el.Patterns.SelectionItem.Pattern.Select())
                Wait.UntilInputIsProcessed(TimeSpan.FromMilliseconds(500)); print("OK", how, arg)
                return
            except Exception:
                continue
        el.Click(True); print("OK mouse", arg)
    elif kind == "type":
        tgt, _, text = arg.partition("=")
        el = find(*split_target(tgt)); el.Click(True); time.sleep(0.3)
        for tok in text.split("|"):
            Keyboard.Type(getattr(VirtualKeyShort, tok)) if hasattr(VirtualKeyShort, tok) else Keyboard.Type(tok)
            time.sleep(0.2)
        print("typed", text)
    elif kind == "front":
        wins(arg)[0].SetForeground(); print("front", arg)
    elif kind == "sleep":
        time.sleep(float(arg))
    elif kind == "idle":
        t0 = time.time()
        while time.time() - t0 < float(arg):
            time.sleep(5)
            print(f"    idle {int(time.time() - t0)}s sys_idle_ms={idle_ms()} windows={len(wins())}")
    elif step == "jiggle":
        b = idle_ms()
        Keyboard.Press(VirtualKeyShort.SHIFT); time.sleep(0.1); Keyboard.Release(VirtualKeyShort.SHIFT); time.sleep(0.2)
        print("    jiggle", time.strftime("%H:%M:%S"), "sys_idle_ms", b, "->", idle_ms())
    elif kind == "find":
        for w in wins():
            for el in safe(lambda: list(w.FindAllDescendants(cf.ByName(arg))), []):
                print("   ", safe(lambda: str(el.ControlType)), "id=", safe(lambda: el.AutomationId), "win=", safe(lambda: w.AutomationId),
                      "enabled=", safe(lambda: el.IsEnabled), "off=", safe(lambda: el.IsOffscreen), safe(lambda: el.BoundingRectangle))
    elif kind == "tog":
        el = find(*split_target(arg))
        print("   toggle", arg, safe(lambda: el.Patterns.Toggle.Pattern.ToggleState.Value), "enabled=", safe(lambda: el.IsEnabled))
    elif kind == "snap":
        snap(arg)
    else:
        raise RuntimeError(f"step ไม่รู้จัก: {step}")


if __name__ == "__main__":
    a = sys.argv[1:]
    while a and a[0].startswith("--"):
        if a[0] == "--proc":
            PROC = a[1].removesuffix(".exe"); a = a[2:]
        elif a[0] == "--ev":
            EV = os.path.abspath(a[1]); a = a[2:]
        else:
            break
    if not PROC or not a:
        sys.exit(__doc__)
    for s in a:
        print(">>", s)
        try:
            do(s)
        except Exception as e:
            print("ERROR", s, e)
            snap("error_" + time.strftime("%H%M%S"))
            sys.exit(1)
