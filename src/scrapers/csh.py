from .base import BaseScraper
from .common import fetch_html_soup, clean_href


class CSHScraper(BaseScraper):
    EXTERNAL_JOB_HOST = "career.it-u.at"
    EXTERNAL_JOB_PATH = "/en/Job/"
    PERSONIO_URL = "https://csh.jobs.personio.com/"
    PERSONIO_JOB_PATH = "/job/"

    def fetch_jobs(self) -> list[dict]:
        url = self.source["url"]
        organization = self.source["organization"]
        default_city = self.source.get("city", "")

        soup = fetch_html_soup(url)
        personio_soup = fetch_html_soup(self.PERSONIO_URL)
        jobs = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = clean_href(url, a["href"])
            href_lower = href.lower()

            if self.EXTERNAL_JOB_HOST not in href_lower:
                continue
            if self.EXTERNAL_JOB_PATH.lower() not in href_lower:
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

        for a in personio_soup.find_all("a", href=True):
            href = clean_href(self.PERSONIO_URL, a["href"])
            href_lower = href.lower()

            if "csh.jobs.personio.com" not in href_lower:
                continue
            if self.PERSONIO_JOB_PATH not in href_lower:
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
