# libraries

Python library สำหรับตรวจ DB (SELECT อย่างเดียว) — ไม่เจอข้อมูลที่คาด → `raise AssertionError` ให้ Robot fail

ตัวอย่างโครง (SQL Server ผ่าน pyodbc — เปลี่ยน driver ตาม DB ขององค์กร):

```python
import pyodbc


class AppDatabase:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self, server, database, uid, pwd, driver="ODBC Driver 17 for SQL Server"):
        self._conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={uid};PWD={pwd};"

    def _fetch(self, sql, *params):
        conn = pyodbc.connect(self._conn_str)
        try:
            return conn.cursor().execute(sql, params).fetchall()
        finally:
            conn.close()
```

ถ้า AUTOMATION_HOME มี library DB อยู่แล้ว (run.ps1 ใส่ `AUTOMATION_HOME/libraries` ใน pythonpath ให้) ต่อยอดด้วยการ import class นั้นแทน
