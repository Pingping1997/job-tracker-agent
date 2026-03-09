from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}


def fetch_html(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=USER_AGENT, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def looks_like_job_title(text: str) -> bool:
    if not text or len(text) < 8:
        return False

    text_lower = text.lower()

    title_keywords = [
        "postdoc", "phd", "research", "scientist", "engineer",
        "analyst", "professor", "project", "fellow", "manager",
        "associate", "assistant", "consultant", "policy", "student"
    ]

    return any(k in text_lower for k in title_keywords)


def scrape_generic_jobs(organization: str, city: str, url: str) -> list[dict]:
    soup = fetch_html(url)

    jobs = []
    seen = set()

    for a in soup.find_all("a", href=True):
        title = a.get_text(" ", strip=True)
        href = urljoin(url, a["href"])

        if not looks_like_job_title(title):
            continue

        if href in seen:
            continue
        seen.add(href)

        jobs.append({
            "organization": organization,
            "title": title,
            "location": city or "",
            "posted_date": "",
            "url": href,
            "summary": title,
        })

    return jobs