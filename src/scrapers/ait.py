from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .base import BaseScraper
from .common import clean_href


class AITScraper(BaseScraper):
    JOB_PATH = "/Job/"

    def fetch_jobs(self) -> list[dict]:
        url = self.source["url"]
        organization = self.source["organization"]
        default_city = self.source.get("city", "")

        jobs = []
        seen = set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(1500)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "lxml")

        for a in soup.select("a[href*='/Job/']"):
            href = clean_href(url, a.get("href", ""))
            if self.JOB_PATH not in href:
                continue

            if href in seen:
                continue
            seen.add(href)

            title = " ".join(a.get_text(" ", strip=True).split())
            if not title:
                continue

            row = a.find_parent("tr")
            if row:
                cells = row.find_all("td")
                summary = " ".join(cells[0].get_text(" ", strip=True).split()) if cells else title
                location = " ".join(cells[1].get_text(" ", strip=True).split()) if len(cells) > 1 else default_city
            else:
                summary = title
                location = default_city

            jobs.append(
                {
                    "organization": organization,
                    "title": title,
                    "location": location or default_city,
                    "posted_date": "",
                    "url": href,
                    "summary": summary,
                }
            )

        return jobs
