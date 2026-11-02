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

## Automation
- {AUTOMATION_HOME}: <โปรเจกต์ Robot Framework ที่มี keyword พื้นฐานของแอป (launch/login) — ตั้งใน local.ps1 ด้วย>
- {BASE_KEYWORDS}: <รายการไฟล์ keyword ใน AUTOMATION_HOME + keyword สำคัญ เช่น Launch And Login, Close App>
- ตัวแปร env สำหรับเปลี่ยน build / DB ต่อ issue: <เช่น APP_WORKDIR, DB_NAME>

## Issue tracker
- {ISSUE_TRACKER}: <วิธีอ่าน issue เช่น MCP tool ชื่อ..., CLI, หรือให้ user วาง>

## DB และกติกาเฉพาะโค้ด
- {DB_QUERY_TOOL}: <เช่น sqlcmd / psql + flag ที่ใช้ + วิธีอ่านภาษาที่ไม่ใช่อังกฤษ>
- {DB_VERSION_SOURCE}: <ตาราง/วิธีดูเวอร์ชัน DB>
- {OPTION_LOOKUP}: <วิธีหาว่า feature ถูกเปิดด้วย option ไหน + ตารางที่เก็บ + ต้องรีสตาร์ทแอปไหม>
- {PERSISTED_VALUE_LOOKUP}: <วิธีหาว่าค่าที่แอปคำนวณถูกบันทึกลงคอลัมน์ไหน เช่น grep parameter ใน data layer>
- {BINARY_STRING_ENCODING}: <encoding ของ string ใน binary เช่น UTF-16LE สำหรับ .NET>
- {EVIDENCE_TABLES}: <ตารางที่ใช้เป็นหลักฐานผลเทส + คอลัมน์เวลา/ID ที่ใช้ filter>
