import re

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from filters import load_keywords, match_keywords
from .base import BaseScraper
from .common import clean_href


class CareersGovScraper(BaseScraper):
    BASE_DETAIL_PATH = "/jobs/hrp/"
    MAX_PAGES_TO_SCAN = 105
    MAX_EMPTY_MATCH_PAGES = 15

    def fetch_jobs(self) -> list[dict]:
        url = self.source["url"]
        organization = self.source["organization"]
        default_city = self.source.get("city", "")
        keywords = load_keywords()

        jobs = []
        seen = set()
        empty_match_pages = 0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(2000)

            for _ in range(self.MAX_PAGES_TO_SCAN):
                soup = BeautifulSoup(page.content(), "lxml")
                page_match_count = 0

                for a in soup.find_all("a", href=True):
                    href = clean_href(url, a["href"])
                    if self.BASE_DETAIL_PATH not in href:
                        continue

                    if href in seen:
                        continue

                    card_text = " ".join(a.get_text(" ", strip=True).split())
                    if not card_text:
                        continue

                    # Job cards include an "apply-button" control; skip it and keep the title button text.
                    title = ""
                    for btn in a.find_all("button"):
                        btn_text = " ".join(btn.get_text(" ", strip=True).split())
                        if not btn_text or btn_text.lower() == "apply-button":
                            continue
                        title = btn_text.replace(" New badge", "").strip()
                        break

                    if not title:
                        title = card_text.split(" New badge ", 1)[0].strip()
                    if not title:
                        continue

                    text_to_match = f"{title} {card_text}"
                    if not match_keywords(text_to_match, keywords):
                        continue

                    seen.add(href)

                    closing_match = re.search(r"Closing on ([0-9]{1,2} [A-Za-z]{3} [0-9]{4})", card_text)
                    posted_date = closing_match.group(1) if closing_match else ""

                    jobs.append(
                        {
                            "organization": organization,
                            "title": title,
                            "location": default_city,
                            "posted_date": posted_date,
                            "url": href,
                            "summary": card_text,
                        }
                    )
                    page_match_count += 1

                if page_match_count == 0:
                    empty_match_pages += 1
                else:
                    empty_match_pages = 0

                if empty_match_pages >= self.MAX_EMPTY_MATCH_PAGES:
                    break

                next_button = page.get_by_role("button", name="Next page")
                if next_button.count() == 0 or next_button.first.is_disabled():
                    break

                next_button.first.click()
                page.wait_for_timeout(1500)

            browser.close()

        return jobs
