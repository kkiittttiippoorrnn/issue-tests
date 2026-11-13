# issue-tests — โครงทดสอบราย issue + Claude Code skill `/test-issue` (v1.3)

Template สำหรับ Tester ที่ใช้ Claude Code ทดสอบ issue แบบครบวงจร:
อ่าน issue (Azure DevOps หรือ Jira) → หา build ที่มี fix → เตรียมข้อมูลทดสอบ → คุม UI ด้วย **FlaUI** + Robot Framework → ตรวจหน้าจอ + DB → รายงาน + automate เก็บเป็น regression → rollback

repo นี้เป็น **โครงเท่านั้น** — ไม่มีข้อมูลองค์กร ค่าเฉพาะองค์กร/เครื่องอยู่ในไฟล์ local ที่ถูก .gitignore
- นำไปใช้ที่องค์กรใหม่ หรือส่งให้ Claude ตัวอื่นปรับใช้ → [ADAPTING.md](ADAPTING.md)
- เริ่มใช้ครั้งแรก (ติดตั้ง + สอน Claude ให้ทำงานแบบทีม) → [SETUP_GUIDE.md](SETUP_GUIDE.md)
- ขั้นตอนเต็ม + ประวัติเวอร์ชัน → [claude-skill/test-issue/SKILL.md](claude-skill/test-issue/SKILL.md)

## ลำดับการทำงานต่อ 1 issue (กฎเหล็กของ skill)
ห้ามข้าม / สลับ / รวบขั้น — ขั้น ◆ Claude ต้องหยุดรอคำตอบของคุณ · ข้ามได้เฉพาะเมื่อคุณสั่งชัด (Claude จดเหตุผลลง `notes.md`)

1. `/clear` → `/test-issue <ID>`
2. อ่าน issue → ตรวจ fix/build จาก binary จริง → เช็ค DB
3. ◆ ขออนุญาต mock ข้อมูล (SQL + ค่าเดิม + `rollback.sql`)
4. ◆ ส่งสรุป Test Case 2 ชุด แล้วรอคำว่า **"เริ่ม"**
5. ◆ แจ้งก่อนคุมหน้าจอ → เทสทีละ TC (หน้าจอ + DB + หลักฐาน)
6. สรุปผล + ข้อความแปะ issue → `TestResult_<ID>.html` + `TestNote_<ID>.html`
7. Automate ก่อน rollback → ◆ Claude รันผ่าน → ◆ **คุณรันจาก terminal ของคุณเองผ่าน 1 รอบ**
8. ◆ ขออนุญาต rollback → รัน + ยืนยันค่ากลับ
9. บันทึก `notes.md` → ◆ คุณแจ้งผลใน issue tracker เอง (Claude ไม่โพสต์/ไม่เปลี่ยนสถานะ)

ข้อยกเว้นเฉพาะคน/องค์กร (เช่นช่วงเวลาที่เริ่มเทสได้ทันที) เขียนใน `local.md` เท่านั้น

## โครงสร้าง
```
issue-tests/
├── claude-skill/test-issue/
│   ├── SKILL.md              ขั้นตอนของ skill (ทั่วไป ใช้ {ตัวแปร} จาก local.md) + ประวัติเวอร์ชัน
│   ├── local.example.md      แม่แบบค่าเฉพาะองค์กร → คัดลอกเป็น local.md (ignored)
├── install-skill.ps1         junction ~/.claude/skills/test-issue → claude-skill/test-issue
├── run.ps1                   .\run.ps1 -Issue <ID> [-DryRun] [-Include TC1] [-RerunFailed] [-Variable K:V]
├── local.example.ps1         แม่แบบค่าเฉพาะเครื่องของ run.ps1 → คัดลอกเป็น local.ps1 (ignored)
├── requirements.txt          Robot Framework, robotframework-flaui, pyodbc, Pillow
├── issues/
│   ├── _template/            issue.robot, notes.md, rollback.sql, make_report.py (รายงาน HTML)
│   └── <ID>/                 งานจริงของแต่ละ issue (ignored ทั้งโฟลเดอร์) — <ID> ใช้ได้ทั้ง 12345 และ PROJ-123
├── resources/
│   ├── keywords/issue_common.resource   keyword ทั่วไปที่ใช้ซ้ำข้าม issue
│   └── locators/app_screens.resource    locator ที่ keyword ข้างบนใช้
├── libraries/                ตัวอย่าง library ตรวจ DB (SELECT อย่างเดียว) + HlMark.py (รูปหลักฐานมีกรอบ/ป้าย)
└── tools/
    ├── noclick.py            คลิกแบบไม่ขยับเมาส์ (PostMessage) + กันคลิกโดนหน้าต่างอื่น + ยกหน้าต่างแอปเมื่อถูกบัง
    ├── ui_step.py            ตัวกด UI แบบสั้น (FlaUI) รวมหลายขั้นในคำสั่งเดียว + snap ภาพทุกจอ
    └── admin-runner/         รันสคริปต์แบบ Admin ผ่าน Task Scheduler (แอปรันแบบ Admin แต่ terminal ไม่ใช่)
```

