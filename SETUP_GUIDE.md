# คู่มือติดตั้งและสอน Claude ให้ทำงานเทสแบบทีม

สำหรับ Tester ที่จะเริ่มใช้ Claude Code + skill `/test-issue` (อ่านคู่กับ [ADAPTING.md](ADAPTING.md))

---

## ส่วนที่ 1 — ติดตั้ง (ครั้งเดียว ~30 นาที)

### 1.1 โปรแกรมที่ต้องมี
| โปรแกรม | ใช้ทำอะไร | ตรวจว่ามีแล้ว |
|---|---|---|
| Claude Code | ตัว Claude ที่สั่งงานใน terminal | `claude --version` |
| Windows Terminal | แสดงภาษาไทยได้ถูก (cmd/PowerShell เดิมไทยเพี้ยน) | — |
| Python 3.11+ | รันเทส / ทำรายงาน | `python --version` |
| Git | ดึง repo นี้ / ดู commit ของ fix | `git --version` |
| เครื่องมือ query DB | เช่น `sqlcmd` สำหรับ SQL Server | `sqlcmd -?` |

### 1.2 ติดตั้ง repo + skill
```powershell
git clone <url ของ repo นี้> $HOME\Desktop\issue-tests
cd $HOME\Desktop\issue-tests
.\install-skill.ps1                      # ลิงก์ /test-issue เข้า Claude Code
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 1.3 ให้ Claude ตั้งค่าที่เหลือให้
เปิด Windows Terminal → `cd` เข้าโฟลเดอร์ repo → พิมพ์ `claude` แล้ววาง prompt ในหัวข้อ
"Prompt สำหรับส่งให้ Claude ตัวอื่นตั้งค่าให้" ของ [ADAPTING.md](ADAPTING.md)
Claude จะสำรวจเครื่อง ถามข้อมูลที่ขาด แล้วสร้าง `local.md` / `local.ps1` (ไฟล์ข้อมูลองค์กร ไม่ขึ้น git)

### 1.4 สิ่งที่ต้องทำเองแบบ Admin
- แอปที่ทดสอบต้องรันแบบ Admin → เปิด PowerShell แบบ **Run as administrator** แล้ว `.\tools\admin-runner\setup_task.ps1` (ครั้งเดียว)
  จากนั้น Claude ใน terminal ธรรมดาก็กดแอปได้ (ผ่าน Task Scheduler)
- ต่อ issue tracker ผ่าน MCP ตามที่ทีมใช้ — Azure DevOps (MCP `azdo`) หรือ Jira (Atlassian MCP: พิมพ์ `/mcp` แล้วเชื่อมต่อ) · ไม่มีก็ได้ ให้วางรายละเอียด issue ในแชทแทน

### 1.5 ทดสอบว่าพร้อม
```powershell
Copy-Item issues\_template issues\0000 -Recurse
.\run.ps1 -Issue 0000 -DryRun             # ต้องผ่าน 1 test
python -X utf8 issues\0000\make_report.py # ต้องได้ TestResult_0000.html
Remove-Item issues\0000 -Recurse
```
แล้วลองงานจริงแบบปลอดภัยก่อน: `/test-issue <ID> manual` (Claude ให้ขั้นตอน คุณกดเอง Claude ตรวจ DB)

---

## ส่วนที่ 2 — "เทรน" Claude ให้ทำงานแบบเรา

Claude **ไม่ได้เรียนรู้ถาวรจากการคุย** — สิ่งที่ทำให้มันทำงานแบบเดิมได้ทุกครั้งคือ "ไฟล์ที่มันอ่านตอนเริ่มงาน" มี 4 ชั้น:

| ชั้น | อยู่ที่ | ใช้กับ | แชร์ทีม? |
|---|---|---|---|
| **SKILL.md** | `claude-skill/test-issue/SKILL.md` | ขั้นตอนเทส + รูปแบบ TC/รายงาน ที่ทั้งทีมใช้ | ✅ ผ่าน git |
| **local.md** | `claude-skill/test-issue/local.md` | ข้อเท็จจริงขององค์กร: path build, DB, ตาราง, option | แชร์ในบริษัททางอื่น (ไม่ขึ้น git) |
| **ไฟล์ข้อมูลทดสอบ** | เช่น `claude-test-info.txt` (ตั้งชื่อใน local.md เป็น `{TEST_INFO}`) | DB ที่ใช้, user/PIN ทดสอบ, path build ปัจจุบัน — เปลี่ยนบ่อย | ส่วนตัว |
| **Memory** | `~\.claude\projects\<โฟลเดอร์>\memory\` | ความชอบส่วนตัว + สถานะงานค้างของแต่ละ issue | ส่วนตัว (ต่อเครื่อง) |

> เพิ่มเติม: `~\.claude\CLAUDE.md` = คำสั่งที่ใช้ทุกงาน เช่น "ตอบเป็นภาษาไทยเสมอ"

### 2.1 วิธีสอน (ใช้ได้ผลที่สุด)
1. **แก้ทันทีที่ผิด + บอกเหตุผล** — "ไม่เอา Excel เพราะเอาไปวางต่อไม่ได้" ดีกว่า "ไม่เอา Excel"
   เหตุผลทำให้ Claude ใช้กฎได้ถูกในกรณีใหม่ที่คล้ายกัน
2. **ให้ตัวอย่างจริง** — วางรูปแบบที่ต้องการทั้งก้อน (เช่นรูปแบบ Test Case / หัวรายงาน) แล้วบอก "ต่อไปใช้แบบนี้"
3. **สั่งให้จำ** — "จำไว้ว่า ..." → Claude เขียนลง memory · ถ้าเป็นกฎของทั้งทีม สั่ง "เพิ่มใน SKILL.md ด้วย"
4. **ชมสิ่งที่ถูก** — "แบบนี้ดี ใช้ต่อ" ก็ถูกจดได้ ไม่ใช่จดแต่ข้อผิด
5. **ตรวจ memory เป็นระยะ** — พิมพ์ `/memory` หรือเปิดโฟลเดอร์ memory ลบ/แก้ข้อที่ล้าสมัย (memory ที่ขัดกันทำให้ Claude สับสน)

### 2.2 ตัวอย่างกฎที่ทีมเราสอนไว้แล้ว (อยู่ใน SKILL.md หัวข้อ "รูปแบบผลงาน")
- issue ใหม่ → สรุป Test Case ก่อน แล้วรอคำว่า "เริ่ม"
- Test Case แสดงเป็น "Test Case 1:" มี Step / ผลลัพธ์ที่คาดหวัง / ผลการทดสอบ ครบทุกข้อ
- TC แยก 2 ชุด: ชุดลง issue (ตาม spec) + ชุดเทสเพิ่ม (จุดที่อาจกระทบ)
- รายงาน HTML แยกบล็อก TEST PASS / TEST FAIL + ข้อสังเกตแยกไฟล์ TestNote
- รูปหลักฐาน crop + กรอบ + ป้ายบอกผล
- ลำดับ 9 ขั้นต่อ issue เป็นกฎเหล็ก · FlaUI เป็นเครื่องมือหลัก · หา locator จากแผนที่หน้าจอก่อน dump สด
- automate ต้องผ่านจาก terminal ของ user เองด้วย

### 2.3 ส่งต่อสิ่งที่สอนให้เพื่อน
- กฎที่ทุกคนควรใช้ → ย้ายจาก memory เข้า SKILL.md แล้ว commit/push (เขียนแบบทั่วไป ห้ามมีชื่อ DB/รหัสผ่าน/ชื่อเครื่อง)
- ข้อเท็จจริงของระบบ (ตาราง, option, gotcha ของหน้าจอ) → `local.md` แล้วส่งให้เพื่อนในบริษัททางช่องทางภายใน
- สถานะงานค้างของแต่ละ issue อยู่ใน `issues\<ID>\notes.md` (ไม่ขึ้น git) — ส่งต่อเป็นไฟล์ถ้าต้องให้คนอื่นทำต่อ

---

## ส่วนที่ 3 — ใช้งานประจำวัน
ลำดับเป็น **กฎเหล็ก** ของ skill (ห้ามข้าม/สลับ/รวบขั้น) — Claude บอกเสมอว่าอยู่ขั้นไหน (เช่น "ขั้น 5/9")
```
/clear                       เริ่ม issue ใหม่ทุกครั้ง (1 issue ต่อ 1 session — ประหยัด token และไม่ปนข้อมูล)
/test-issue 1234             Claude อ่าน issue → ตรวจ build → เสนอ mock (Jira: /test-issue POS-123)
อนุญาต mock                  Claude mock + เขียน rollback.sql → ส่งสรุป Test Case แล้วรอ
เริ่ม                         Claude แจ้งก่อนคุมหน้าจอ แล้วเทสทีละ TC
(Claude ส่งผล)               ได้ TestResult_1234.html + TestNote_1234.html + ข้อความแปะ issue
(automate)                   Claude ทำ issue.robot + setup.sql รันผ่าน → คุณรันจาก CMD (Admin) อีก 1 รอบ
rollback ได้                  คืนข้อมูลทดสอบ แล้ว SELECT ยืนยัน
                             คุณแปะผล/แนบรายงานใน issue tracker เอง
