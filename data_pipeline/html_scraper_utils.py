import os
import time
import logging
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

# Set to True for detailed logging and screenshot capture
DEBUG = False  # 🔧 Toggle this to True to enable debugging features (e.g., screenshots)

# Set up logging for debugging
log_path = "logs/scraper_test.log"
os.makedirs("logs/screenshots", exist_ok=True)
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("✅ HTML Scraper Utilities loaded")

def init_edge_browser(headless: bool = False):
    """
    Initialize a Microsoft Edge browser instance for Selenium automation.
    Args:
        headless (bool): Whether to launch in headless mode (no visible UI).
    Returns:
        webdriver.Edge: Configured Selenium Edge driver instance.
    """
    options = EdgeOptions()
    options.use_chromium = True
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    return webdriver.Edge(service=EdgeService(), options=options)

def scrape_congress_summary(bill_id: str, congress: str = "119") -> Optional[Dict[str, str]]:
    """
    Scrape the visible CRS summary text and latest action from congress.gov for the given bill.
    Args:
        bill_id (str): The bill ID (e.g. HR3800, HRES52)
        congress (str): The Congress session, default is "119"
    Returns:
        dict or None: A dictionary with 'summary' and 'latest_action' keys if found, else None.
    """
    number_only = bill_id.lower().replace("hr", "").replace("hres", "")
    url = f"https://www.congress.gov/bill/{congress}th-congress/house-bill/{number_only}"
    logging.info(f"🌐 Scraping summary from: {url}")
    browser = None
    screenshot_name = os.path.join("logs", "screenshots", f"screenshot_{bill_id.upper()}.png")

    latest_action = None

    try:
        browser = init_edge_browser(headless=False)
        browser.get(url)
        time.sleep(5)  # Let JS render and Cloudflare check finish

        if "Just a moment" in browser.title or "Verify you are human" in browser.page_source:
            logging.warning("⚠️ Blocked by bot protection at page: %s", url)
            return None

        # ✅ Try to fetch latest action using more robust XPath
        try:
            latest_cell = browser.find_element(By.XPATH, '//*[@id="content"]/div[1]/div[3]/div[1]/table/tbody/tr[3]/td')
            latest_action = latest_cell.text.strip()
            logging.info(f"📌 Latest action: {latest_action}")
        except NoSuchElementException:
            logging.warning(f"⚠️ Could not extract latest action for {bill_id}")

        # ✅ Main summary section if available
        try:
            summary_section = browser.find_element(By.ID, "bill-summary")
            html = summary_section.get_attribute("innerHTML")
            soup = BeautifulSoup(html, "html.parser")
            summary_text = soup.get_text(" ", strip=True)
            if summary_text:
                logging.info(f"✅ Extracted main summary for {bill_id}")
                return {"summary": summary_text, "latest_action": latest_action}
        except NoSuchElementException:
            logging.warning(f"🔍 No #bill-summary section found for {bill_id}, trying backup path")

        # ✅ Fallback summary section
        try:
            fallback_p = browser.find_element(By.CSS_SELECTOR, "#main p.no-highlighting")
            fallback_text = fallback_p.text.strip()
            if fallback_text:
                logging.info(f"✅ Extracted fallback summary for {bill_id}")
                return {"summary": fallback_text, "latest_action": latest_action}
        except NoSuchElementException:
            logging.warning(f"❌ No fallback <p> found for {bill_id}")

        return None

    except Exception as e:
        logging.error(f"🔥 Selenium scraping failed for {bill_id}: {e}")
        return None

    finally:
        if browser:
            try:
                browser.save_screenshot(screenshot_name)
                logging.info(f"📸 Saved screenshot for {bill_id} -> {screenshot_name}")
            except:
                logging.warning(f"⚠️ Could not save screenshot for {bill_id}")
            browser.quit()

            # Cleanup screenshot
            try:
                if os.path.exists(screenshot_name):
                    os.remove(screenshot_name)
                    logging.info(f"🧹 Deleted screenshot: {screenshot_name}")
            except Exception as e:
                logging.warning(f"⚠️ Failed to delete screenshot {screenshot_name}: {e}")

if __name__ == "__main__":
    test_bill = "HR3829"
    result = scrape_congress_summary(test_bill)
    if result:
        print(f"\n📄 SUMMARY for {test_bill}:\n{result['summary']}\n")
        print(f"📌 LATEST ACTION: {result['latest_action']}\n")
    else:
        print(f"\n⚠️ No summary found for {test_bill}\n")
