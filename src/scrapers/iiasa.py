from .base import BaseScraper
from .common import fetch_html_soup, clean_href


class IIASAScraper(BaseScraper):
    BOARD_URL = "https://iiasa.onlyfy.jobs/"
    JOB_PATH = "/job/"

    def fetch_jobs(self) -> list[dict]:
        organization = self.source["organization"]
        default_city = self.source.get("city", "")

        soup = fetch_html_soup(self.BOARD_URL)
        jobs = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = clean_href(self.BOARD_URL, a["href"])
            href_lower = href.lower()

            if "iiasa.onlyfy.jobs" not in href_lower:
                continue
            if self.JOB_PATH not in href_lower:
                continue

            title = " ".join(a.get_text(" ", strip=True).split())
            if not title:
                continue

            if href in seen:
                continue
            seen.add(href)

            jobs.append(
                {
                    "organization": organization,
                    "title": title,
                    "location": default_city,
                    "posted_date": "",
                    "url": href,
                    "summary": title,
                }
            )

        return jobs
