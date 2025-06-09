import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
from collections import Counter
from html_scraper_utils import scrape_congress_summary  # Import from Selenium scraper module

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GOV_API_KEY")
BASE_URL = "https://api.congress.gov/v3"
DEBUG = True

HEADERS = {
    "Accept": "application/json"
}

# Create log file per run
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, f"explore_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.log")

missing_summary_queue = []  # Stores bills that have no summary or text


def log(msg):
    """Helper function to print and log messages."""
    print(msg)
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def call_api(endpoint, params=None):
    """Make an API GET call with retry logic and error handling."""
    if not params:
        params = {}
    params["api_key"] = API_KEY

    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params)
        time.sleep(0.6)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        raise RuntimeError(f"❌ HTTP error on {endpoint}: {e}")
    except requests.RequestException as e:
        raise RuntimeError(f"❌ Connection error on {endpoint}: {e}")
    except Exception as e:
        raise RuntimeError(f"❌ Unknown error on {endpoint}: {e}")


def get_recent_bills(congress=119, chamber="house", limit=5):
    """Fetch a list of recent bills for a specific chamber and congress."""
    log("📦 Fetching recent bills (summary)...")
    data = call_api("/bill", params={
        "congress": congress,
        "chamber": chamber,
        "pageSize": limit
    })

    if "bills" not in data:
        raise KeyError("Missing 'bills' in summary response")

    return data["bills"]


def fetch_all_pages(base_url):
    """Handles pagination for endpoints like cosponsors or amendments."""
    results = []
    while base_url:
        data = call_api(base_url.replace(BASE_URL, ""))
        page_items = data.get("cosponsors") or data.get("amendments") or []
        results.extend(page_items)
        base_url = data.get("pagination", {}).get("next")
    return results


