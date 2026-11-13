# ADAPTING — นำไปใช้ที่องค์กรใหม่ / ส่งให้ Claude ตัวอื่นปรับใช้

## สมมติฐานของโครงนี้ (ถ้าไม่ตรงต้องปรับตามหัวข้อ "ปรับเชิงลึก")
- ระบบที่ทดสอบเป็น **Windows desktop app** (คุม UI ด้วย **FlaUI (UIA3)** เป็นหลัก + Robot Framework)
- ข้อมูลอยู่ใน **SQL database** ที่ query ได้ (ตัวอย่างใช้ SQL Server)
- มี **source code** ให้อ่าน (หา commit ของ fix, หา id ของ control, หาเงื่อนไขของ bug)
- issue tracker เป็น **Azure DevOps หรือ Jira** (หรือไม่มี — ให้ user วางเนื้อหา)
- ทำงานบน Windows + Claude Code

## ขั้นตอนพื้นฐาน (ประมาณ 15 นาที)
1. Clone repo แล้วติดตั้ง skill: `.\install-skill.ps1`
2. คัดลอก `claude-skill\test-issue\local.example.md` → `local.md` แล้วกรอกทุก `{ตัวแปร}` (ไม่มีให้เขียน "ไม่มี")
3. คัดลอก `local.example.ps1` → `local.ps1`
   - มีโปรเจกต์ Robot Framework ของแอปอยู่แล้ว → ตั้ง `AUTOMATION_HOME` ชี้ไปที่นั่น (ใช้ venv + keyword พื้นฐานของมัน)
   - ยังไม่มี → `python -m venv .venv` + `.venv\Scripts\pip install -r requirements.txt` แล้วเขียน keyword พื้นฐาน (launch / login / ปิดแอป) ใน `resources\keywords\`
4. ตั้ง locator dialog error ของแอปใน `resources\locators\app_screens.resource` (`${APP.ERROR_DIALOG}`)
4.1 ตั้งค่าใหม่ของ v1.1–1.3 ใน `local.md`:
   - tracker: `{ISSUE_TRACKER}` `{ISSUE_KEY_FORMAT}` `{TEST_SCENARIO_SOURCE}` `{FIX_LINK_SOURCE}` `{RESULT_POST_FORMAT}` (ตัวอย่างทั้ง AzDO และ Jira อยู่ใน `local.example.md`)
   - UI: `{FLAUI_HELPERS}` (โฟลเดอร์สคริปต์ตัวช่วย FlaUI ของแอป — ค่าเริ่มต้น `tools\`) และ `{SCREEN_MAP}` (แผนที่หน้าจอ + โฟลเดอร์ UI tree ที่ export ไว้ — สร้างไฟล์ index ว่างไว้ก่อนได้ Claude จะเติมเองเมื่อ dump หน้าใหม่)
   - ข้อยกเว้นของกฎเหล็ก (ถ้ามี) เช่นช่วงเวลาที่เริ่มเทสได้ทันที
5. ทดสอบโครง: คัดลอก `issues\_template` เป็น `issues\0000` แล้ว `.\run.ps1 -Issue 0000 -DryRun` ต้องผ่าน 1 test
   (ทดสอบแม่แบบรายงาน: `python -X utf8 issues\0000\make_report.py` ต้องได้ TestResult_0000.html)
5.1 แอปต้องรันแบบ Admin แต่ terminal ของ Claude ไม่ใช่ → รัน `tools\admin-runner\setup_task.ps1` แบบ Admin ครั้งเดียว
5.2 อ่านหัวข้อ "รูปแบบผลงาน" ใน SKILL.md — รูปแบบ TC/รายงานของทีม ปรับให้ตรงทีมได้
6. ลองใช้จริง: `/test-issue <ID> manual` ก่อน (ไม่ต้องมี locator) แล้วค่อยใช้โหมด default
7. automate ใบแรก: ให้ Claude รันผ่าน แล้ว**รันซ้ำจาก CMD ของคุณเอง** (`powershell -ExecutionPolicy Bypass -File run.ps1 -Issue <ID>`) ต้องผ่านเหมือนกัน

## ปรับเชิงลึก
| ต่างจากสมมติฐาน | ปรับที่ |
|---|---|
| เว็บแอป | เปลี่ยนตัวคุม UI จาก FlaUI เป็น Browser/SeleniumLibrary ใน `issue_common.resource` + locator; ตัดหัวข้อ FlaUI/UIPI/BOM/noclick ใน SKILL.md |
| DB ไม่ใช่ SQL Server | `{DB_QUERY_TOOL}` ใน local.md + driver ใน `libraries/` และ requirements.txt |
| ไม่มี source code | ข้าม Phase 1 ข้อ 1-4 (ให้ user บอก build) และใช้ UI inspector อย่างเดียวในการหา locator |
| ใช้ Jira | `{ISSUE_TRACKER}` = Atlassian MCP / Jira REST / acli · `{ISSUE_KEY_FORMAT}` = `PROJ-123` · ระบุที่อยู่ Test Scenario (Description / custom field / Xray-Zephyr) ใน `{TEST_SCENARIO_SOURCE}` |
| ไม่มี issue tracker ที่ Claude อ่านได้ | `{ISSUE_TRACKER}`: "ให้ user วาง" |
| ทีมไม่ใช้ภาษาไทย | SKILL.md เขียนภาษาไทยแต่สั่งให้ตอบตามภาษาของ user — แปล SKILL.md ได้ถ้าต้องการ |

## Prompt สำหรับส่งให้ Claude ตัวอื่นตั้งค่าให้
คัดลอกข้อความนี้ไปวางใน Claude Code ที่เปิดอยู่ในโฟลเดอร์ repo นี้:

```
อ่าน README.md และ ADAPTING.md ของ repo นี้ แล้วช่วยตั้งค่า skill /test-issue ให้ใช้กับระบบของเรา:
1. ถามข้อมูลที่ต้องใช้กรอก claude-skill/test-issue/local.md ทีละหมวด (ระบบที่ทดสอบ, paths, automation + FlaUI helpers + แผนที่หน้าจอ, issue tracker (Azure DevOps / Jira), DB, ข้อยกเว้นของกฎเหล็ก)
   — สำรวจเครื่องเองก่อนถาม (หา source repo, โปรเจกต์ Robot Framework, เครื่องมือ DB) แล้วเสนอค่าให้ยืนยัน
