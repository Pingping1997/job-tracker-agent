from urllib.parse import urlsplit, urlunsplit

from .base import BaseScraper
from .common import fetch_html_soup


class OECDIEAScraper(BaseScraper):
    def fetch_jobs(self) -> list[dict]:
        url = self.source["url"]
        organization = self.source["organization"]
        default_city = self.source.get("city", "")

        soup = fetch_html_soup(url)
        jobs = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if "jobs.smartrecruiters.com/OECD/" not in href:
                continue

            # Remove tracking query params so URL stays stable across runs.
            parts = urlsplit(href)
            clean_url = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
            if clean_url in seen:
                continue
            seen.add(clean_url)

            raw_title = " ".join(a.get_text(" ", strip=True).split())
            if not raw_title:
                continue

            title = raw_title
            location = default_city
            if " Paris, France" in raw_title:
                title = raw_title.replace(" Paris, France", "").strip()
                location = "Paris, France"

            jobs.append(
                {
                    "organization": organization,
                    "title": title,
                    "location": location,
                    "posted_date": "",
                    "url": clean_url,
                    "summary": raw_title,
                }
            )

        return jobs
