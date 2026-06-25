"""
Create or refresh docs_md/dnext_business_page.md from the public Dnext website.

This is intentionally a manual, one-off utility. It should not be called from
the chat request path.
"""

from pathlib import Path

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://www.dnext.io/"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "docs_md" / "dnext_business_page.md"


def fetch_clean_text(url: str) -> str:
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    lines = []
    for text in soup.stripped_strings:
        if text not in lines:
            lines.append(text)

    return "\n".join(lines)


def build_snapshot(content: str) -> str:
    return f"""# Dnext Business Page Snapshot

This file is a manually refreshed snapshot of the public `dnext.io` business page.
It is stored locally so the chatbot can use it through the normal RAG pipeline
without scraping the website during every chat request.

*******

Snapshot Metadata

Source URL: {SOURCE_URL}
Refresh method: run `python scripts/scrape_dnext_business_page.py`

*******

Website Snapshot

{content}
"""


def main() -> None:
    content = fetch_clean_text(SOURCE_URL)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_snapshot(content), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
