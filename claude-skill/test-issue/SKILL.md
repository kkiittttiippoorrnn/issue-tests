---
name: test-issue
description: ทดสอบ issue แบบครบวงจรสำหรับ Tester (Azure DevOps หรือ Jira) — อ่าน issue/Test Scenario → หา build ที่มี fix → เตรียม/mock DB (ขออนุญาต) → คุม UI ด้วย FlaUI + Robot Framework แล้วรันเอง → ตรวจหน้าจอ+DB → สรุป Pass/Fail + rollback. ใช้เมื่อ "/test-issue <ID>", "เทส issue นี้ให้", "ทดสอบตาม test scenario"
args: "<IssueID> [manual]"
version: "2.0"
---

> **test-issue เวอร์ชัน 2.0** (2026-11-13) — ประวัติการแก้ดูหัวข้อ "ประวัติเวอร์ชัน" ท้ายไฟล์

เมื่อ user เรียก `/test-issue <ID> [manual]` ทำตามขั้นตอนนี้ **ทีละ phase** ตอบเป็นภาษาของ user

### ⛔ กฎเหล็ก: ลำดับต่อ 1 issue (◆ = ต้องหยุดรอ user)
**บังคับทุก issue — ห้ามข้ามขั้น ห้ามสลับลำดับ ห้ามรวบหลายขั้นในครั้งเดียว**
- ขั้น ◆ ต้องได้คำตอบจาก user ในข้อความใหม่ก่อนไปขั้นถัดไป — การอนุญาตขั้นหนึ่งไม่นับเป็นการอนุญาตขั้นอื่น (อนุญาต mock ≠ อนุญาตเริ่มเทส ≠ อนุญาต rollback)
- ข้ามขั้นได้เฉพาะเมื่อ user **สั่งชัดเจน** ให้ข้ามขั้นนั้น (เช่น "ไม่ต้องทำ automate") → จดคำสั่ง + เหตุผลลง `notes.md` ทุกครั้ง
- ข้อยกเว้นเฉพาะ user/องค์กร (เช่นช่วงเวลาที่เริ่มเทสได้ทันที) ต้องเขียนไว้ใน `local.md` เท่านั้น — ห้ามอนุมานเอง
- ขั้นไหนทำไม่ได้ (ไม่มีสิทธิ์ / build ไม่มี fix / แอปเปิดไม่ได้) → หยุดที่ขั้นนั้น แจ้ง user พร้อมสาเหตุ ห้ามข้ามไปขั้นถัดไป
- ทุกครั้งที่รายงานความคืบหน้า บอกว่าอยู่ขั้นไหน (เช่น "ขั้น 5/9")

1. เริ่ม session ใหม่ (`/clear`) → `/test-issue <ID>`
2. อ่าน issue → ตรวจ fix/build จาก binary จริง + เช็คว่าโฟลเดอร์ที่ใช้รันคือ build นั้น → เช็ค DB/SP
3. หาเงื่อนไขบั๊ก → query DB → ◆ ขออนุญาต mock (SQL + ค่าเดิม + `rollback.sql`)
4. ◆ ส่งสรุป Test Case 2 ชุด แล้วรอคำว่า "เริ่ม"
5. ◆ แจ้งก่อนคุมหน้าจอ → เทสทีละ TC (หน้าจอ + DB + หลักฐาน) · fail ต้องแยก test พัง vs ระบบพัง
6. สรุปผล TC + ข้อความแปะ issue tracker → รายงาน `TestResult_<ID>.html` + `TestNote_<ID>.html`
7. Automate ก่อน rollback: `issue.robot` + `setup.sql` → DryRun → ◆ รันจริงผ่าน → ◆ user รันจาก terminal ของ user เองผ่าน 1 รอบ
8. ◆ ขออนุญาต rollback → รัน + SELECT ยืนยัน
9. บันทึก `notes.md` (ผล / rollback / automate / วิธีรัน) → ◆ user แจ้งผลใน issue tracker เอง

> **ก่อนเริ่ม: อ่าน `local.md` ในโฟลเดอร์เดียวกับไฟล์นี้** — ค่าในวงเล็บปีกกา ({APP_NAME}, {SOURCE_REPO}, ...) และกติกาเฉพาะระบบอยู่ในนั้น
> ไม่มี `local.md` → หยุด บอก user ให้ทำตาม `ADAPTING.md` ที่ root ของ repo (คัดลอก `local.example.md` แล้วกรอก) — ห้ามเดา path/ชื่อระบบ
>
> **โหมด**
> - `/test-issue <ID>` (default) — ผมรัน UI เองผ่าน Robot Framework (`run.ps1`)
> - `/test-issue <ID> manual` — ไม่รัน UI: ให้ขั้นตอนทีละ TC ให้ user กดเอง แล้วผมเช็ค DB หลังแต่ละ TC
>
> **หลักที่ใช้ตลอด**
> - user เป็น Tester ต้องการผลเทส/bug report ไม่ใช่ให้แก้โค้ดของระบบที่เทส
> - **Gate ที่ต้องหยุดถาม:** (1) ก่อนแก้ข้อมูล/option ใน DB ทุกครั้ง (2) ก่อนรัน UI ครั้งแรกของ session (3) ก่อน rollback (4) ก่อน git commit/push
> - ห้ามตัดสิน Pass จากสิ่งที่ไม่ได้ตรวจจริง — แยก "ตรวจแล้ว" กับ "อ้างอิงผล Dev / user ยืนยัน" ให้ชัด
> - Report ผลจริงตามที่เห็น ถ้า fail ให้แนบ output/หลักฐาน
> - **ข้อมูลองค์กรห้ามขึ้น git:** `issues/<ID>/`, `local.md`, `local.ps1` ถูก .gitignore — ไฟล์อื่นใน repo (SKILL.md, README, resources, libraries) ต้องเขียนแบบทั่วไป ไม่มี path/ชื่อระบบ/ข้อมูล DB ขององค์กร

