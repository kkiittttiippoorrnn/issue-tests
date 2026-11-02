*** Settings ***
Documentation    <ID> - <ชื่อ issue>
...              build: <build ที่มี fix> | DB: <ชื่อ DB>
# keyword พื้นฐานของแอปจาก AUTOMATION_HOME เช่น
# Resource       ${AUTOMATION_HOME}/resources/keywords/login.resource
Resource         ${ISSUE_TESTS}/resources/keywords/issue_common.resource
# DB check (SELECT อย่างเดียว) จาก libraries/ ของ repo นี้หรือของ AUTOMATION_HOME เช่น
# Library        AppDatabase.py    ${DB_SERVER}    ${DB_NAME}    ${DB_UID}    ${DB_PWD}
# Test Setup     <ปิดแอปที่ค้าง>
# Test Teardown  <เก็บ screenshot ถ้า fail + ปิดแอป>
Test Tags        issue-<ID>


*** Test Cases ***
ISSUE-<ID>-TC1 - <คำอธิบาย>
    [Documentation]    Expected: <ผลที่ต้องได้จาก Test Scenario>
    [Tags]    TC1
    # <ขั้นตอนตาม TC ด้วย keyword พื้นฐาน + keyword ใน issue_common.resource>
    No Error Dialog Should Be Shown
    # <ตรวจ DB>
