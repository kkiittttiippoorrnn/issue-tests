---
name: test-issue
description: ทดสอบ issue แบบครบวงจรสำหรับ Tester — อ่าน issue/Test Scenario → หา build ที่มี fix → เตรียม/mock DB (ขออนุญาต) → แปลง TC เป็น Robot Framework test แล้วรันเอง → ตรวจหน้าจอ+DB → สรุป Pass/Fail + rollback. ใช้เมื่อ "/test-issue <ID>", "เทส issue นี้ให้", "ทดสอบตาม test scenario"
args: "<IssueID> [manual]"
---

เมื่อ user เรียก `/test-issue <ID> [manual]` ทำตามขั้นตอนนี้ **ทีละ phase** ตอบเป็นภาษาของ user

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
2. อ่าน issue ตาม {ISSUE_TRACKER} (Description, comment ของ Dev, Test Scenario, attachments)
   - อ่านไม่ได้ / ไม่มีสิทธิ์ → ขอให้ user วาง: รายละเอียดจาก Dev + Test Scenario + DB ที่ใช้
3. user ไม่ได้บอก DB → ถาม (ห้ามเดา) ค่าเริ่มต้นที่เสนอได้คือ DB ใน {TEST_INFO}

## Phase 1 — ตรวจ fix และ build

1. หา commit ของ fix (จาก Test Scenario หรือ `git log --all --grep "<ID>"` ใน {SOURCE_REPO} หลัง `git fetch -q origin`)
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

### 3A. โหมด default — Robot Framework

repo นี้ (`issue-tests`) มีแค่ส่วนของ issue; keyword พื้นฐานของแอป (launch, login, เมนูหลัก) อยู่ที่ {AUTOMATION_HOME} (อ้างใน .robot ด้วย `${AUTOMATION_HOME}`, repo นี้ด้วย `${ISSUE_TESTS}`) — **ห้ามเขียนไฟล์ issue ลง {AUTOMATION_HOME}**
อ่าน README ของทั้งสองที่ + รายการ keyword ใน {BASE_KEYWORDS} ก่อนเขียน

1. **ใช้ keyword ที่มีอยู่ก่อน** ({BASE_KEYWORDS} + `resources\keywords\issue_common.resource`) — เขียนใหม่เฉพาะที่ขาด
2. **Locator** (ลำดับความน่าเชื่อถือ):
   1. id ของ control จาก source ({UI_SOURCE_GLOB})
   2. UI tree ที่ user export จาก {UI_INSPECTOR}
   3. ตำแหน่ง (`path:`) — ใช้เมื่อจำเป็นเท่านั้น + comment ว่าเปราะ
   - ทำตามข้อจำกัด UI ใน `local.md` (เช่นภาษาที่แสดงบนจอ)
   - หา locator ไม่ได้ → หยุด ขอให้ user export UI tree ของหน้าจอนั้น (บอกชัดว่าหน้าจอไหน จังหวะไหน)
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
3. ข้อความสั้นพร้อมแปะใน issue tracker (ไม่ใช้ตาราง)
4. **Gate:** ถามก่อนรัน rollback → รันแล้ว SELECT ยืนยันค่ากลับเป็นค่าเดิม
5. อัปเดต `issues\<ID>\notes.md` ด้วยผลสุดท้าย + สถานะ rollback; test เก็บไว้เป็น regression — รันซ้ำด้วย `.\run.ps1 -Issue <ID>`
6. โหมด manual ก็สร้าง `notes.md` + `rollback.sql` เหมือนกัน (ไม่ต้องมี issue.robot)
7. user สั่ง commit → `git status` ก่อน ต้องไม่มี `issues/<ID>/`, `local.md`, `local.ps1` หลุดเข้า stage
