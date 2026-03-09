# Job Tracker Agent

A simple Python job tracker for university, research institute, and public-sector job pages.

## Features

- Reads job source URLs from `data/sources.csv`
- Scrapes simple HTML job listing pages
- Filters by keywords from `data/keywords.txt`
- Stores matched jobs in SQLite
- Generates monthly markdown summaries
- Runs automatically with GitHub Actions

## Project structure

```text
job-tracker-agent/
├── .github/workflows/job_tracker.yml
├── data/
│   ├── keywords.txt
│   └── sources.csv
├── reports/
├── src/
│   ├── db.py
│   ├── filters.py
│   ├── main.py
│   ├── report.py
│   └── scrapers.py
├── .gitignore
├── README.md
└── requirements.txt