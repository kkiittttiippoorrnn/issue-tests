# ADAPTING — นำไปใช้ที่องค์กรใหม่ / ส่งให้ Claude ตัวอื่นปรับใช้

## สมมติฐานของโครงนี้ (ถ้าไม่ตรงต้องปรับตามหัวข้อ "ปรับเชิงลึก")
- ระบบที่ทดสอบเป็น **Windows desktop app** (ขับด้วย Robot Framework + RPA.Windows / UI Automation)
- ข้อมูลอยู่ใน **SQL database** ที่ query ได้ (ตัวอย่างใช้ SQL Server)
- มี **source code** ให้อ่าน (หา commit ของ fix, หา id ของ control, หาเงื่อนไขของ bug)
- ทำงานบน Windows + Claude Code

## ขั้นตอนพื้นฐาน (ประมาณ 15 นาที)
1. Clone repo แล้วติดตั้ง skill: `.\install-skill.ps1`
2. คัดลอก `claude-skill\test-issue\local.example.md` → `local.md` แล้วกรอกทุก `{ตัวแปร}` (ไม่มีให้เขียน "ไม่มี")
3. คัดลอก `local.example.ps1` → `local.ps1`
   - มีโปรเจกต์ Robot Framework ของแอปอยู่แล้ว → ตั้ง `AUTOMATION_HOME` ชี้ไปที่นั่น (ใช้ venv + keyword พื้นฐานของมัน)
   - ยังไม่มี → `python -m venv .venv` + `.venv\Scripts\pip install -r requirements.txt` แล้วเขียน keyword พื้นฐาน (launch / login / ปิดแอป) ใน `resources\keywords\`
4. ตั้ง locator dialog error ของแอปใน `resources\locators\app_screens.resource` (`${APP.ERROR_DIALOG}`)
5. ทดสอบโครง: คัดลอก `issues\_template` เป็น `issues\0000` แล้ว `.\run.ps1 -Issue 0000 -DryRun` ต้องผ่าน 1 test
6. ลองใช้จริง: `/test-issue <ID> manual` ก่อน (ไม่ต้องมี locator) แล้วค่อยใช้โหมด default

## ปรับเชิงลึก
| ต่างจากสมมติฐาน | ปรับที่ |
|---|---|
| เว็บแอป | เปลี่ยน `RPA.Windows` เป็น Browser/SeleniumLibrary ใน `issue_common.resource` + locator; ตัดหัวข้อ UIPI/BOM ใน SKILL.md |
| DB ไม่ใช่ SQL Server | `{DB_QUERY_TOOL}` ใน local.md + driver ใน `libraries/` และ requirements.txt |
| ไม่มี source code | ข้าม Phase 1 ข้อ 1-4 (ให้ user บอก build) และใช้ UI inspector อย่างเดียวในการหา locator |
| ไม่มี issue tracker ที่ Claude อ่านได้ | `{ISSUE_TRACKER}`: "ให้ user วาง" |
| ทีมไม่ใช้ภาษาไทย | SKILL.md เขียนภาษาไทยแต่สั่งให้ตอบตามภาษาของ user — แปล SKILL.md ได้ถ้าต้องการ |

## Prompt สำหรับส่งให้ Claude ตัวอื่นตั้งค่าให้
คัดลอกข้อความนี้ไปวางใน Claude Code ที่เปิดอยู่ในโฟลเดอร์ repo นี้:

```
อ่าน README.md และ ADAPTING.md ของ repo นี้ แล้วช่วยตั้งค่า skill /test-issue ให้ใช้กับระบบของเรา:
1. ถามข้อมูลที่ต้องใช้กรอก claude-skill/test-issue/local.md ทีละหมวด (ระบบที่ทดสอบ, paths, automation, issue tracker, DB)
   — สำรวจเครื่องเองก่อนถาม (หา source repo, โปรเจกต์ Robot Framework, เครื่องมือ DB) แล้วเสนอค่าให้ยืนยัน
2. สร้าง local.md และ local.ps1
3. ถ้าระบบต่างจาก "สมมติฐานของโครงนี้" ให้เสนอการปรับตามตาราง "ปรับเชิงลึก" ก่อนแก้
4. รัน install-skill.ps1 และ dry-run issues/_template ให้ผ่าน
ห้ามใส่ข้อมูลองค์กรลงไฟล์ที่ขึ้น git (ดู .gitignore)
```

## พัฒนาต่อเป็นของตัวเอง
- แก้ `SKILL.md` ได้เลย — ใช้ `{ตัวแปร}` แทนค่าเฉพาะองค์กรเสมอ แล้วเพิ่มตัวแปรใหม่ใน `local.example.md`
- keyword ที่ใช้ได้กับทุกแอป → `issue_common.resource`; keyword เฉพาะแอป → โปรเจกต์ใน `AUTOMATION_HOME`
- ก่อน commit: `git status` ต้องไม่มี `issues/<ID>/`, `local.md`, `local.ps1`
