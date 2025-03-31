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
import random # added for some unpredictability


# global timeout values
SMALL_TIMEOUT = 2.5  # inconsistent decimal value
BIG_TIMEOUT = 11     # slightly odd number

# Some globals - not ideal but realistic for quick scripts
success_count = 0
fail_count = 0
browser = None  # will be set later


class myReportBot:
    '''simple bot to report attendance'''
    def __init__(self):
        # Set up the browser with my prefs
        my_options = Options()
        chrome_folder = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data'
        my_options.add_argument(f'user-data-dir={chrome_folder}')
        my_options.add_argument('--profile-directory=Default')
        
        # some personal todo comments left in the code
        # TODO: add headless option for background running
        # FIXME: sometimes this breaks if Chrome is already open
        
        global browser
        browser = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=my_options
        )
        self.driver = browser  # redundant assignment, common in real code
        self._wait = WebDriverWait(self.driver, BIG_TIMEOUT)  # underscore prefix inconsistently used
        print("Got the browser running!")

    def go_to_website(self):
        # Random sleep timings that vary slightly - more human-like
        try:
            self.driver.get("https://one.prat.idf.il/finish")
            time.sleep(2 + random.random())  # sleep between 2-3 seconds
            print("Got to the website ok")
            return True
        except Exception as e:
            print(f"Crap, website error: {e}")
            return False

    def click_future_stuff(self):
        # Inconsistent naming compared to other methods
        try:
            # Hebrew comments mixed in
            # מחפש את הכפתור של דיווחים עתידיים
            future_btn = self._wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'דיווחים עתידיים')]"))
            )
            future_btn.click()
            
            # Some hard-coded sleep values rather than waits - common in real code
            time.sleep(1.8)
            print("Found the future reports button!")
            return True
        except Exception as e:
            print(f"Couldn't find future button: {e}")
            return False

    def find_date_and_click(self, target_date):
        # Method with unnecessarily complex implementation - common in real code
        date_num = str(target_date.day)
        print(f"Looking for day number {date_num}")
        
        # Over-engineering with multiple approaches
        xpath_attempts = [
            f"//td[normalize-space(.)='{date_num}' and not(contains(@class, 'disabled'))]",
            f"//*[text()='{date_num}' and not(ancestor::*[contains(@class, 'disabled')])]",
            f"//table[contains(@class, 'calendar')]//td[text()='{date_num}']",
            f"//*[@aria-label[contains(., '{date_num}')]]"
        ]
        
        # Different sleep times for different attempts - typical of human debugging
        attempt_sleeps = [1.1, 0.75, 1.5, 0.9]
        
        for i, xpath in enumerate(xpath_attempts):
            try:
                el = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                
                # JS scroll with inconsistent argument style
                self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
                
                # Try clicking in different ways with unclear necessity
                try:
                    # Attempt 1
                    el.click()
                except:
                    try:
                        # JS click with inline comment
                        self.driver.execute_script("arguments[0].click();", el) # js click usually works better
                    except:
                        # Action chain as last resort
                        actions = ActionChains(self.driver)
                        actions.move_to_element(el).click().perform()
                
                # Sleep time from array - typical of quickly written scripts  
                time.sleep(attempt_sleeps[i])
                
                # Check if it worked
                try:
                    check = self._wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'נמצא/ת ביחידה')]"))
                    )
                    print(f"FOUND IT! clicked day {date_num}")
                    global success_count
                    success_count += 1
                    return True
                except TimeoutException:
                    print(f"click didn't work right for try #{i+1}")
                    continue
                    
            except Exception as e:
                print(f"nope, try #{i+1} failed")
                continue
        
        # Last ditch effort with some poorly formatted JS
        try:
            js_try = f"""
            var allDates = document.evaluate("//td[contains(text(), '{date_num}')]", 
                document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            for(var i = 0; i < allDates.snapshotLength; i++) {{
                var el = allDates.snapshotItem(i);
                if(el.offsetParent !== null) {{
                    el.click();
                    return true;
                }}
            }}
            return false;
            """
            worked = self.driver.execute_script(js_try)
            if worked:
                print(f"js trick worked for day {date_num}!!")
                time.sleep(0.7)  # inconsistent sleep time
                success_count += 1
                return True
        except Exception as e:
            print(f"js trick failed too: {e}")
        
        print(f"can't click on {date_num}, skipping it")
        global fail_count
        fail_count += 1
        return False

    def do_the_reporting(self):
        # Function with less formal name
        try:
            # Hebrew and English mixed in comments and variables
            buttons = [
                ("נמצא/ת ביחידה", "at_unit"),
                ("נוכח/ת", "present"),
                ("שליחת דיווח", "send_it"),
                ("אישור וסיום", "confirm")
            ]
            
            for heb_text, btn_name in buttons:
                b = self._wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{heb_text}')]"))
                )
                b.click()
                print(f"Clicked: {btn_name}")
                
                # Variable sleep times
                wait_time = 0.8 + (random.random() * 0.4)  # 0.8 - 1.2 seconds
                time.sleep(wait_time)
            
            return True
        except Exception as e:
            print(f"Error while clicking buttons: {e}")
            return False

    def figure_out_dates(self):
        # Different naming style in this method
        today = datetime.now()
        end = today
        
        # Find next Thursday with comment in Hebrew
        # מוצאים את יום חמישי הקרוב
        while end.weekday() != 3:  # 3 = Thursday
            end += timedelta(days=1)
        
        print(f"Will do from {today.strftime('%d/%m/%Y')} to {end.strftime('%d/%m/%Y')}")
        return today, end

    def is_work_day(self, d):
        # Shortened variable name - typical in quickly written scripts
        return d.weekday() in [0, 1, 2, 3]  # Sun-Thu, explicit list instead of range

    def run_all(self):
        # Main function with error handling
        global success_count, fail_count
        success_count = 0
        fail_count = 0
        
        try:
            print("\n### STARTING THE BOT ###")
            
            # Some inconsistent error handling - sometimes returning, sometimes continuing
            if not self.go_to_website():
                print("Can't even get to the site, giving up")
                return
            
            if not self.click_future_stuff():
                print("Future reports button problem, will try to continue anyway")
                # Continuing despite failure - common in real code
            
            # Get dates to work with
            start, end = self.figure_out_dates()
            curr = start
            
            # Loop through dates
            while curr <= end:
                if self.is_work_day(curr):
                    print(f"\nTrying for {curr.strftime('%d/%m/%Y')}")
                    if self.find_date_and_click(curr):
                        if not self.do_the_reporting():
                            print(f"Failed reporting for {curr.strftime('%d/%m/%Y')}")
                    else:
                        print(f"Skipping {curr.strftime('%d/%m/%Y')} - couldn't select it")
                else:
                    print(f"Skipping {curr.strftime('%d/%m/%Y')} - not a work day")
                
                curr += timedelta(days=1)
            
            print(f"\n### ALL DONE! Success: {success_count}, Failed: {fail_count} ###")
            
        except Exception as e:
            print(f"\nSomething broke in the main process: {e}")
        finally:
            print("\nShutting down...")
            self.driver.quit()


# Script entry point with slightly inconsistent style
if __name__ == "__main__":
    print("\n### ATTENDANCE BOT STARTING ###")
    # Inconsistent variable naming convention
    myBot = myReportBot()
    myBot.run_all()