## สิ่งที่ไม่ขึ้น git
- `issues/<ID>/` — ผลเทส, notes, rollback, robot ของแต่ละ issue ที่มีข้อมูลจริง
- `claude-skill/test-issue/local.md` — path, ชื่อระบบ, DB, issue tracker, แผนที่หน้าจอ, ข้อยกเว้นของกฎเหล็ก
- `local.ps1` — ค่าเฉพาะเครื่องของ run.ps1
- `issues/**/evidence/` — report/screenshot จากการรัน

## ใช้งาน
ใน Claude Code:
```
/test-issue 1234          Claude คุม UI เอง (FlaUI)          · Jira: /test-issue POS-123
/test-issue 1234 manual   Claude ให้ขั้นตอน คุณกดเอง Claude ตรวจ DB
```
รันเทสซ้ำเอง — **CMD แบบ Run as administrator** (แอปรันแบบ Admin):
```bat
cd /d <โฟลเดอร์ repo>
powershell -ExecutionPolicy Bypass -File run.ps1 -Issue 1234 -DryRun
powershell -ExecutionPolicy Bypass -File run.ps1 -Issue 1234
powershell -ExecutionPolicy Bypass -File run.ps1 -Issue 1234 -Include TC2
```
ดูรายงานรอบล่าสุด:
```bat
cd /d <โฟลเดอร์ repo>\issues\1234\evidence
dir /b /ad /o-n 2026*
start "" <โฟลเดอร์บนสุด>\report.html
```
- ระหว่างรัน test คุมแอป — ไม่ต้องแตะเครื่อง (คลิกแบบไม่ขยับเมาส์ หน้าต่าง CMD เปิดค้างได้)
- automate นับว่าเสร็จเมื่อผ่านจาก terminal ของคุณเองอย่างน้อย 1 รอบ (ไม่ใช่แค่ผ่านใน runner ของ Claude)

## หลักการที่ skill บังคับ (สรุป — รายละเอียดใน SKILL.md)
- **FlaUI (UIA3) เป็นเครื่องมือหลัก** — ติดปัญหาให้แก้ตัวช่วย FlaUI ไม่เปลี่ยนไปวิธีอื่น
- **หา locator จากแผนที่หน้าจอ / UI tree ที่ export ไว้ก่อน** (`{SCREEN_MAP}`) → id จาก source → dump สดเฉพาะจุดที่ไม่รู้ แล้วบันทึกลงแผนที่ทันที
- **ความเร็ว:** หาหน้าต่างด้วย EnumWindows · รอแบบมีเงื่อนไข (`wait`/`waitgone`) แทน sleep · รวมหลายขั้นต่อ process · ข้ามการนำทางซ้ำ · DB check หนักจำกัดช่วง + คู่ขนาน · จดเวลาต่อ test
- **ทุก test ตรวจทั้งหน้าจอและ DB** · `setup.sql` คู่ `rollback.sql` ให้รันซ้ำได้
- Gate ที่ Claude ต้องถามเสมอ: แก้ข้อมูลใน DB, รัน UI ครั้งแรก, rollback, git commit/push

## รูปแบบผลงาน
รูปแบบ Test Case, รายงาน HTML (TestResult / TestNote), รูปหลักฐาน และ gotcha ของ UI automation
อยู่ใน `SKILL.md` หัวข้อ "รูปแบบผลงาน" — ทีมใช้ร่วมกัน ปรับได้ที่นั่นที่เดียว

## แอปต้องรันแบบ Admin
```powershell
# ครั้งเดียว ใน PowerShell แบบ Run as administrator
.\tools\admin-runner\setup_task.ps1
# จากนั้น Claude สั่งจาก terminal ธรรมดาได้
python tools\admin-runner\run_as_admin.py --cwd . python -X utf8 tools\ui_step.py --proc MyApp state
```
