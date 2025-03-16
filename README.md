# Automating Attendance Reporting

A Python script that automates weekly attendance reporting.

## Setup

1. Install required packages:
   - selenium
   - webdriver-manager (`https://pypi.org/project/webdriver-manager/`)
   - Script defaults to Chrome browser, but can be configured to work with other
     browsers supported by Selenium WebDriver.  

2. Run the script:
   - Use the non-GUI version for scheduling (attendance_report-public.py)
   - Schedule it to run every Sunday morning for best results

## Important Notes

- First run requires manual verification (including entering verification code)
- After first run, browser cookies save your session
- Script saves connection profile in a local folder - secure your computer
- If the target website changes, you'll need to update the script
- Check attendance_report.log file for execution details and troubleshooting
