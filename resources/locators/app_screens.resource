*** Settings ***
Documentation    Locator ของหน้าจอที่ keyword ใน repo นี้ใช้ (RPA.Windows syntax)
...              ลำดับที่ใช้: id ของ control จาก source > UI tree ที่ export > path ตามตำแหน่ง (เปราะ ต้อง comment)
...              ถ้าแอปไม่ได้แสดงภาษาอังกฤษ ห้ามใช้ name: ที่เป็นข้อความภาษาอังกฤษ


*** Variables ***
# dialog error ของแอป (ค่าเริ่มต้น: Windows MessageBox)
${APP.ERROR_DIALOG}    class:#32770
