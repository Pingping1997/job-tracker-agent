from pathlib import Path

KEYWORDS_PATH = Path("data/keywords.txt")


def load_keywords() -> list[str]:
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    text = (text or "").lower()
    return [kw for kw in keywords if kw in text]


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
        "transition", "net zero"
    }
    future = {
        "optimization", "optimisation", "energy systems",
        "systems modelling", "lca", "life cycle assessment", "policy"
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