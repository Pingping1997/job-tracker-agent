import requests

from .base import BaseScraper
from .common import USER_AGENT, clean_href


class DTUOracleScraper(BaseScraper):
    API_URL = "https://efzu.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
    SITE_NUMBER = "CX_2001"
    FACETS = "LOCATIONS;WORK_LOCATIONS;WORKPLACE_TYPES;TITLES;CATEGORIES;ORGANIZATIONS;POSTING_DATES;FLEX_FIELDS"
    EXPAND = (
        "requisitionList.workLocation,requisitionList.otherWorkLocations,"
        "requisitionList.secondaryLocations,flexFieldsFacet.values,"
        "requisitionList.requisitionFlexFields"
    )
    PAGE_LIMIT = 25

    def _fetch_batch(self, offset: int) -> dict:
        finder = (
            f"findReqs;siteNumber={self.SITE_NUMBER},"
            f"facetsList={self.FACETS},"
            f"limit={self.PAGE_LIMIT},"
            f"offset={offset},"
            "sortBy=POSTING_DATES_DESC"
        )

        params = {
            "onlyData": "true",
            "expand": self.EXPAND,
            "finder": finder,
        }
        response = requests.get(self.API_URL, params=params, headers=USER_AGENT, timeout=45)
        response.raise_for_status()
        return response.json()

    def fetch_jobs(self) -> list[dict]:
        source_url = self.source["url"]
        organization = self.source["organization"]
        default_city = self.source.get("city", "")

        jobs = []
        seen = set()
        offset = 0
        total_jobs = None

        while True:
            payload = self._fetch_batch(offset)
            items = payload.get("items") or []
            if not items:
                break

            page = items[0] if isinstance(items[0], dict) else {}
            requisitions = page.get("requisitionList") or []

            if total_jobs is None:
                total_jobs = page.get("TotalJobsCount", 0)

            if not requisitions:
                break

            for req in requisitions:
                req_id = str(req.get("Id", "")).strip()
                if not req_id:
                    continue

                href = clean_href(
                    source_url,
                    f"/hcmUI/CandidateExperience/en/sites/{self.SITE_NUMBER}/job/{req_id}",
                )
                if href in seen:
                    continue
                seen.add(href)

                title = " ".join((req.get("Title") or "").split())
                if not title:
                    continue

                summary = " ".join((req.get("ShortDescriptionStr") or title).split())
                location = " ".join((req.get("PrimaryLocation") or default_city).split())

                jobs.append(
                    {
                        "organization": organization,
                        "title": title,
                        "location": location,
                        "posted_date": req.get("PostedDate", ""),
                        "url": href,
                        "summary": summary,
                    }
                )

            offset += len(requisitions)

            if len(requisitions) < self.PAGE_LIMIT:
                break
            if total_jobs is not None and offset >= int(total_jobs):
                break

        return jobs