---

## Phase 0 — โหลด context

1. อ่าน `local.md` และ {TEST_INFO}
2. อ่าน issue ตาม {ISSUE_TRACKER} (Description, comment ของ Dev, Test Scenario ตาม {TEST_SCENARIO_SOURCE}, attachments)
   - `<ID>` = เลข issue ตาม {ISSUE_KEY_FORMAT} ใช้ตามจริงทุกที่ (โฟลเดอร์ `issues\<ID>\`, ชื่อ test `ISSUE-<ID>-TC<n>`, tag `issue-<ID>`) เช่น AzDO `12345` / Jira `POS-123`
   - **Jira:** Test Scenario อาจกระจายหลายที่ — Description, custom field, Acceptance Criteria, sub-task, หรือ Test issue ที่ link ไว้ (Xray/Zephyr) → อ่านให้ครบแล้วสรุปว่าใช้จากที่ไหน · ดู comment + Development panel (branch/PR) · Jira Cloud ผ่าน MCP ยังไม่ authenticate → บอก user ให้เชื่อมต่อ (`/mcp`) หรือวางเนื้อหามา
   - **Azure DevOps:** ดู field Test Scenario + comment + relations (PR / Fixed in Commit)
   - อ่านไม่ได้ / ไม่มีสิทธิ์ → ขอให้ user วาง: รายละเอียดจาก Dev + Test Scenario + DB ที่ใช้
3. user ไม่ได้บอก DB → ถาม (ห้ามเดา) ค่าเริ่มต้นที่เสนอได้คือ DB ใน {TEST_INFO}

## Phase 1 — ตรวจ fix และ build

1. หา commit ของ fix ตาม {FIX_LINK_SOURCE} (PR/commit ที่ link กับ issue) หรือ `git log --all --grep "<ID>"` ใน {SOURCE_REPO} หลัง `git fetch -q origin`
   - Jira: key (`POS-123`) อยู่ใน commit/branch ตาม smart commit — grep ตรงได้ · AzDO: เลขล้วนชนกับเลขอื่นง่าย → grep `#<ID>` หรือ `AB#<ID>` แล้วยืนยันกับ PR ที่ link ไว้
2. `git branch -r --contains <sha>` → fix อยู่ branch ไหน
3. `git show <sha>` → แก้ module ไหน + string/logic ที่เปลี่ยน
4. หา build ใน {BUILD_DROP} (ใหม่สุดก่อน) แล้ว **พิสูจน์จาก binary จริง** ว่ามี fix:
   - fix เปลี่ยน string (SQL/ข้อความ) → `python -c` เปิดไฟล์แบบ rb แล้วหา string ใหม่ (encoding ตาม {BINARY_STRING_ENCODING}) เทียบกับ string เก่า
   - logic ที่ไม่มี string ให้เทียบ → ใช้ timestamp ไฟล์เทียบกับเวลา commit + บอก user ว่ายืนยันไม่ได้ 100%
5. เทียบเวอร์ชัน DB ({DB_VERSION_SOURCE}) กับเวอร์ชัน build
6. สรุป: build ไหนมี fix (ใช้เทส) / build ไหนยังเป็นโค้ดเก่า (ใช้ reproduce ได้)

## Phase 2 — เตรียมข้อมูลทดสอบ

1. อ่านโค้ดจุดที่แก้ → หา **เงื่อนไขที่ทำให้ bug เกิด** (ข้อมูล / option gate — วิธีหา option ใน {OPTION_LOOKUP})
2. Query DB (read-only ด้วย {DB_QUERY_TOOL}) ว่าข้อมูลปัจจุบันเข้าเงื่อนไขหรือยัง
3. ต้อง mock → **Gate: เสนอ SQL + ค่าเดิม แล้วรอ user อนุญาต**
   - เขียน rollback script (ค่าเดิมแบบตายตัว) ที่ `issues\<ID>\rollback.sql` (สร้างโฟลเดอร์จาก `_template` ถ้ายังไม่มี) แล้วบอก path
   - รันใน transaction แล้ว SELECT ยืนยันผลทุกครั้ง
   - เลือกค่า mock ให้ **แยกแยะได้** (ค่าจากแต่ละแหล่งต่างกัน) เพื่อพิสูจน์ว่าระบบอ่านถูกแหล่ง
4. จบ phase: สรุปข้อมูลที่ใช้เป็นชื่อที่ user เห็นบนจอ

## Phase 3 — ทดสอบ

### 3A. โหมด default — FlaUI (UIA3) + Robot Framework

**เครื่องมือหลักในการคุม UI = FlaUI (UIA3) ผ่าน `tools\flaui_kit.py`** (v2) — library ไฟล์เดียวใช้ได้ทุกแอป:
- **Robot:** `Library  ${ISSUE_TESTS}/tools/flaui_kit.py  <process>  <exe>  AS  <ชื่อ>` → keyword ทำงานใน process เดียว **ห้ามใช้ `Run Process` เรียกสคริปต์ทีละขั้น** (เสีย 2–6 วิ/ครั้ง) · หลายแอปในชุดเดียวใช้หลาย instance (`AS POS` / `AS HQ`)
- **CLI (เทสสด/สำรวจ):** `python -X utf8 tools\flaui_kit.py --proc <process> [--exe <path>] <คำสั่ง> ... ; <คำสั่ง> ...` — คำสั่งชุดเดียวกับ keyword (`@<หน้าต่าง>`, `k=v`)
- Locator: `id:<AutomationId>` · `name:<Name>` · `type:<ControlType>` รวมด้วย `|` · `#2` = ตัวที่ 2 · หน้าต่าง = AutomationId/Name (รวม dialog ลูก) หรือ `#0` = บนสุด (popup ไม่มีชื่อ)
- keyword หลัก: Start App / Kill App · Wait / Wait Gone / Wait Window / Wait Window Gone · Click (ไม่ขยับเมาส์) / Invoke · Type Text / Set Value / Press Keys (ดึงหน้าต่างขึ้นหน้าสุดก่อนพิมพ์) · **Select Item** (combo/dropdown/checked combo ด้วย element จริง) · Message Box · Close Window / Close Any Window · No Error Dialog · Grid Rows · Rect · Screenshot · Dump · At Point (แปลงพิกัดเดิมเป็น locator)
- ตัวช่วยเฉพาะแอปที่ยังไม่ได้ย้าย ({FLAUI_HELPERS}) ใช้ได้ระหว่างย้าย — งานใหม่เขียนด้วย `flaui_kit` เท่านั้น
- ห้ามเปลี่ยนไปใช้วิธีอื่น (RPA.Windows, pywinauto, MCP คุมหน้าจอ, ให้ user กด/แคปจอ) เพียงเพราะ FlaUI ติดปัญหา — แก้ที่ตัวช่วย FlaUI ก่อน · โหมด manual ใช้เมื่อ user สั่งเท่านั้น
- หา locator จาก **แผนที่หน้าจอ {SCREEN_MAP} / UI tree ที่ export ไว้แล้ว** ก่อนเสมอ — dump สดด้วย FlaUI เฉพาะจุดที่ยังไม่รู้ (ดูลำดับ Locator ด้านล่าง)
- ทำตามหัวข้อ **"ประสิทธิภาพและเวลา"** ด้านล่างทุกครั้งที่เขียน/แก้ตัวช่วยหรือ `.robot`

repo นี้ (`issue-tests`) มีแค่ส่วนของ issue; keyword พื้นฐานของแอป (launch, login, เมนูหลัก) อยู่ที่ {AUTOMATION_HOME} (อ้างใน .robot ด้วย `${AUTOMATION_HOME}`, repo นี้ด้วย `${ISSUE_TESTS}`) — **ห้ามเขียนไฟล์ issue ลง {AUTOMATION_HOME}**
อ่าน README ของทั้งสองที่ + รายการ keyword ใน {BASE_KEYWORDS} ก่อนเขียน

1. **ใช้ keyword ที่มีอยู่ก่อน** ({BASE_KEYWORDS} + `resources\keywords\issue_common.resource`) — เขียนใหม่เฉพาะที่ขาด
2. **Locator** — ใช้ของที่มีอยู่ก่อน dump สด (เร็วกว่า + ได้ค่าเดิมทุกรอบ):
   1. **แผนที่หน้าจอ {SCREEN_MAP}** + **UI tree ที่ export ไว้แล้ว** จาก {UI_INSPECTOR} — อ่านไฟล์ก่อนเปิดหน้าจอเสมอ
   2. AutomationId ของ control จาก source ({UI_SOURCE_GLOB}) — เมื่อแผนที่ยังไม่มีหน้านั้น
   3. **dump สดด้วย FlaUI เฉพาะจุดที่ยังไม่รู้** หรือ locator จากแผนที่หาไม่เจอ (build ใหม่เปลี่ยนหน้าจอ)
      - dump เฉพาะหน้าต่าง/element นั้น จำกัดความลึก — ห้าม dump ทั้งแอปหรือ dump หน้าที่แผนที่มีอยู่แล้ว
      - **บันทึกผลลง {SCREEN_MAP} ทันที** (ทางเข้า, id, ControlType+Name, ข้อควรระวัง) — เก็บเฉพาะของที่ใช้ซ้ำได้ ไม่เก็บข้อมูลเฉพาะ issue
   4. ให้ user export จาก {UI_INSPECTOR} — เมื่อ dump แล้วยังไม่ได้ (เช่น popup ที่หายเร็ว) บอกชัดว่าหน้าจอไหน จังหวะไหน
   5. พิกัดภายในหน้าต่าง — ทางสุดท้าย + comment ว่าเปราะ (ขึ้นกับความละเอียดจอ) · ใช้ `At Point` แปลงพิกัดเดิมเป็น locator ก่อนเสมอ
   - element ที่ไม่มี id ใช้ ControlType + Name (ตามภาษาบนจอ) · ลิงก์ (LinkLabel) ให้คลิกที่ Hyperlink ลูก ไม่ใช่กลางกรอบ Text
   - การอ่าน**ค่า**บนจอระหว่างเทส (ข้อความใน dialog, ค่าในช่อง, รายการใน grid) ยังอ่านสดตามปกติ — ไม่นับเป็นการ dump
   - ทำตามข้อจำกัด UI ใน `local.md` (เช่นภาษาที่แสดงบนจอ)
3. ไฟล์ที่สร้าง — คัดลอก `issues\_template\` เป็น `issues\<ID>\` แล้วแก้:
   - `issue.robot` — 1 test ต่อ TC, ชื่อ `ISSUE-<ID>-TC<n> - <คำอธิบาย>`, tag `issue-<ID>` + `TC<n>`
   - `notes.md` — build / DB / mock (ค่าเดิม → ใหม่) / ผล / ข้อสังเกต (อัปเดตตลอดทาง)
   - `rollback.sql` — ค่าเดิมแบบตายตัว
   - keyword ที่ใช้ซ้ำได้ → `resources\keywords\issue_common.resource`, locator → `resources\locators\app_screens.resource` (**เขียนแบบทั่วไป** เพราะขึ้น git — ค่าเฉพาะแอปให้ส่งผ่านตัวแปร)
   - DB check → `libraries\*.py` (SELECT อย่างเดียว, ไม่เจอ → `raise AssertionError`)
   - ทุก test ต้องตรวจ **ทั้งจอ** (`No Error Dialog Should Be Shown`) **และ DB**
4. ค่าเฉพาะ issue (build, DB) ส่งผ่าน environment variable ตามที่ {AUTOMATION_HOME} รองรับ — ไม่แก้ไฟล์ config ของ {AUTOMATION_HOME}:
   ```powershell
   Set-Location <issue-tests>
   $env:<APP_PATH_VAR>='<build dir>'; $env:<DB_NAME_VAR>='<DB>'; .\run.ps1 -Issue <ID> -DryRun
   ```
   - ไฟล์ .ps1 ที่มีอักษรนอก ASCII ต้องบันทึกเป็น UTF-8 **มี BOM** (Windows PowerShell 5.1)
5. รัน `-DryRun` ก่อนเสมอ (เช็ค syntax/keyword โดยไม่เปิดแอป)
6. **Gate (ครั้งแรกของ session):** บอก user ว่าจะคุมเมาส์/คีย์บอร์ด ห้ามแตะเครื่องระหว่างรัน + ให้ปิด {APP_NAME} ที่เปิดค้าง → รอตอบ
7. รันจริง: `.\run.ps1 -Issue <ID> -RerunFailed` (timeout ยาว)
   - แอปรันแบบ Admin แล้ว click ไม่ติด (UIPI) → บอก user ให้รัน terminal แบบ Admin
8. อ่านผล `issues\<ID>\evidence\<timestamp>\output.xml` (หรือ `merged\`) — fail ให้แยกว่า **test พัง (locator/timing)** หรือ **ระบบพังจริง** ก่อนสรุป
   - test พัง → แก้ test แล้วรันใหม่ (ไม่นับเป็น bug)
   - ระบบพังจริง → เก็บ screenshot + ข้อความ error + ข้อมูล DB เป็นหลักฐาน

### 3B. โหมด manual

- ให้ขั้นตอนทีละ TC เป็นชื่อที่ user เห็นบนจอ + ผลที่ต้องได้
- รอ user บอก "เสร็จ" → query DB ด้วย filter เวลา/ID ล่าสุด (ไม่เดา ID) แล้วสรุปผลต่อ TC — ตารางหลักฐานดู {EVIDENCE_TABLES}
- ไม่เจอ activity ใน DB → บอกตรงๆ (อาจยังไม่บันทึก / แอปต่อคนละ DB)

### ทั้งสองโหมด
- ก่อนสรุปว่าค่าไหน "ตรวจจาก DB ไม่ได้" ให้หาก่อนว่าค่านั้นถูกบันทึกลง DB หรือไม่ ({PERSISTED_VALUE_LOOKUP})
- ข้อสังเกตที่ไม่เกี่ยวกับ fix → แยกหัวข้อ "ข้อสังเกต (ไม่เกี่ยวกับใบนี้)" ไม่ปนกับผล TC

## Phase 4 — สรุปผล

1. ผลต่อ TC: ✅ Pass / ❌ Fail / ⚠️ ตรวจได้บางส่วน + หลักฐาน (ID, ค่าใน DB, path report/screenshot)
2. Build + DB ที่ใช้, ข้อมูล mock ที่ยังค้าง
3. ข้อความสั้นพร้อมแปะใน issue tracker (ไม่ใช้ตาราง) ตาม {RESULT_POST_FORMAT}
   - Jira Cloud: Markdown (`**ตัวหนา**`, `- รายการ`) · Jira Server/DC: wiki markup (`*ตัวหนา*`, `* รายการ`, `{code}...{code}`) · AzDO: ข้อความธรรมดา/HTML
   - ข้อความอ้างไฟล์แนบ `TestResult_<ID>.html` / `TestNote_<ID>.html` — Claude ไม่โพสต์/ไม่เปลี่ยนสถานะ issue เอง (user ทำ ตามกฎเหล็กขั้น 9)
4. **ทำ Automate เก็บไว้ทุก issue (ก่อน rollback — ข้อมูล mock ยังอยู่)** — แม้เทสรอบแรกจะทำแบบ manual หรือสคริปต์ชั่วคราว
   - `issues\<ID>\issue.robot` 1 test ต่อ TC (ชื่อ/tag ตาม Phase 3A) ใช้ขั้นตอนที่ **ผ่านจริงแล้ว** ในรอบเทส (locator, การรอ, หน้าต่างที่ระบุ) ไม่ต้องสำรวจใหม่
   - ทุก test มี assertion อัตโนมัติ: หน้าจอ (หน้าต่าง/ข้อความที่ต้องเห็น + ไม่มี error dialog) และ DB (SELECT ก่อน → หลัง) — ห้ามมี test ที่แค่กดโดยไม่ตรวจ
   - ขั้นที่ไวต่อเวลา/input จริง (เช่น Auto Logout) เรียก `tools\ui_step.py` ผ่าน `Run Process` ได้
   - `issues\<ID>\setup.sql` = ตั้งข้อมูล/option ให้อยู่ในสถานะพร้อมเทส (คู่กับ `rollback.sql`) — regression ต้องรันซ้ำได้หลัง rollback
   - TC ที่เทสไม่ได้ (N/A) → `Skip` พร้อมเหตุผล · TC ที่ต้องปิดเปิดแอป/เปลี่ยน option → tag แยก (เช่น `restart`) ให้เลือกรัน
   - DryRun → **Gate (รัน UI)** → รันจริง 1 รอบให้ผ่านทั้งหมด → จด `.\run.ps1 -Issue <ID>` + เวลาที่ใช้ + เงื่อนไขก่อนรัน ลง `notes.md`
   - **ต้องผ่านในสภาพแวดล้อมเดียวกับที่ user จะรัน** — ผ่านจาก runner/Task ของ Claude อย่างเดียวยังไม่นับว่าเสร็จ: ให้ user รันคำสั่งที่ส่งให้จาก terminal ของ user เอง (เช่น CMD แบบ Admin) แล้วผ่าน 1 รอบ
     - สาเหตุที่ผ่านใน runner แต่ fail ที่ user: encoding ของ console (`Run Process` ต้องใส่ `output_encoding=UTF-8` เมื่อเทียบข้อความนอก ASCII) · หน้าต่าง terminal ของ user บังแอป (การคลิกต้องยกหน้าต่างแอปขึ้นก่อน) · venv/robot คนละตัวกับที่ runner ใช้
     - คำสั่งที่ให้ user ต้องเป็นของ shell ที่ user ใช้จริง (CMD: `powershell -ExecutionPolicy Bypass -File run.ps1 -Issue <ID>`) พร้อมคำสั่งเปิด `report.html` ของรอบล่าสุด
   - user สั่งข้ามได้ ("ไม่ต้องทำ automate") — ถ้าข้ามให้บันทึกเหตุผลใน `notes.md`
5. **Gate:** ถามก่อนรัน rollback → รันแล้ว SELECT ยืนยันค่ากลับเป็นค่าเดิม
6. อัปเดต `issues\<ID>\notes.md` ด้วยผลสุดท้าย + สถานะ rollback + สถานะ automate; test เก็บไว้เป็น regression — รันซ้ำด้วย `.\run.ps1 -Issue <ID>`
7. โหมด manual ก็สร้าง `notes.md` + `rollback.sql` และทำ automate ตามข้อ 4 เหมือนกัน
8. user สั่ง commit → `git status` ก่อน ต้องไม่มี `issues/<ID>/`, `local.md`, `local.ps1` หลุดเข้า stage

---

## รูปแบบผลงาน (ใช้ทุก issue — ถ้า user สั่งต่างจากนี้ให้ทำตาม user)

### ลำดับการทำงาน
- issue ใหม่: วิเคราะห์ + เตรียม/mock เสร็จ → **ส่งสรุป Test Case แล้วหยุดรอคำว่า "เริ่ม"** (การอนุญาต mock ≠ อนุญาตเริ่มเทส)
- แยก TC 2 ชุด: **ชุดลง issue** = ครอบคลุม spec / Test Scenario เท่านั้น · **ชุดเทสเพิ่ม** = จุดที่อาจกระทบจากโค้ดที่แก้ (edge case, ฟังก์ชันรอบๆ, option ปิด/เปิด) — เทสจริงทั้งคู่; ถ้า user เลือกชุดไหนใช้ชุดนั้น
- ต้องสลับลำดับทำ TC → เรียงเลข TC ใหม่ตามลำดับที่ทำจริง (1, 2, 3 ...)
- 1 issue ต่อ 1 session — จบแล้วจดสถานะลง `notes.md` แนะนำ `/clear`; ดูโค้ดเฉพาะ diff, crop รูปก่อนเปิดดู, สรุปสั้น

### รูปแบบ Test Case (ทุกครั้งที่แสดง รวมถึงแสดงซ้ำ/รายงานผล)
ข้อความใน code block (copy ไปวางได้) ไม่ใช้ตาราง ไม่ใช้ "TC1" และ **ทุกข้อมีครบ 3 ส่วนเสมอ** แม้ user บอก "เอาแค่ Step":
```
รายชื่อ Test Case
Test Case 1: <ชื่อ>
Test Case 2: <ชื่อ>

----------------------------------------------
Test Case 1: <ชื่อ>
Step
  เข้าสู่ระบบ ... → เมนู → หน้า
  ทำ ...
ผลลัพธ์ที่คาดหวัง
  ...
ผลการทดสอบ
  (ว่างไว้ตอนสรุป TC / ใส่ผลตอนรายงาน)
```

### รายงาน HTML (`issues\<ID>\make_report.py` จากแม่แบบใน `_template`)
- **ระดับงานที่ต้องได้: ดู `docs\example\TestResult_EXAMPLE.html` + `TestNote_EXAMPLE.html`** (และ `docs\example\make_report.py` = ตัวอย่างการกรอกแม่แบบ) — ทำรูป/รายงานให้ได้อย่างน้อยระดับนี้
- `TestResult_<ID>.html` — บล็อก **TEST PASS** (TC/ส่วนที่ผ่าน) แล้วบล็อก **TEST FAIL** (เฉพาะถ้ามีส่วนที่ไม่ผ่าน) แต่ละบล็อกมีหัว `Test Status / Test on Date / Test Version / Test By` ของตัวเอง ไม่มีส่วน "สรุปผล" ด้านบน
  - TC ที่ผลปนกัน → อยู่ทั้ง 2 บล็อก พร้อมป้าย "ผลที่ผ่าน (PASS)" / "ผลที่ไม่ผ่าน (FAIL)" และรูปเฉพาะส่วนนั้น
  - ใส่ชุดเทสเพิ่มรวมในไฟล์เดียวกันได้ถ้า user ต้องการ
- `TestNote_<ID>.html` — ข้อสังเกตแยกไฟล์: ปัญหา / Step / ผลจริง / ผลกระทบ / ให้ SA ยืนยัน + รูป/ตารางก่อน→หลัง · เขียนด้วยชื่อกลาง (สินค้า A, สาขา X) ใส่ค่าจริงแค่บรรทัด "ข้อมูลในรูป"
- รูปหลักฐาน: `libraries\HlMark.py` — crop เฉพาะจุด + กรอบหนา + ป้ายบอก "ตรวจอะไร/ได้อะไร" (เขียว=ผ่าน แดง=ผิด น้ำเงิน=ข้อมูลประกอบ); ผล DB เป็นรูปตาราง (`table()`); ทุก TC มีอย่างน้อย 1 รูปที่มีป้าย; ภาพหลายจอให้ย่อก่อนใส่ป้าย
- ขนาดไฟล์: ฝังรูปเป็น JPEG กว้าง ~760px quality ~55 (รายงาน 12 TC ≈ 0.5 MB)
- สรุปผล DB ในแชท: บอกแค่ก่อน → หลัง (ไม่ต้องบอกว่าค่าไหน mock); ข้อความแปะ issue tracker สั้น ไม่ใช้ตาราง

### Mock / DB ทดสอบ
- DB ทดสอบไม่ต้องสร้างตาราง backup (zz_*) — จดค่าเดิมแบบตายตัวใน `rollback.sql` แทน (ยังต้องขออนุญาตก่อนแก้)
- การกดบันทึกในหน้าตั้งค่าของแอปอาจแก้ DB เกินค่าที่ติ๊ก (ลบ/สร้างแถวใหม่) → snapshot ตาราง option ก่อน-หลังด้วย diff แล้วเพิ่มลง rollback

## ประสิทธิภาพและเวลา (บังคับ — ใช้กับการเทสสดและ automate)

เป้าหมาย: แต่ละขั้นของ UI ใช้เวลาเป็น "ส่วนของวินาที" ไม่ใช่หลายวินาที · test เดียวเกิน ~60 วิ ต้องหาสาเหตุก่อนส่งงาน

**หาหน้าต่าง / element**
- locator มาจากแผนที่หน้าจอ / export ที่มีอยู่ก่อน — dump สดเฉพาะจุดที่ไม่รู้แล้วบันทึกลงแผนที่ (ลำดับ Locator ใน 3A)
- หาหน้าต่างของแอปด้วย `EnumWindows` + `FromHandle` (≈0.05 วิ) — **ห้าม** `Desktop.FindAllChildren()` (2–3 วิ/ครั้ง)
- ระบุหน้าต่างก่อนค้น element (id ซ้ำข้ามหน้าต่างได้) · cache หน้าต่าง/แท็บที่ใช้ซ้ำในคำสั่งเดียวกัน

**รอแบบมีเงื่อนไข ไม่ sleep ตายตัว**
- ใช้ `wait <element>` / `waitgone <element>` / `until(fn, timeout)` — ไปต่อทันทีที่เงื่อนไขจริง
- sleep ตายตัวได้เฉพาะช่วงสั้น (≤1 วิ) เช่น dropdown/animation · ยกเว้นฟีเจอร์ที่นับเวลาว่าง (ดู Gotcha)
- งานยาวที่มีสัญญาณจบ (sync, export, รายงาน) → รอหน้าต่าง/ไฟล์/แถว DB ที่บอกว่าจบ แทนการ sleep ประมาณเวลา

**คลิก/พิมพ์โดยไม่ลากเมาส์**
- คลิกด้วย `tools\noclick.py` (PostMessage ไปที่หน้าต่างลูก ณ จุดนั้น) — เคอร์เซอร์ไม่ขยับ ไม่บล็อกแม้ปุ่มเปิด modal · ส่ง `pids` ของแอปเสมอ (กันคลิกโดนหน้าต่างอื่น; ถ้าถูกบังจะยกหน้าต่างแอปขึ้นก่อน)
- ปุ่มที่ไม่เปิด modal ใช้ UIA Invoke ได้ · พิมพ์ด้วย `Focus()` + Keyboard หรือ Value pattern (ไม่ต้องคลิกช่องก่อน)
- คีย์บอร์ดไปที่หน้าต่าง foreground เท่านั้น → ดึงหน้าต่างขึ้นหน้าสุดก่อนพิมพ์ (`noclick.activate`) · พิมพ์ทีละ token เว้น ~0.3 วิ (ช่องสแกน/ค้นหาทำงานตอน TextChanged) · id ซ้ำหลายชนิด (เช่น `1001` ใน Save As มีทั้ง ComboBox และ Edit) ระบุ `type:` ด้วย
- DevExpress LookUp: ตั้งข้อความที่ตรงรายการผ่าน Value pattern = เลือกแล้ว (popup ที่เด้งก็คลิกได้) · DevExpress CheckedCombo: เปิด popup → ติ๊ก CheckBox → OK · ปุ่ม Open ใน DevExpress Edit ไม่รับคลิก PostMessage
- control ที่ไม่รับ PostMessage (เช่นปุ่มใน layout บางแบบ) → ปิด dialog ด้วย `WM_CLOSE` / ใช้ pattern ที่เหมาะ — ไม่กลับไปใช้เมาส์จริงถ้าเลี่ยงได้
- ต้องใช้เมาส์จริง → `noclick` ตั้ง FlaUI `Mouse.MovePixelsPerMillisecond` สูงให้กระโดดทันที (ไม่ลาก)

**ลดจำนวนครั้งที่เรียก process**
- automate: เรียก `flaui_kit` เป็น Robot library ใน process เดียว (วัดจริง: 4 test จาก 116 วิ → 21 วิ)
- 1 process (และ 1 ครั้งที่เรียก admin runner) รันหลายขั้นต่อกัน (คั่นด้วย `;` หรือ sequence) — การเริ่ม Python + โหลด FlaUI กิน 2–6 วิ/ครั้ง
- แยกการเรียกเฉพาะจุดที่ต้องดูผลก่อนตัดสินใจขั้นต่อไป

**ไม่ทำซ้ำสิ่งที่ไม่จำเป็น**
- เช็คสถานะก่อนนำทาง — อยู่หน้าเป้าหมายแล้ว (และตั้งค่าไว้แล้ว) ให้ข้าม · ใช้แอปที่เปิดอยู่ต่อ ไม่ปิดเปิด/login ซ้ำ เว้นแต่ต้องโหลด option ใหม่
- เรียง TC ให้ใช้สถานะต่อกันได้ (login เดียว, หน้าเดียว) โดยไม่ทำให้ TC พึ่งผลกันจนแยกรันไม่ได้
- ภาพหลักฐานถ่ายครั้งเดียวให้ครอบหลาย TC ได้ถ้าอยู่หน้าจอเดียวกัน

**DB check หนัก**
- query/SP ที่ช้าบนข้อมูลทั้งหมด → ค่าเริ่มต้นจำกัดช่วง (เช่นย้อนหลัง N วัน) + ตัวแปรเลือกรันแบบเต็ม · งานอิสระกัน (เช่น SP ก่อน/หลังแก้) รันคู่ขนาน · ช่วงที่เลือกต้องมีข้อมูล (ไม่มี → fail ไม่ใช่ผ่านลอยๆ)

**วัดผล**
- หลังรันทุกครั้งอ่านเวลาต่อ test จาก `output.xml` แล้วจดลง `notes.md` (เวลารวม + test ที่ช้าสุด) — เทียบกับรอบก่อนเมื่อแก้เพื่อความเร็ว

## Gotcha ของ UI automation (Windows desktop)
- แอปรันแบบ Admin → ตัวกดต้องเป็น Admin ด้วย (UIPI) — ใช้ `tools\admin-runner` (Task Scheduler) ถ้า terminal ไม่ใช่ Admin
- **ฟีเจอร์ที่นับเวลาว่าง (Auto Logout, screen saver)** ใช้ `GetLastInputInfo` — UIA `Invoke` และ FlaUI `Mouse.MoveBy` **ไม่นับเป็น input** (แอปเห็นเครื่องว่างตลอด → logout ทันทีหลัง login) ต้องใช้ `Click()` / `Keyboard.Press` จริง; ระหว่างรอใช้ sleep ไม่ใช่ loop ที่เรียก UIA (ช้า เวลาเพี้ยน); รวมทุกขั้นของ TC ไว้ในคำสั่งเดียว (คั่นคำสั่งแล้วแอปอาจ logout ไปก่อน)
- ปุ่มที่เปิด modal (MessageBox/dialog) → UIA `Invoke` ค้าง ใช้ `tools\noclick.py` (PostMessage) แทน
- หา element ด้วย id ให้ **ระบุหน้าต่าง** (`btnSave@<WindowId>`) — id เดียวกันมีหลายหน้าต่าง ตัวแรกที่เจออาจซ่อนอยู่/คนละหน้า (คลิกพลาดโดยไม่ error)
- ปุ่มเป็นสีเทา (`IsEnabled=False`) → กดไม่มีผล ตรวจก่อนสรุปว่าแอปไม่ตอบสนอง
- script fail → ถ่ายภาพหน้าจอดูสถานะจริงก่อนแก้/รันซ้ำ (มักเป็น dialog ค้าง ไม่ใช่ระบบผิด)
- ผล "แปลก" ให้แยก test พัง vs ระบบพังเสมอ — เช่นวัด idle ของระบบจริง (`tools\ui_step.py` แสดง `sys_idle_ms`) ก่อนสรุปว่าแอปผิด


---

## ประวัติเวอร์ชัน
- **1.0** (2026-11-13) — เวอร์ชันแรกที่ใช้งานจริง: 5 phase (context → fix/build → เตรียมข้อมูล → ทดสอบ default/manual → สรุป+automate+rollback) · gate 4 จุด · TC 2 ชุด · รายงาน TestResult/TestNote · automate ก่อน rollback · ลำดับต่อ 1 issue เป็น**กฎเหล็ก** (ห้ามข้าม/สลับ/รวบขั้น, ขั้น ◆ ต้องรอ user, ข้ามได้เมื่อ user สั่งชัด + จดเหตุผล) · ต้องผ่านในสภาพแวดล้อมเดียวกับที่ user รัน (encoding UTF-8, หน้าต่างบัง, คำสั่งตาม shell ของ user)
- **1.1** (2026-11-13) — รองรับ Jira นอกจาก Azure DevOps: เลข issue แบบ `PROJ-123` ใช้ได้ทุกที่ (โฟลเดอร์/ชื่อ test/tag) · แหล่ง Test Scenario ของ Jira (Description / custom field / Acceptance Criteria / Xray-Zephyr / sub-task) · หา fix จาก Development panel + smart commit · รูปแบบข้อความแปะผล (Markdown / wiki markup / AzDO) · ค่าใหม่ใน local.md: {ISSUE_KEY_FORMAT} {TEST_SCENARIO_SOURCE} {FIX_LINK_SOURCE} {RESULT_POST_FORMAT}
- **1.2** (2026-11-13) — FlaUI (UIA3) เป็นเครื่องมือหลักคุม UI (ห้ามเปลี่ยนวิธีเพราะติดปัญหา, dump UI tree เองก่อนขอ user) · หัวข้อใหม่ "ประสิทธิภาพและเวลา": EnumWindows แทน FindAllChildren, wait/waitgone แทน sleep, คลิกแบบไม่ขยับเมาส์ `tools\noclick.py`, รวมหลายขั้นต่อ process, ข้ามการนำทางซ้ำ, DB check หนักจำกัดช่วง+คู่ขนาน, จดเวลาต่อ test · ค่าใหม่ {FLAUI_HELPERS}
- **1.3** (2026-11-13) — ลำดับหา locator ใหม่: แผนที่หน้าจอ {SCREEN_MAP} + UI tree ที่ export ไว้ → AutomationId จาก source → dump สดด้วย FlaUI เฉพาะจุดที่ไม่รู้/หาไม่เจอ (dump เฉพาะหน้าต่างนั้น แล้วบันทึกลงแผนที่ทันที) → ขอ user export → พิกัด · ค่าใหม่ {SCREEN_MAP}
- **2.0** (2026-11-13) — `tools\flaui_kit.py`: FlaUI library ไฟล์เดียว ใช้เป็น Robot library ใน process เดียว (เลิก Run Process ทีละขั้น — #12327 จาก 116 วิ เหลือ 21 วิ) + CLI คำสั่งชุดเดียวกัน · locator `id:/name:/type:` + `#n` · Select Item สำหรับ combo / DevExpress LookUp / CheckedCombo แทนพิกัด · At Point แปลงพิกัดเป็น locator · Close Any Window แทน sleep รอ sync · noclick.activate ดึงหน้าต่างขึ้นหน้าสุดก่อนพิมพ์ (แก้กรณีหน้าต่างอื่นบัง)
