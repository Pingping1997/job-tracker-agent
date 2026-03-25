import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .base import BaseScraper
from .common import clean_href


class PBLScraper(BaseScraper):
    LIST_URL = "https://www.werkenvoornederland.nl/vacatures?werkgever=01920"
    PBL_TOKEN = "-pbl-"

    def fetch_jobs(self) -> list[dict]:
        organization = self.source["organization"]
        default_city = self.source.get("city", "")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.LIST_URL, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(3000)

            for label in ["Accepteer", "Accept", "Accept all", "Akkoord"]:
                try:
                    page.get_by_text(label, exact=False).click(timeout=1500)
                    page.wait_for_timeout(1000)
                    break
                except Exception:
                    pass

            soup = BeautifulSoup(page.content(), "lxml")
            browser.close()

        jobs = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = clean_href(self.LIST_URL, a["href"])
            href_lower = href.lower()

            if "/vacatures/" not in href_lower:
                continue
            if self.PBL_TOKEN not in href_lower:
                continue
            if href in seen:
                continue
            seen.add(href)

            card = a.find_parent(["article", "li", "div"])
            card_text = " ".join((card.get_text(" ", strip=True) if card else a.get_text(" ", strip=True)).split())

            title = " ".join(a.get_text(" ", strip=True).split())
            if not title or title.lower().startswith("bekijk"):
                if card:
                    for candidate in card.find_all("a", href=True):
                        candidate_href = clean_href(self.LIST_URL, candidate["href"])
                        candidate_text = " ".join(candidate.get_text(" ", strip=True).split())
                        if candidate_href == href and candidate_text and not candidate_text.lower().startswith("bekijk"):
                            title = candidate_text
                            break

            if not title:
                continue

            deadline_match = re.search(r"solliciteer voor\s+([0-9]{1,2}\s+[a-zA-Z]+\s+[0-9]{4})", card_text.lower())
            posted_date = deadline_match.group(1) if deadline_match else ""

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

        return jobs
