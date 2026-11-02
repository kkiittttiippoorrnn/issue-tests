*** Settings ***
Documentation    keyword ที่ใช้ซ้ำข้าม issue (เขียนแบบทั่วไป - ค่าเฉพาะแอปส่งผ่านตัวแปร/locator)
...              keyword พื้นฐานของแอป (launch, login) อยู่ที่ ${AUTOMATION_HOME}
Library          RPA.Windows
Resource         ${ISSUE_TESTS}/resources/locators/app_screens.resource


*** Keywords ***
No Error Dialog Should Be Shown
    [Documentation]    ต้องไม่มี dialog error ค้างบนจอ (ค่าเริ่มต้น: Windows MessageBox class #32770)
    ...    เปลี่ยน locator ได้ที่ ${APP.ERROR_DIALOG} ใน app_screens.resource
    ${found}=    Run Keyword And Return Status    Get Element    ${APP.ERROR_DIALOG}    timeout=0.5
    IF    ${found}
        ${text}=    Get Attribute    ${APP.ERROR_DIALOG}    Name
        Fail    เจอ dialog บนหน้าจอ: ${text}
    END
