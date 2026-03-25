from pathlib import Path
import re

KEYWORDS_PATH = Path("data/keywords.txt")

# Map Dutch terms to existing canonical keywords used in data/keywords.txt.
DUTCH_KEYWORD_ALIASES: dict[str, set[str]] = {
    "energy": {"energie"},
    "climate": {"klimaat"},
    "climate change": {"klimaatverandering"},
    "carbon": {"koolstof"},
    "carbon management": {"koolstofbeheer"},
    "ccs": {"koolstofafvang en opslag", "co2-opslag", "co2 opslag"},
    "ccus": {"co2-afvang", "co2 afvang", "koolstofafvang en gebruik"},
    "carbon capture": {"koolstofafvang", "co2-afvang", "co2 afvang"},
    "co2": {"co2", "kooldioxide"},
    "decarbonization": {"decarbonisatie", "dekarbonisatie"},
    "decarbonisation": {"decarbonisatie", "dekarbonisatie"},
    "power-to-x": {"power-to-x", "power to x"},
    "powertox": {"powertox"},
    "ptx": {"ptx"},
    "hydrogen": {"waterstof"},
    "negative emissions": {"negatieve emissies"},
    "cdr": {"koolstofverwijdering", "co2-verwijdering", "co2 verwijdering"},
    "dac": {"directe luchtafvang"},
    "daccs": {"directe luchtafvang met opslag"},
    "beccs": {"bio-energie met koolstofafvang", "bioenergie met koolstofafvang"},
    "sustainability": {"duurzaamheid"},
    "sustainable": {"duurzaam"},
    "lca": {"lca", "levenscyclusanalyse"},
    "life cycle assessment": {"levenscyclusanalyse"},
    "energy systems": {"energiesystemen"},
    "systems modelling": {"systeemmodellering"},
    "systems modeling": {"systeemmodellering"},
    "optimization": {"optimalisatie", "optimaliseren"},
    "optimisation": {"optimalisatie", "optimaliseren"},
    "industrial decarbonization": {"industriele decarbonisatie", "industriele dekarbonisatie"},
    "industrial decarbonisation": {"industriele decarbonisatie", "industriele dekarbonisatie"},
    "net zero": {"netto nul", "netto-nul", "klimaatneutraal"},
    "emissions": {"emissies", "uitstoot"},
    "transition": {"transitie", "energietransitie"},
    "industrial ecology": {"industriele ecologie"},
    "game theory": {"speltheorie"},
}


def load_keywords() -> list[str]:
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def _contains_phrase(text: str, phrase: str) -> bool:
    phrase = phrase.strip().lower()
    if not phrase:
        return False

    # Match whole words while allowing flexible whitespace between phrase tokens.
    pattern = r"\b" + re.escape(phrase).replace(r"\ ", r"\s+") + r"\b"
    return re.search(pattern, text) is not None


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    text = (text or "").lower()
    matched = []

    for kw in keywords:
        if _contains_phrase(text, kw):
            matched.append(kw)
            continue

        aliases = DUTCH_KEYWORD_ALIASES.get(kw, set())
        if any(_contains_phrase(text, alias) for alias in aliases):
            matched.append(kw)

    return matched


def score_job(text: str, matched: list[str]) -> int:
    score = 0
    text_lower = (text or "").lower()

    direct = {
        "ccs", "ccus", "carbon capture", "carbon management",
        "dac", "daccs", "beccs", "cdr"
    }
    adjacent = {
        "energy", "climate", "decarbonization", "decarbonisation",
        "co2", "power-to-x", "ptx", "hydrogen", "renewable",
        "transition", "net zero", "emissions", "sustainable"
    }
    future = {
        "optimization", "optimisation", "energy systems",
        "systems modelling", "systems modeling",
        "lca", "life cycle assessment", "industrial ecology"
    }

    for kw in matched:
        if kw in direct:
            score += 5
        elif kw in adjacent:
            score += 3
        elif kw in future:
            score += 2
        else:
            score += 1

    if "vienna" in text_lower:
        score += 2

    return score