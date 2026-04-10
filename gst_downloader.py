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
        """Initialize the GST Automator with a specific download directory."""
        self.download_dir = download_dir or os.path.join(os.path.expanduser('~'), 'Downloads')
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 20)  # 20 seconds explicit wait

    def _setup_driver(self):
        """Set up Chrome WebDriver with custom download preferences."""
        logging.info(f"Setting up Chrome WebDriver. Downloads will save to: {self.download_dir}")
        chrome_options = Options()
        
        # Keep browser open after script finishes if needed, or allow manual control
        chrome_options.add_experimental_option("detach", True)
        
        # Set default download directory
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True  # Download PDF instead of opening in viewer
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Use WebDriver Manager to automatically get the correct ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        return driver

    def login_manual(self):
        """Navigate to GST login and wait for the user to log in manually."""
        logging.info("Navigating to GST Portal Login Page...")
        self.driver.get("https://services.gst.gov.in/services/login")
        
        logging.info("Waiting for user to manually enter credentials, captcha, and login...")
        input("Press ENTER in this console AFTER you have successfully logged in and the dashboard is visible...")
        logging.info("Manual login confirmed.")

    def navigate_to_returns_dashboard(self):
        """Navigate to the Returns Dashboard after login."""
        logging.info("Navigating to Returns Dashboard...")
        try:
            # Click Services -> Returns -> Returns Dashboard
            # Note: Update XPaths based on actual GST portal DOM
            services_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Services')]")))
            services_menu.click()
            
            returns_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Returns')]")))
            returns_menu.click()
            
            dashboard_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Returns Dashboard')]")))
            dashboard_link.click()
            
            logging.info("Successfully navigated to Returns Dashboard.")
        except Exception as e:
            logging.error(f"Failed to navigate to Returns Dashboard: {e}")

    def select_period(self, financial_year, month):
        """Select Financial Year, Quarter, and Period (Month)."""
        logging.info(f"Selecting Period: FY {financial_year}, Month: {month}")
        try:
            # Select Financial Year
            fy_dropdown = self.wait.until(EC.presence_of_element_located((By.ID, "finYear")))
            Select(fy_dropdown).select_by_visible_text(financial_year)
            
            # Select Period (Month)
            # Assuming 'Quarter' auto-updates or isn't strictly required if period is selected
            period_dropdown = self.wait.until(EC.presence_of_element_located((By.ID, "mon")))
            Select(period_dropdown).select_by_visible_text(month)
            
            # Click Search
            search_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "srchBtn")))
            search_btn.click()
            
            logging.info("Period selected and search executed.")
        except Exception as e:
            logging.error(f"Error selecting period: {e}")

    def download_gstr1(self):
        logging.info("Downloading GSTR-1 PDF...")
        try:
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'GSTR-1')]/following-sibling::div//button[contains(text(), 'DOWNLOAD')]")))
            btn.click()
            # Wait for PDF generation/download link
            pdf_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Generate PDF')]")))
            pdf_link.click()
            logging.info("GSTR-1 PDF Download initiated.")
            self._back_to_dashboard()
        except Exception as e:
            logging.error(f"Could not download GSTR-1: {e}")

    def download_gstr3b(self):
        logging.info("Downloading GSTR-3B PDF...")
        try:
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'GSTR-3B')]/following-sibling::div//button[contains(text(), 'DOWNLOAD')]")))
            btn.click()
            pdf_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'DOWNLOAD GSTR-3B')]")))
            pdf_link.click()
            logging.info("GSTR-3B PDF Download initiated.")
            self._back_to_dashboard()
        except Exception as e:
            logging.error(f"Could not download GSTR-3B: {e}")

    def download_gstr2a(self):
        logging.info("Downloading GSTR-2A Excel...")
        try:
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'GSTR-2A')]/following-sibling::div//button[contains(text(), 'DOWNLOAD')]")))
            btn.click()
            excel_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'GENERATE EXCEL FILE TO DOWNLOAD')]")))
            excel_btn.click()
            # Note: Generating Excel might take 20 mins on the portal. You might need to click the actual download link after generation.
            download_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Click here to download Excel')]")))
            download_link.click()
            logging.info("GSTR-2A Excel Download initiated.")
            self._back_to_dashboard()
        except Exception as e:
            logging.error(f"Could not download GSTR-2A: {e}")

    def download_gstr2b(self):
        logging.info("Downloading GSTR-2B Excel...")
        try:
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'GSTR-2B')]/following-sibling::div//button[contains(text(), 'DOWNLOAD')]")))
            btn.click()
            excel_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download Excel')]")))
            excel_btn.click()
            logging.info("GSTR-2B Excel Download initiated.")
            self._back_to_dashboard()
        except Exception as e:
            logging.error(f"Could not download GSTR-2B: {e}")

    def _back_to_dashboard(self):
        """Helper to navigate back to the dashboard results page."""
        try:
            back_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'BACK')]")))
            back_btn.click()
            # Small implicit wait to ensure dashboard has reloaded properly
            time.sleep(2) 
        except Exception:
            logging.warning("Could not find BACK button, attempting to re-navigate to Returns Dashboard.")
            self.navigate_to_returns_dashboard()

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
            logging.info("Continuing from existing session. Please ensure you are logged in and on the Returns Dashboard.")
            # If starting from dashboard, ask the user to navigate manually first
            input("Navigate to the Returns Dashboard manually, then press ENTER in this console to continue...")

        # Ask user for Period
        fy = input("Enter Financial Year (e.g., 2023-24): ")
        month = input("Enter Month (e.g., October): ")
        
        automator.select_period(fy, month)
        
        # Download files
        automator.download_gstr1()
        automator.download_gstr3b()
        automator.download_gstr2a()
        automator.download_gstr2b()
        
        logging.info("All downloads initiated successfully. Please check your Downloads folder.")
        
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # Keep browser open to finish downloads if needed
        input("Press ENTER to close the browser and exit...")
        automator.close()

if __name__ == "__main__":
    main()