```
- ไม่ต้องทำ automate ใบไหน → สั่ง "ไม่ต้องทำ robot" (Claude จดเหตุผลลง notes.md)
- ระหว่าง Claude คุมแอป ไม่ต้องแตะเครื่อง — คลิกแบบไม่ขยับเมาส์ แต่เทสที่นับเวลาว่าง (เช่น Auto Logout) ใช้ input จริง ห้ามแตะเด็ดขาด
- Claude ขออนุญาตทุกครั้งก่อน: แก้ข้อมูลใน DB, รัน UI ครั้งแรก, rollback, git commit/push

รันเทสซ้ำเอง (CMD แบบ Run as administrator):
```bat
cd /d <โฟลเดอร์ repo>
powershell -ExecutionPolicy Bypass -File run.ps1 -Issue 1234
cd issues\1234\evidence & dir /b /ad /o-n 2026*
start "" <โฟลเดอร์บนสุด>\report.html
```

## ปัญหาที่พบบ่อย
| อาการ | แก้ |
|---|---|
| ภาษาไทยในหน้าจอ Claude เพี้ยน | ใช้ Windows Terminal |
| Claude กดแอปไม่ติด | แอปรันแบบ Admin → ตั้ง `tools\admin-runner` (ข้อ 1.4) |
| ตัวรันแบบ Admin ค้าง | แอปมี dialog ค้าง — ดูหน้าจอ แล้ว `schtasks /end /tn ClaudeAdminRunner` |
| Claude ทำไม่ตรงแบบที่เคยสอน | ดู memory / SKILL.md ว่ามีกฎนั้นไหม หรือมีกฎขัดกัน |
| MCP (issue tracker) ต่อไม่ได้ | พิมพ์ `/mcp` → reconnect (Jira: เชื่อม Atlassian) · หรือวางรายละเอียด issue ในแชทแทน |
| automate ผ่านตอน Claude รัน แต่ fail ตอนรันเองจาก CMD | ภาษาไทยเพี้ยนใน output (`α╕...`) → `Run Process` ต้องมี `output_encoding=UTF-8` · หน้าต่างอื่นบังแอป → ใช้ `tools\noclick.py` (ยกหน้าต่างแอปให้เอง) · บอก Claude พร้อมโฟลเดอร์ evidence ของรอบนั้น |
| เทสช้า / เมาส์ลากไปมา | ตัวช่วยยังใช้ `Desktop.FindAllChildren` หรือ sleep ตายตัว / คลิกเมาส์จริง → ให้ Claude ปรับตามหัวข้อ "ประสิทธิภาพและเวลา" ใน SKILL.md |
