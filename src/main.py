import pandas as pd

from db import init_db, upsert_job
from filters import load_keywords, match_keywords, score_job
from scrapers import scrape_generic_jobs


def main() -> None:
    init_db()
    keywords = load_keywords()
    sources = pd.read_csv("data/sources.csv").fillna("")

    total_found = 0
    total_matched = 0

    for _, row in sources.iterrows():
        organization = row["organization"]
        city = row["city"]
        url = row["url"]

        print(f"\nChecking {organization} ...")

        try:
            jobs = scrape_generic_jobs(organization, city, url)
            print(f"  Found {len(jobs)} possible jobs")

            total_found += len(jobs)

            for job in jobs:
                full_text = " ".join([
                    job.get("title", ""),
                    job.get("location", ""),
                    job.get("summary", ""),
                ])

                matched = match_keywords(full_text, keywords)
                if not matched:
                    continue

                job["matched_keywords"] = ", ".join(matched)
                job["relevance_score"] = score_job(full_text, matched)

                upsert_job(job)
                total_matched += 1

                print(f"  Matched: {job['title']}")
                print(f"    Keywords: {job['matched_keywords']}")
                print(f"    Score: {job['relevance_score']}")

        except Exception as e:
            print(f"  Failed: {e}")

    print("\nDone.")
    print(f"Total possible jobs found: {total_found}")
    print(f"Total matched jobs stored: {total_matched}")


if __name__ == "__main__":
    main()