def explore_bill_data(summary):
    """Explore all details of a given bill summary object from /bill."""
    log("\n==============================")
    log("🔍 Exploring new bill (summary view)...")

    if DEBUG:
        log("Raw keys: " + str(list(summary.keys())))

    bill_type = summary.get("type")
    bill_number = summary.get("number")
    congress = summary.get("congress")

    if bill_type is None or bill_number is None or congress is None:
        raise TypeError("Missing 'type', 'number', or 'congress'")

    bill_id = f"{bill_type.upper()}{bill_number}"
    log(f"📄 Bill ID: {bill_id}")

    full_resp = call_api(f"/bill/{congress}/{bill_type}/{bill_number}")
    full_bill = full_resp.get("bill")
    if not full_bill:
        log(f"⚠️ Skipping {bill_id}: no 'bill' object returned")
        return

    # --- Metadata ---
    try:
        bill_data = {
            "bill_id": [bill_id],
            "title": [full_bill.get("title", "Unknown")],
            "shortTitle": [full_bill.get("shortTitle")],
            "introducedDate": [full_bill.get("introducedDate", "Unknown")],
            "latestAction": [full_bill.get("latestAction", {}).get("text", "Unknown")],
            "subjects": [full_bill.get("subjects", {}).get("legislativeSubjects", [])]
        }
        log("📊 Bill Metadata:")
        log(str(pd.DataFrame(bill_data)))
    except Exception as e:
        log(f"⚠️ Error parsing metadata for {bill_id}: {e}")

    # --- Sponsor ---
    sponsors = full_bill.get("sponsors", [])
    if sponsors:
        sponsor = sponsors[0]
        sponsor_info = {
            "name": sponsor.get("fullName", "Unknown"),
            "party": sponsor.get("party", "Unknown"),
            "state": sponsor.get("state", "Unknown"),
            "chamber": full_bill.get("originChamber", "Unknown")
        }
        log("\n👤 Sponsor Info:")
        log(str(pd.DataFrame([sponsor_info])))
    else:
        log("⚠️ No sponsor data available.")

    # --- Text or Summary ---
    try:
        text_versions_url = full_bill.get("textVersions", {}).get("url")
        if text_versions_url:
            text_versions = call_api(text_versions_url.replace(BASE_URL, ""))
            for item in text_versions.get("textVersions", []):
                if item.get("format") == "text":
                    text = requests.get(item["url"]).text
                    log("\n📄 First 500 characters of Bill Text:")
                    log(text[:500])
                    break
            else:
                raise ValueError("No plain text format found.")
        else:
            raise ValueError("No textVersions URL found.")
    except Exception:
        log(f"⚠️ No plain text available, trying summaries for {bill_id}...")
        try:
            summaries_url = full_bill.get("summaries", {}).get("url")
            if summaries_url:
                summaries_data = call_api(summaries_url.replace(BASE_URL, ""))
                summaries = summaries_data.get("summaries", [])
                if summaries:
                    raw_html = summaries[0].get("text", "No summary text.")
                    plain_summary = BeautifulSoup(raw_html, "html.parser").get_text()
                    log("\n📄 Summary:")
                    log(plain_summary.strip())
                else:
                    raise ValueError("No summaries returned from API")
            else:
                raise ValueError("No summaries URL available")
        except Exception:
            log(f"⚠️ Summary not available via API, using HTML scraper for {bill_id}...")
            html_summary = scrape_congress_summary(bill_id, str(congress))
            if html_summary:
                log("\n📄 Scraped Summary:")
                log(html_summary.strip())
            else:
                log(f"⚠️ Could not scrape summary for {bill_id}")
            missing_summary_queue.append(bill_id)

    # --- Amendments ---
    try:
        amendments_url = full_bill.get("amendments", {}).get("url")
        if amendments_url:
            amendments = fetch_all_pages(amendments_url)
            if amendments:
                log(f"\n📌 Found {len(amendments)} amendment(s):")
                rows = []
                for amend in amendments:
                    amend_type = amend.get("amendmentType", "Unknown")
                    amend_number = amend.get("amendmentNumber", "Unknown")
                    details = {}
                    if amend_type and amend_number:
                        try:
                            details = call_api(f"/amendment/{congress}/{amend_type}/{amend_number}").get("amendment", {})
                        except Exception:
                            pass
                    rows.append({
                        "amendment_id": amend_number,
                        "sponsor": details.get("sponsor", {}).get("fullName", "Unknown"),
                        "title": details.get("title", "Unknown")
                    })
                log(str(pd.DataFrame(rows)))
            else:
                log("\n📎 No amendments found.")
        else:
            log("\n📎 No amendments found.")
    except Exception as e:
        log(f"⚠️ Error processing amendments: {e}")

    # --- Cosponsors ---
    try:
        cosponsors_url = full_bill.get("cosponsors", {}).get("url")
        count = full_bill.get("cosponsors", {}).get("count", 0)
        log(f"👥 Cosponsor count: {count}")
        if cosponsors_url and count:
            cosponsors = fetch_all_pages(cosponsors_url)
            if cosponsors:
                party_counts = Counter(c.get("party", "Unknown") for c in cosponsors)
                log("👥 Cosponsor party breakdown: " + ", ".join([f"{p}: {n}" for p, n in party_counts.items()]))
    except Exception as e:
        log(f"⚠️ Error processing cosponsors: {e}")

    # --- Related Bills ---
    try:
        related_url = full_bill.get("relatedBills", {}).get("url")
        if related_url:
            related_data = call_api(related_url.replace(BASE_URL, ""))
            related = related_data.get("relatedBills", [])
            log(f"🔗 Related bills found: {len(related)}")
            for r in related[:3]:
                r_type = r.get("billType", "?")
                r_num = r.get("number", "?")
                title = "Unknown"
                try:
                    info = call_api(f"/bill/{congress}/{r_type}/{r_num}").get("bill", {})
                    title = info.get("title", "Unknown")
                except Exception:
                    pass
                log(f"  - {r_num} ({r.get('relationshipType', 'Unknown')}): {title}")
        else:
            log("🔗 No related bills.")
    except Exception as e:
        log(f"⚠️ Error fetching related bills: {e}")

# --- Entry point ---
if __name__ == "__main__":
    try:
        recent_bills = get_recent_bills(limit=15)
        for bill_summary in recent_bills:
            explore_bill_data(bill_summary)

        if missing_summary_queue:
            log("\n📭 Bills queued for scraping due to missing summary/text:")
            for b in missing_summary_queue:
                log(f" - {b}")

    except Exception as e:
        log(f"\n🔥 Fatal script error: {e}")
