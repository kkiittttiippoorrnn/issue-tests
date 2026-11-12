# issue-tests — โครงทดสอบราย issue + Claude Code skill `/test-issue`

Template สำหรับ Tester ที่ใช้ Claude Code ทดสอบ issue แบบครบวงจร:
อ่าน issue → หา build ที่มี fix → เตรียมข้อมูลทดสอบ → รันเทส UI (Robot Framework) → ตรวจหน้าจอ + DB → สรุปผล + rollback

repo นี้เป็น **โครงเท่านั้น** — ไม่มีข้อมูลองค์กร ค่าเฉพาะองค์กร/เครื่องอยู่ในไฟล์ local ที่ถูก .gitignore
นำไปใช้ที่องค์กรใหม่ หรือส่งให้ Claude ตัวอื่นปรับใช้ → อ่าน [ADAPTING.md](ADAPTING.md)
เริ่มใช้ครั้งแรก (ติดตั้ง + สอน Claude ให้ทำงานแบบทีม) → อ่าน [SETUP_GUIDE.md](SETUP_GUIDE.md)

## โครงสร้าง
```
issue-tests/
├── claude-skill/test-issue/
│   ├── SKILL.md              ขั้นตอนของ skill (ทั่วไป ใช้ {ตัวแปร} จาก local.md)
│   ├── local.example.md      แม่แบบค่าเฉพาะองค์กร → คัดลอกเป็น local.md (ignored)
├── install-skill.ps1         junction ~/.claude/skills/test-issue → claude-skill/test-issue
├── run.ps1                   .\run.ps1 -Issue <ID> [-DryRun] [-Include TC1] [-RerunFailed]
├── local.example.ps1         แม่แบบค่าเฉพาะเครื่องของ run.ps1 → คัดลอกเป็น local.ps1 (ignored)
├── requirements.txt          ใช้เมื่อไม่มีโปรเจกต์ automation เดิม
├── issues/
│   ├── _template/            issue.robot, notes.md, rollback.sql, make_report.py (รายงาน HTML)
│   └── <ID>/                 งานจริงของแต่ละ issue (ignored ทั้งโฟลเดอร์)
├── resources/
│   ├── keywords/issue_common.resource   keyword ทั่วไปที่ใช้ซ้ำข้าม issue
│   └── locators/app_screens.resource    locator ที่ keyword ข้างบนใช้
├── libraries/                ตัวอย่าง library ตรวจ DB (SELECT อย่างเดียว) + HlMark.py (รูปหลักฐานมีกรอบ/ป้าย)
└── tools/
    ├── ui_step.py            ตัวกด UI แบบสั้น (FlaUI) รวมหลายขั้นในคำสั่งเดียว + snap ภาพทุกจอ
    └── admin-runner/         รันสคริปต์แบบ Admin ผ่าน Task Scheduler (แอปรันแบบ Admin แต่ terminal ไม่ใช่)
```

## สิ่งที่ไม่ขึ้น git
- `issues/<ID>/` — ผลเทส, notes, rollback ที่มีข้อมูลจริง
- `claude-skill/test-issue/local.md` — path, ชื่อระบบ, กติกาเฉพาะโค้ด/DB ขององค์กร
- `local.ps1` — ค่าเฉพาะเครื่องของ run.ps1
- `issues/**/evidence/` — report/screenshot จากการรัน

## ใช้งาน
```powershell
.\install-skill.ps1                    # ครั้งแรก
# ใน Claude Code
/test-issue 1234                       # Claude รันเทส UI เอง
/test-issue 1234 manual                # Claude ให้ขั้นตอน คุณกดเอง Claude ตรวจ DB
# รันเทสซ้ำเอง
.\run.ps1 -Issue 1234 -DryRun
.\run.ps1 -Issue 1234
```

ระหว่างรันจริง test คุมเมาส์/คีย์บอร์ด — ห้ามแตะเครื่อง

## รูปแบบผลงาน
รูปแบบ Test Case, รายงาน HTML (TestResult / TestNote), รูปหลักฐาน และ gotcha ของ UI automation
อยู่ใน `claude-skill/test-issue/SKILL.md` หัวข้อ "รูปแบบผลงาน" — ทีมใช้ร่วมกัน ปรับได้ที่นั่นที่เดียว

## แอปต้องรันแบบ Admin
```powershell
# ครั้งเดียว ใน PowerShell แบบ Run as administrator
.\tools\admin-runner\setup_task.ps1
# จากนั้นสั่งจาก terminal ธรรมดาได้
python tools\admin-runner\run_as_admin.py --cwd . python -X utf8 tools\ui_step.py --proc MyApp state
```
