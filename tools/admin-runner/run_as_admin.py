"""สั่งรันงานแบบ Admin ผ่าน Task Scheduler "ClaudeAdminRunner" แล้วรอผล (ตั้งครั้งแรก: setup_task.ps1 แบบ Admin)

ใช้: python run_as_admin.py [--cwd DIR] [--timeout SEC] python -X utf8 <script.py> [args]
     python run_as_admin.py --cwd <repo> robot --outputdir out issues\\1234\\issue.robot
รันได้เฉพาะไฟล์ .py/.robot ใน repo นี้ (ดู run_admin.ps1)
งานค้าง/ไม่จบ: schtasks /end /tn ClaudeAdminRunner
"""
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
cwd, timeout = os.getcwd(), 3600
while args and args[0].startswith("--"):
    if args[0] == "--cwd":
        cwd = os.path.abspath(args[1]); args = args[2:]
    elif args[0] == "--timeout":
        timeout = int(args[1]); args = args[2:]
    else:
        break
if not args:
    sys.exit(__doc__)

out, done = os.path.join(HERE, "job_out.txt"), os.path.join(HERE, "job_done.txt")
for f in (out, done):
    try:
        if os.path.exists(f):
            os.remove(f)
    except PermissionError:
        sys.exit("มีงานเดิมยังรันอยู่ (job_out.txt ถูกล็อก) — รอให้จบ หรือ schtasks /end /tn ClaudeAdminRunner")
json.dump({"exe": args[0], "args": args[1:], "cwd": cwd},
          open(os.path.join(HERE, "job.json"), "w", encoding="utf-8"), ensure_ascii=False)

r = subprocess.run(["schtasks", "/run", "/tn", "ClaudeAdminRunner"], capture_output=True, text=True)
if r.returncode != 0:
    sys.exit("เรียก Task ไม่ได้ (รัน setup_task.ps1 แบบ Admin แล้วหรือยัง?): " + r.stdout + r.stderr)

pos, end = 0, time.time() + timeout
while time.time() < end:
    if os.path.exists(out):
        with open(out, encoding="utf-8-sig", errors="replace") as f:
            f.seek(pos); chunk = f.read(); pos = f.tell()
        if chunk:
            print(chunk, end="", flush=True)
    if os.path.exists(done):
        time.sleep(0.5)
        if os.path.exists(out):
            with open(out, encoding="utf-8-sig", errors="replace") as f:
                f.seek(pos); print(f.read(), end="")
        code = open(done).read().strip()
        print(f"\n[admin exit code {code}]")
        sys.exit(int(code) if code.lstrip("-").isdigit() else 1)
    time.sleep(2)
sys.exit("หมดเวลารอ — งานอาจยังรันอยู่ (เช่นติด dialog) ถ่ายภาพหน้าจอดูก่อน แล้ว schtasks /end /tn ClaudeAdminRunner")
