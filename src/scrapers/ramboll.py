import math
import requests

from .base import BaseScraper


class RambollScraper(BaseScraper):
    API_URL = "https://www.ramboll.com/api/jobsPosts"
    BASE_URL = "https://www.ramboll.com/careers"

    def fetch_jobs(self) -> list[dict]:
        organization = self.source["organization"]

        jobs = []
        seen = set()

        first_page = self._fetch_page(page_number=1)
        first_data = self._extract_data(first_page)

        page_size = int(first_data.get("pageSize", 10) or 10)
        total_records = int(first_data.get("totalRecordCount", 0) or 0)
        total_pages = max(1, math.ceil(total_records / page_size)) if page_size > 0 else 1

        self._append_jobs(first_data.get("jobPosts", []), organization, jobs, seen)

        for page_number in range(2, total_pages + 1):
            page_json = self._fetch_page(page_number=page_number)
            page_data = self._extract_data(page_json)
            self._append_jobs(page_data.get("jobPosts", []), organization, jobs, seen)

        return jobs

    def _fetch_page(self, page_number: int) -> dict:
        params = {
            "locale": "en",
            "countries": "",
            "workplace": "",
            "market": "",
            "careerStage": "",
            "search": "",
            "pageNumber": page_number,
        }

        response = requests.get(self.API_URL, params=params, timeout=40)
        response.raise_for_status()
        return response.json()

    def _extract_data(self, payload: dict) -> dict:
        return payload.get("jobsPosts", {}).get("data", {})

    def _append_jobs(
        self,
        postings: list[dict],
        organization: str,
        jobs: list[dict],
        seen: set[str],
    ) -> None:
        for posting in postings:
            job_id = str(posting.get("jobPostId", "")).strip()
            title = " ".join(str(posting.get("title", "")).split())
            if not job_id or not title:
                continue

            href = f"{self.BASE_URL}/{job_id}"
            if href in seen:
                continue
            seen.add(href)

            location_bits = [
                str(posting.get("location", "")).strip(),
                str(posting.get("country", "")).strip(),
            ]
            location = ", ".join([bit for bit in location_bits if bit])

            summary = " ".join(
                part
                for part in [
                    title,
                    str(posting.get("market", "")).strip(),
                    str(posting.get("teaser", "")).strip(),
                ]
                if part
            )

            jobs.append(
                {
                    "organization": organization,
                    "title": title,
                    "location": location,
                    "posted_date": str(posting.get("postingStartDate", "")).strip(),
                    "url": href,
                    "summary": summary,
                }
            )