2. สร้าง local.md และ local.ps1
3. ถ้าระบบต่างจาก "สมมติฐานของโครงนี้" ให้เสนอการปรับตามตาราง "ปรับเชิงลึก" ก่อนแก้
4. รัน install-skill.ps1 และ dry-run issues/_template ให้ผ่าน
ห้ามใส่ข้อมูลองค์กรลงไฟล์ที่ขึ้น git (ดู .gitignore)
```

## พัฒนาต่อเป็นของตัวเอง
- แก้ `SKILL.md` ได้เลย — ใช้ `{ตัวแปร}` แทนค่าเฉพาะองค์กรเสมอ แล้วเพิ่มตัวแปรใหม่ใน `local.example.md`
- ทุกครั้งที่แก้ SKILL.md ขึ้นเลข `version` ใน frontmatter + บรรทัดบนสุด และเพิ่มรายการในหัวข้อ "ประวัติเวอร์ชัน" ท้ายไฟล์
- ตัวช่วย FlaUI ที่ใช้ได้กับทุกแอป → `tools\` (เขียนแบบทั่วไป ห้ามมี path เครื่อง) · ตัวช่วยเฉพาะแอป/issue → `{FLAUI_HELPERS}` หรือ `issues\<ID>\`
- keyword ที่ใช้ได้กับทุกแอป → `issue_common.resource`; keyword เฉพาะแอป → โปรเจกต์ใน `AUTOMATION_HOME`
- ก่อน commit: `git status` ต้องไม่มี `issues/<ID>/`, `local.md`, `local.ps1`
