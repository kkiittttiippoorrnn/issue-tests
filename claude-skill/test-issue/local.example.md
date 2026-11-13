# test-issue — ค่าเฉพาะองค์กร/เครื่อง (ตัวอย่าง)

คัดลอกเป็น `local.md` ในโฟลเดอร์เดียวกันแล้วกรอกค่า — `local.md` ถูก .gitignore ใส่ข้อมูลภายในได้
SKILL.md อ้างค่าเหล่านี้ด้วยชื่อในวงเล็บปีกกา ถ้าข้อไหนไม่มีในองค์กรให้เขียน "ไม่มี" (skill จะข้ามขั้นนั้น)

## ระบบที่ทดสอบ
- {APP_NAME}: <ชื่อแอป / exe ที่ทดสอบ>
- {UI_LANGUAGE}: <ภาษาที่แสดงบนจอ — ถ้าไม่ใช่อังกฤษ ห้ามใช้ locator จากข้อความภาษาอังกฤษ>

## Paths
- {TEST_INFO}: <ไฟล์ข้อมูลทดสอบในเครื่อง: DB server, user/PIN, path build, mock ที่ค้าง>
- {SOURCE_REPO}: <path source code ของระบบที่ทดสอบ (ใช้หา commit fix / อ่านโค้ด)>
- {BUILD_DROP}: <โฟลเดอร์ที่วาง build ใหม่ + โครงสร้างย่อย>
- {UI_SOURCE_GLOB}: <glob ไฟล์ที่นิยามชื่อ control เช่น **/*.Designer.vb, **/*.xaml>
- {UI_INSPECTOR}: <เครื่องมือ export UI tree เช่น Accessibility Insights, FlaUInspect, เครื่องมือภายใน>
- {SCREEN_MAP}: <แผนที่หน้าจอของแอป (ไฟล์ index + ไฟล์ dump ต่อหน้า) และโฟลเดอร์ UI tree ที่ export จาก inspector — Claude อ่านก่อนหา locator และบันทึกหน้าที่ dump ใหม่ลงที่นี่>

## Automation
- {AUTOMATION_HOME}: <โปรเจกต์ Robot Framework ที่มี keyword พื้นฐานของแอป (launch/login) — ตั้งใน local.ps1 ด้วย>
- {FLAUI_HELPERS}: <โฟลเดอร์สคริปต์ตัวช่วย FlaUI ของแอป (หาหน้าต่าง/คลิก/dump/wait) — ค่าเริ่มต้น `tools\` ของ repo นี้>
- {BASE_KEYWORDS}: <รายการไฟล์ keyword ใน AUTOMATION_HOME + keyword สำคัญ เช่น Launch And Login, Close App>
- ตัวแปร env สำหรับเปลี่ยน build / DB ต่อ issue: <เช่น APP_WORKDIR, DB_NAME>

## Issue tracker (Azure DevOps หรือ Jira)
- {ISSUE_TRACKER}: <ชนิด + วิธีอ่าน issue>
  - Azure DevOps: เช่น MCP `azdo` (`show_work_item`, `list_work_item_comments`) หรือ `az boards work-item show`
  - Jira: เช่น Atlassian MCP (อ่าน issue + comment + remote link), Jira REST `GET /rest/api/3/issue/<KEY>?expand=renderedFields`, หรือ `acli jira workitem view <KEY>`
  - อ่านไม่ได้ / ไม่มีสิทธิ์ → ให้ user วางเนื้อหา
- {ISSUE_KEY_FORMAT}: <รูปแบบเลข issue — AzDO: ตัวเลข เช่น `12345` · Jira: `<PROJECT>-<เลข>` เช่น `POS-123`>
- {TEST_SCENARIO_SOURCE}: <Test Scenario อยู่ที่ไหน — AzDO: field เช่น `Custom.TestScenario` · Jira: หัวข้อใน Description, custom field (`customfield_xxxxx`), Acceptance Criteria, หรือ Test issue ที่ link ไว้ (Xray/Zephyr) / sub-task>
- {FIX_LINK_SOURCE}: <หา PR/commit ของ fix — AzDO: relations "Fixed in Commit"/Pull Request · Jira: Development panel (branch/PR/commit) หรือ commit message ที่มี key>
- {RESULT_POST_FORMAT}: <รูปแบบข้อความแปะผล — AzDO: ข้อความธรรมดา/HTML · Jira Cloud: Markdown (MCP/ADF) · Jira Server/DC: wiki markup (`*ตัวหนา*`, `{code}`)>

## DB และกติกาเฉพาะโค้ด
- {DB_QUERY_TOOL}: <เช่น sqlcmd / psql + flag ที่ใช้ + วิธีอ่านภาษาที่ไม่ใช่อังกฤษ>
- {DB_VERSION_SOURCE}: <ตาราง/วิธีดูเวอร์ชัน DB>
- {OPTION_LOOKUP}: <วิธีหาว่า feature ถูกเปิดด้วย option ไหน + ตารางที่เก็บ + ต้องรีสตาร์ทแอปไหม>
- {PERSISTED_VALUE_LOOKUP}: <วิธีหาว่าค่าที่แอปคำนวณถูกบันทึกลงคอลัมน์ไหน เช่น grep parameter ใน data layer>
- {BINARY_STRING_ENCODING}: <encoding ของ string ใน binary เช่น UTF-16LE สำหรับ .NET>
- {EVIDENCE_TABLES}: <ตารางที่ใช้เป็นหลักฐานผลเทส + คอลัมน์เวลา/ID ที่ใช้ filter>
