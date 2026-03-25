import requests

from .base import BaseScraper


class RMIScraper(BaseScraper):
    JOBS_API_URL = "https://rockymountain.wd1.myworkdayjobs.com/wday/cxs/rockymountain/RMI/jobs"
    BASE_URL = "https://rockymountain.wd1.myworkdayjobs.com/en-US/RMI"

    def fetch_jobs(self) -> list[dict]:
        organization = self.source["organization"]
        default_city = self.source.get("city", "")

        jobs = []
        seen = set()

        limit = 20
        offset = 0

        while True:
            payload = {
                "limit": limit,
                "offset": offset,
                "searchText": "",
            }

            response = requests.post(self.JOBS_API_URL, json=payload, timeout=40)
            response.raise_for_status()
            data = response.json()

            postings = data.get("jobPostings", [])
            if not postings:
                break

            for posting in postings:
                external_path = str(posting.get("externalPath", "")).strip()
                title = " ".join(str(posting.get("title", "")).split())
                if not external_path or not title:
                    continue

                href = f"{self.BASE_URL}{external_path}"
                if href in seen:
                    continue
                seen.add(href)

                location = " ".join(str(posting.get("locationsText", default_city)).split())
                posted_date = " ".join(str(posting.get("postedOn", "")).split())

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

            total = int(data.get("total", 0) or 0)
            offset += limit
            if offset >= total:
                break

        return jobs
