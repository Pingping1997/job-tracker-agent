import pandas as pd

from db import init_db, upsert_job
from filters import load_keywords, match_keywords, score_job

from scrapers import (
    KTHScraper,
    NTNUScraper,
    ChalmersScraper,
    AalborgScraper,
    IAEAScraper,
    OECDIEAScraper,
    RMIScraper,
    CareersGovScraper,
    RambollScraper,
    AITScraper,
    CSHScraper,
    IIASAScraper,
    DTUOracleScraper,
    GenericHtmlScraper,
    GenericHubScraper,
    GenericJSScraper,
)


def get_scraper(source: dict):
    org = source.get("organization", "")
    source_type = source.get("source_type", "html")

    if org == "KTH":
        return KTHScraper(source)
    if org == "NTNU":
        return NTNUScraper(source)
    if org == "Chalmers":
        return ChalmersScraper(source)
    if org == "Aalborg University":
        return AalborgScraper(source)
    if org == "IAEA":
        return IAEAScraper(source)
    if org == "OECD IEA":
        return OECDIEAScraper(source)
    if org == "RMI":
        return RMIScraper(source)
    if org == "Careers@Gov":
        return CareersGovScraper(source)
    if org == "Ramboll":
        return RambollScraper(source)
    if org == "AIT":
        return AITScraper(source)
    if org == "CSH":
        return CSHScraper(source)
    if org == "IIASA":
        return IIASAScraper(source)
    if org == "DTU":
        return DTUOracleScraper(source)

    if source_type == "html":
        return GenericHtmlScraper(source)
    if source_type == "hub":
        return GenericHubScraper(source)
    if source_type == "javascript":
        return GenericJSScraper(source)

    return GenericHtmlScraper(source)


def main() -> None:
    init_db()
    keywords = load_keywords()
    sources = pd.read_csv("data/sources.csv").fillna("")

    total_found = 0
    total_stored = 0
    total_matched = 0

    for _, row in sources.iterrows():
        source = row.to_dict()
        organization = source.get("organization", "")

        print(f"\nChecking {organization} ...")

        try:
            scraper = get_scraper(source)
            jobs = scraper.fetch_jobs()
            print(f"  Found {len(jobs)} possible jobs")
            total_found += len(jobs)

            for job in jobs:
                full_text = " ".join([
                    job.get("title", ""),
                    job.get("location", ""),
                    job.get("summary", ""),
                ])

                matched = match_keywords(full_text, keywords)
                job["matched_keywords"] = ", ".join(matched)
                job["relevance_score"] = score_job(full_text, matched) if matched else 0

                upsert_job(job)
                total_stored += 1

                if matched:
                    total_matched += 1
                    print(f"  Matched: {job['title']}")
                    print(f"    Keywords: {job['matched_keywords']}")
                    print(f"    Score: {job['relevance_score']}")
                else:
                    print(f"  Stored only: {job['title']}")

        except Exception as e:
            print(f"  Failed: {e}")

    print("\nDone.")
    print(f"Total possible jobs found: {total_found}")
    print(f"Total stored jobs: {total_stored}")
    print(f"Total matched jobs: {total_matched}")


if __name__ == "__main__":
    main()