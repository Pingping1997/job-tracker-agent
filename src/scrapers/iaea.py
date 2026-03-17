from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .base import BaseScraper
from .common import clean_href


class IAEAScraper(BaseScraper):
    def fetch_jobs(self) -> list[dict]:
        url = self.source["url"]
        organization = self.source["organization"]
        default_city = self.source.get("city", "")

        jobs = []
        seen = set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)

            # Ensure the actual openings table is visible.
            try:
                page.evaluate(
                    """() => {
                        const btn = document.querySelector('#clearButton');
                        if (btn) btn.click();
                    }"""
                )
                page.wait_for_timeout(1500)
            except Exception:
                pass

            try:
                page.wait_for_selector("a[href*='jobdetail.ftl?job=']", timeout=15000)
            except Exception:
                browser.close()
                return jobs

            self._collect_page_jobs(page.content(), url, organization, default_city, jobs, seen)

            # Follow pagination when available.
            for _ in range(4):
                before = len(seen)
                moved = False
                try:
                    moved = page.evaluate(
                        """() => {
                            const next = document.querySelector('#next');
                            if (!next) return false;

                            const parentClass = (next.parentElement?.className || '').toLowerCase();
                            const nextClass = (next.className || '').toLowerCase();
                            const fullClass = parentClass + ' ' + nextClass;
                            if (fullClass.includes('disabled')) return false;

                            next.click();
                            return true;
                        }"""
                    )
                except Exception:
                    moved = False

                if not moved:
                    break

                page.wait_for_timeout(2000)
                page.wait_for_load_state("networkidle", timeout=15000)
                self._collect_page_jobs(page.content(), url, organization, default_city, jobs, seen)

                if len(seen) == before:
                    break

            browser.close()

        return jobs

    def _collect_page_jobs(
        self,
        html: str,
        base_url: str,
        organization: str,
        default_city: str,
        jobs: list[dict],
        seen: set[str],
    ) -> None:
        soup = BeautifulSoup(html, "lxml")

        for row in soup.find_all("tr"):
            link = row.select_one("a[href*='jobdetail.ftl?job=']")
            if not link:
                continue

            title = link.get_text(" ", strip=True)
            href = clean_href(base_url, link.get("href", ""))
            href = href.replace(" ", "%20")

            if not title or not href or href in seen:
                continue
            seen.add(href)

            cells = row.find_all("td")
            location = default_city
            posted_date = ""

            if len(cells) >= 3:
                location = cells[1].get_text(" ", strip=True)
                posted_date = cells[2].get_text(" ", strip=True)

            jobs.append(
                {
                    "organization": organization,
                    "title": title,
                    "location": location,
                    "posted_date": posted_date,
                    "url": href,
                    "summary": title,
                }
            )