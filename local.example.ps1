# ค่าเฉพาะเครื่อง - คัดลอกเป็น local.ps1 (ถูก .gitignore) run.ps1 จะโหลดให้อัตโนมัติ

# โปรเจกต์ Robot Framework ที่มี keyword พื้นฐานของแอป (launch, login, เมนูหลัก)
# ไม่ตั้ง = ใช้ repo นี้เอง (ต้องเขียน keyword พื้นฐานใน resources/keywords/)
# if (-not $env:AUTOMATION_HOME) { $env:AUTOMATION_HOME = 'C:\path\to\app-automation' }

# robot.exe ที่จะใช้ (ไม่ตั้ง = หา .venv ของ AUTOMATION_HOME / repo นี้ / PATH)
# if (-not $env:ROBOT_EXE) { $env:ROBOT_EXE = 'C:\path\to\.venv\Scripts\robot.exe' }

# ค่าเริ่มต้นของแอป/DB (เปลี่ยนต่อ issue ได้ด้วยการตั้ง env ก่อนรัน)
# if (-not $env:APP_WORKDIR) { $env:APP_WORKDIR = 'C:\path\to\build' }
# if (-not $env:DB_NAME) { $env:DB_NAME = 'TestDb' }
