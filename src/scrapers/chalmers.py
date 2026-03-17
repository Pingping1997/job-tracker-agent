import re

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper


class ChalmersScraper(BaseScraper):
    SCRIPT_RE = re.compile(r"customerjs/I003-304-5\.js")
    DEFAULT_SCRIPT_URL = "https://web103.reachmee.com/customerjs/I003-304-5.js"

    def fetch_jobs(self) -> list[dict]:
        organization = self.source["organization"]
        city = self.source.get("city", "")

        page_resp = requests.get(self.source["url"], timeout=40)
        page_resp.raise_for_status()
        soup = BeautifulSoup(page_resp.text, "lxml")

        script_url = ""
        for script in soup.find_all("script", src=True):
            src = script.get("src", "")
            if self.SCRIPT_RE.search(src):
                script_url = src if src.startswith("http") else f"https://web103.reachmee.com{src}"
                break

        if not script_url:
            script_url = self.DEFAULT_SCRIPT_URL

        script_resp = requests.get(script_url, timeout=40)
        script_resp.raise_for_status()
        script_text = script_resp.text

        validator = self._extract_js_value(script_text, "validator")
        iid = self._extract_js_value(script_text, "iid")
        customer = self._extract_js_value(script_text, "customer")
        site = self._extract_js_value(script_text, "site")
        lang = self._extract_js_value(script_text, "langDef") or "UK"

        if not validator or not iid or not customer or not site:
            return []

        jobs_url = (
            f"https://web103.reachmee.com/ext/{iid}/{customer}/main"
            f"?site={site}&validator={validator}&lang={lang}&ref=&notrack=1"
        )
        jobs_resp = requests.get(jobs_url, timeout=40)
        jobs_resp.raise_for_status()

        jobs_soup = BeautifulSoup(jobs_resp.text, "lxml")
        jobs = []
        seen = set()

        for row in jobs_soup.select("#jobsTable tbody tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            link = cells[1].find("a", href=True)
            if not link:
                continue

            title = " ".join(link.get_text(" ", strip=True).split())
            href = link["href"].strip()
            if not href or href in seen:
                continue
            seen.add(href)

            raw_deadline = " ".join(cells[2].get_text(" ", strip=True).split())
            iso_deadline = re.search(r"\d{4}-\d{2}-\d{2}", raw_deadline)
            posted_date = iso_deadline.group(0) if iso_deadline else raw_deadline
            location = city
            if len(cells) >= 4:
                location = " ".join(cells[3].get_text(" ", strip=True).split())

            summary = title
            if len(cells) >= 5:
                summary = f"{title} {' '.join(cells[4].get_text(' ', strip=True).split())}".strip()

            jobs.append(
                {
                    "organization": organization,
                    "title": title,
                    "location": location,
                    "posted_date": posted_date,
                    "url": href,
                    "summary": summary,
                }
            )

        return jobs

    @staticmethod
    def _extract_js_value(script_text: str, key: str) -> str:
        match = re.search(rf"var\s+{re.escape(key)}\s*=\s*'([^']*)'", script_text)
        return match.group(1).strip() if match else ""