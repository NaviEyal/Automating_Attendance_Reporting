from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

class AttendanceReporter:
    def __init__(self):
        """Initialize the Chrome WebDriver with appropriate options"""
        self.options = Options()
        self.user_data_dir = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data'
        self.options.add_argument(f'user-data-dir={self.user_data_dir}')
        self.options.add_argument('--profile-directory=Default')
        self.options.add_argument("--headless")  # Run in headless mode
        self.options.add_argument("--disable-gpu")  # Extra stability
        self.options.add_argument("--no-sandbox")  # Avoid permission issues


        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=self.options
        )
        self.wait = WebDriverWait(self.driver, 10)
        print("Browser initialized successfully")

    def navigate_to_site(self):
        """Navigate to the reporting site"""
        try:
            self.driver.get("https://one.prat.idf.il/finish")
            time.sleep(2)
            print("Successfully navigated to site")
            return True
        except Exception as e:
            print(f"Error navigating to site: {e}")
            return False

    def access_future_reports(self):
        """Access the future reports section"""
        try:
            # חיפוש וקליק על כפתור 'דיווחים עתידיים'
            future_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'דיווחים עתידיים')]"))
            )
            future_button.click()
            time.sleep(2)
            print("Accessed future reports successfully")
            return True
        except Exception as e:
            print(f"Error accessing future reports: {e}")
            return False

    def find_and_click_date(self, date):
        """Find and click on a specific date number in the calendar using multiple strategies"""
        try:
            date_str = str(date.day)
            print(f"Looking for date: {date_str}")
            
            # Strategy 1: Try finding by table cell with multiple attributes
            xpath_strategies = [
                # Look for the number within a table cell
                f"//td[normalize-space(.)='{date_str}' and not(contains(@class, 'disabled'))]",
                
                # Look for the number within any clickable element
                f"//*[text()='{date_str}' and not(ancestor::*[contains(@class, 'disabled')])]",
                
                # Look specifically within the calendar table
                f"//table[contains(@class, 'calendar')]//td[text()='{date_str}']",
                
                # Try finding by aria-label if available
                f"//*[@aria-label[contains(., '{date_str}')]]"
            ]
            
            for xpath in xpath_strategies:
                try:
                    # Wait for element to be present and visible
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    
                    # Scroll element into view using JavaScript
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    
                    # Try multiple click methods
                    try:
                        # Method 1: Standard click
                        element.click()
                    except:
                        try:
                            # Method 2: JavaScript click
                            self.driver.execute_script("arguments[0].click();", element)
                        except:
                            # Method 3: Action chains
                            from selenium.webdriver.common.action_chains import ActionChains
                            actions = ActionChains(self.driver)
                            actions.move_to_element(element)
                            actions.click()
                            actions.perform()
                    
                    # Verify the click worked by checking for any expected changes
                    time.sleep(1)
                    try:
                        # Look for elements that should appear after successful date selection
                        success = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'נמצא/ת ביחידה')]"))
                        )
                        print(f"Successfully clicked on date {date_str} using strategy: {xpath}")
                        return True
                    except TimeoutException:
                        print(f"Click didn't produce expected results for strategy: {xpath}")
                        continue
                        
                except Exception as e:
                    print(f"Strategy failed: {xpath}")
                    continue
            
            # If all strategies fail, try one last approach with direct JavaScript injection
            try:
                js_click_script = f"""
                var dates = document.evaluate("//td[contains(text(), '{date_str}')]", 
                    document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for(var i = 0; i < dates.snapshotLength; i++) {{
                    var element = dates.snapshotItem(i);
                    if(element.offsetParent !== null) {{
                        element.click();
                        return true;
                    }}
                }}
                return false;
                """
                clicked = self.driver.execute_script(js_click_script)
                if clicked:
                    print(f"Successfully clicked date {date_str} using JavaScript")
                    time.sleep(1)
                    return True
            except Exception as e:
                print(f"JavaScript click strategy failed: {e}")
            
            print(f"All strategies failed to click date {date_str}")
            return False
                
        except Exception as e:
            print(f"Error in find_and_click_date: {e}")
            return False

    def submit_report(self):
        """Submit the attendance report through the sequence of buttons"""
        try:
            button_sequence = [
                ("נמצא/ת ביחידה", "Unit presence"),
                ("נוכח/ת", "Presence"),
                ("שליחת דיווח", "Submit report"),
                ("אישור וסיום", "Confirm")
            ]
            
            for text, step_name in button_sequence:
                button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text}')]"))
                )
                button.click()
                print(f"Completed step: {step_name}")
                time.sleep(1)
            
            return True
        except Exception as e:
            print(f"Error in submit_report at step {step_name}: {e}")
            return False

    def get_date_range(self):
        """Calculate the date range from today until next Thursday"""
        start_date = datetime.now()
        end_date = start_date
        
        # מציאת יום חמישי הקרוב
        while end_date.weekday() != 3:  # 3 = Thursday
            end_date += timedelta(days=1)
        
        print(f"Date range: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}")
        return start_date, end_date

    def is_workday(self, date):
        """Check if given date is a workday (Sunday-Thursday)"""
        return date.weekday() in range(0, 4)  # 0 = Sunday, 3 = Thursday

    def report_attendance(self):
        """Main function to report attendance"""
        try:
            print("\n=== Starting attendance reporting process ===")
            
            if not self.navigate_to_site():
                return
            
            if not self.access_future_reports():
                print("Failed to access future reports")
                return
            
            start_date, end_date = self.get_date_range()
            current_date = start_date
            
            while current_date <= end_date:
                if self.is_workday(current_date):
                    print(f"\nProcessing date: {current_date.strftime('%d/%m/%Y')}")
                    if self.find_and_click_date(current_date):
                        if not self.submit_report():
                            print(f"Failed to submit report for {current_date.strftime('%d/%m/%Y')}")
                    else:
                        print(f"Skipping date {current_date.strftime('%d/%m/%Y')} - could not select")
                
                current_date += timedelta(days=1)
            
            print("\n=== Attendance reporting completed ===")
            
        except Exception as e:
            print(f"\nAn error occurred in main process: {e}")
        finally:
            print("\nClosing browser...")
            self.driver.quit()

if __name__ == "__main__":
    print("\n=== Initializing attendance reporter ===")
    reporter = AttendanceReporter()
    reporter.report_attendance()