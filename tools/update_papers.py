#!/usr/bin/env python3
"""Refresh _data/papers.yml from arXiv (paper list) and Crossref (journal, volume, year).

    python3 tools/update_papers.py

Hand edits in _data/papers.yml that survive re-runs:
  "role": "first" | "coauthor"     which Publications section a paper goes in
  "hide": true                     drop a paper that isn't yours
  "fix": {"year": 2025, ...}       override any field (year, venue, doi, title, ...)
Everything else is regenerated. Standard library only.
"""
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "_data" / "papers.yml"
QUERIES = ['au:"Matthew T. Miles"', 'au:"M. T. Miles"', 'au:"Matthew Miles"', "au:Miles_M_T",
           'au:Miles_M AND (abs:pulsar OR abs:"gravitational wave")']
# Author-name strings that are you. Anything else with "Miles" in it is someone else.
ME = re.compile(r"^(Matthew|Matt|M\.)\s*(T\.?\s*)?Miles$")
CATS = ("astro-ph", "gr-qc")
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
JOURNALS = {
    "Monthly Notices of the Royal Astronomical Society": "MNRAS",
    "The Astrophysical Journal Letters": "ApJL",
    "The Astrophysical Journal": "ApJ",
    "The Astrophysical Journal Supplement Series": "ApJS",
    "Publications of the Astronomical Society of Australia": "PASA",
    "Physical Review D": "PRD",
    "Physical Review Letters": "PRL",
    "Astronomy & Astrophysics": "A&A",
    "Classical and Quantum Gravity": "CQG",
}
# First MNRAS volume of each year. Crossref dates January issues to the previous
# December, but ADS (and everyone citing them) uses the volume year.
MNRAS_YEAR_START = {500: 2021, 509: 2022, 518: 2023, 527: 2024, 536: 2025}
UA = {"User-Agent": "matttmiles.github.io paper updater (mailto:noreply@github.com)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def arxiv(query):
    return ET.fromstring(get("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": query, "sortBy": "submittedDate", "sortOrder": "descending", "max_results": 300})))


def crossref(doi):
    try:
        m = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))["message"]
    except Exception as e:  # leave arXiv details in place
        print(f"  crossref failed for {doi}: {e}")
        return {}
    journal = (m.get("container-title") or [""])[0]
    venue = JOURNALS.get(journal, journal)
    date = (m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0]
    year, vol = date[0], m.get("volume", "")
    if venue == "MNRAS" and vol.isdigit():
        starts = [v for v in MNRAS_YEAR_START if v <= int(vol)]
        if starts and int(vol) < max(MNRAS_YEAR_START) + 9:
            year = MNRAS_YEAR_START[max(starts)]
    page = m.get("page") or m.get("article-number") or ""
    page = page.split("-")[0]
    if re.fullmatch(r"sta[a-z]\d+", page):  # MNRAS DOI suffix, not a page number
        page = ""
    return {"venue": venue + (f" {vol}" if vol else "") + (f", {page}" if page else ""), "year": year}


def norm(t):
    return re.sub(r"[^a-z0-9]", "", clean(t).lower().replace("\u2212", "").replace("\u2013", ""))


def find_doi(title):
    """DOI for a published paper whose arXiv entry has none; exact title match only."""
    try:
        items = json.loads(get("https://api.crossref.org/works?rows=5&select=DOI,title,type&query.bibliographic="
                               + urllib.parse.quote(clean(title))))["message"]["items"]
    except Exception:
        return ""
    for it in items:
        if it.get("type") == "journal-article" and norm((it.get("title") or [""])[0]) == norm(title):
            return it["DOI"]
    return ""


def clean(title):
    t = " ".join(title.split())
    t = t.replace("$-$", "−").replace("--", "–")
    return re.sub(r"\$([^$]*)\$", r"\1", t)


def short_authors(authors, pos):
    me = "**M. T. Miles**"
    if pos == 1:
        return me + (" et al." if len(authors) > 1 else "")
    if len(authors) <= 4:
        return ", ".join(me if i + 1 == pos else a for i, a in enumerate(authors))
    return f"{authors[0]} et al. (incl. {me})"


def load_existing():
    # papers.yml is written by this script as one JSON object per list item, which is valid YAML.
    if not OUT.exists():
        return {}
    return {d["arxiv"]: d for d in (json.loads(l[2:]) for l in OUT.read_text().splitlines() if l.startswith("- {"))}


def main():
    existing = load_existing()
    papers = {}
    for q in QUERIES:
        for e in arxiv(q).findall("a:entry", NS):
            if not e.find("a:category", NS).get("term").startswith(CATS):
                continue
            authors = [a.find("a:name", NS).text.strip() for a in e.findall("a:author", NS)]
            pos = next((i + 1 for i, a in enumerate(authors) if ME.match(a)), None)
            if pos is None:
                continue
            aid = re.sub(r"v\d+$", "", e.find("a:id", NS).text.rsplit("/abs/", 1)[-1])
            doi = e.find("x:doi", NS)
            papers[aid] = {
                "arxiv": aid,
                "title": clean(e.find("a:title", NS).text),
                "authors": short_authors(authors, pos),
                "n_authors": len(authors),
                "position": pos,
                "year": int(e.find("a:published", NS).text[:4]),
                "venue": "arXiv preprint",
                "doi": doi.text.strip() if doi is not None else "",
                "role": "first" if pos == 1 else "coauthor",
            }
        time.sleep(3)  # arXiv asks for >= 3 s between requests

    for aid, old in existing.items():
        if aid not in papers:
            papers[aid] = old  # added by hand / no longer matched
            continue
        for k in ("hide", "fix"):
            if k in old:
                papers[aid][k] = old[k]
        if old.get("role") == "first" or (old.get("role") == "coauthor" and papers[aid]["position"] != 1):
            papers[aid]["role"] = old["role"]

    for p in papers.values():
        if not p["doi"] and not p.get("hide"):
            p["doi"] = find_doi(p["title"])
        if p["doi"] and not p.get("hide"):
            p.update(crossref(p["doi"]))
        p.update(p.get("fix", {}))
        p["title"] = clean(p["title"])

    rows = sorted(papers.values(), key=lambda p: (p["year"], p["arxiv"]), reverse=True)
    header = "# Generated by tools/update_papers.py. Hand edits kept: \"role\", \"hide\", \"fix\" (see script docstring).\n"
    OUT.write_text(header + "".join("- " + json.dumps(p, ensure_ascii=False) + "\n" for p in rows))
    shown = [p for p in rows if not p.get("hide")]
    print(f"wrote {len(rows)} papers ({len(shown)} shown: {sum(p['role'] == 'first' for p in shown)} first-author) to {OUT}")


if __name__ == "__main__":
    main()
