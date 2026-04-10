import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GSTPortalAutomator:
    def __init__(self, download_dir=None):
        self.download_dir = download_dir or os.path.join(os.path.expanduser('~'), 'Downloads')
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def _setup_driver(self):
        logging.info(f"Setting up Chrome WebDriver. Downloads will save to: {self.download_dir}")
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        return driver

    def login_manual(self):
        logging.info("Navigating to GST Portal Login Page...")
        self.driver.get("https://services.gst.gov.in/services/login")
        logging.info("Waiting for user to manually enter credentials, captcha, and login...")
        input("Press ENTER in this console AFTER you have successfully logged in and the dashboard is visible...")
        logging.info("Manual login confirmed.")

    def navigate_to_returns_dashboard(self):
        logging.info("Clicking on 'RETURN DASHBOARD' button...")
        try:
            dashboard_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[normalize-space(text())='RETURN DASHBOARD']")
            ))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dashboard_btn)
            time.sleep(1)
            dashboard_btn.click()
            logging.info("Successfully navigated to Returns Dashboard.")
        except Exception as e:
            logging.error(f"Failed to click Return Dashboard: {e}")

    def select_period(self, financial_year, quarter, month):
        logging.info(f"Selecting FY: {financial_year}, Quarter: {quarter}, Month: {month}")
        try:
            time.sleep(2)
            fy_select = Select(self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(), 'Financial Year')]/following::select[1]")
            )))
            fy_select.select_by_visible_text(financial_year)
            time.sleep(1)
            
            qtr_select = Select(self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(), 'Quarter')]/following::select[1]")
            )))
            qtr_select.select_by_visible_text(quarter)
            time.sleep(1)

            period_select = Select(self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(), 'Period')]/following::select[1]")
            )))
            period_select.select_by_visible_text(month)
            time.sleep(1)
            
            search_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[normalize-space(text())='SEARCH']")
            ))
            search_btn.click()
            logging.info("Period selected and search executed.")
            time.sleep(3)
            
        except Exception as e:
            logging.error(f"Error selecting period: {e}")

    def download_gstr3b(self):
        logging.info("Downloading GSTR-3B PDF...")
        try:
            btn_xpath = "//*[contains(text(), 'GSTR-3B')]/ancestor::div[contains(@class, 'card') or contains(@class, 'box')]//button[normalize-space(text())='DOWNLOAD']"
            fallback_xpath = "(//button[normalize-space(text())='DOWNLOAD'])[2]"
            try:
                download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
            except Exception:
                logging.warning("Primary GSTR-3B Xpath failed, using fallback...")
                download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, fallback_xpath)))

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_btn)
            time.sleep(1)
            download_btn.click()
            logging.info("GSTR-3B PDF Download clicked.")
            time.sleep(3)
            
        except Exception as e:
            logging.error(f"Could not download GSTR-3B: {e}")

    def download_gstr1(self):
        logging.info("Processing GSTR-1...")
        try:
            view_xpath = "//*[contains(text(), 'GSTR1')]/ancestor::div[contains(@class, 'card') or contains(@class, 'box')]//button[normalize-space(text())='VIEW']"
            try:
                view_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, view_xpath)))
            except Exception:
                view_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[normalize-space(text())='VIEW'])[1]")))
                
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_btn)
            time.sleep(1)
            view_btn.click()
            logging.info("Clicked VIEW for GSTR-1. Waiting for page to load...")
            
            time.sleep(3)
            summary_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='VIEW SUMMARY']")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", summary_btn)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", summary_btn)
            logging.info("Clicked VIEW SUMMARY. Waiting for summary to generate...")
            
            time.sleep(5)
            
            download_pdf_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='DOWNLOAD (PDF)']")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", download_pdf_btn)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", download_pdf_btn)
            logging.info("GSTR-1 PDF Download clicked.")
            
            time.sleep(3)
            back_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='BACK']")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", back_btn)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", back_btn)
            logging.info("Navigated BACK to search results.")
            time.sleep(3)
            
        except Exception as e:
            logging.error(f"Could not download GSTR-1: {e}")

    def close(self):
        logging.info("Closing browser...")
        self.driver.quit()

def main():
    print("=== GST Returns Auto Downloader ===")
    start_mode = input("Select Mode: \n1. Start from Login\n2. Continue from existing Dashboard session\nChoice (1/2): ")
    automator = GSTPortalAutomator()

    try:
        if start_mode == '1':
            automator.login_manual()
            automator.navigate_to_returns_dashboard()
        else:
            logging.info("Continuing from existing session...")
            input("Navigate to the Dashboard manually, then press ENTER in this console to continue...")
            automator.navigate_to_returns_dashboard()

        fy = input("Enter Financial Year exactly as shown (e.g., 2025-26): ")
        quarter = input("Enter Quarter exactly as shown (e.g., Quarter 4 (Jan - Mar)): ")
        month = input("Enter Period/Month exactly as shown (e.g., February): ")
        
        automator.select_period(fy, quarter, month)
        
        automator.download_gstr3b()
        automator.download_gstr1()
        
        logging.info("All downloads initiated successfully. Please check your Downloads folder.")
        
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        input("Press ENTER to close the browser and exit...")
        automator.close()

if __name__ == "__main__":
    main()