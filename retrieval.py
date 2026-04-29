import requests
import xml.etree.ElementTree as ET
from ddgs import DDGS


def search_arxiv(query: str, max_results: int = 3) -> list:
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"arXiv API failed for query: {query}")
            return []
        root = ET.fromstring(response.text)
    except Exception as e:
        print(f"Error fetching arXiv for query '{query}': {e}")
        return []

    results = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        try:
            title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
            summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
            published = entry.find("{http://www.w3.org/2005/Atom}published").text[:10]
            link = entry.find("{http://www.w3.org/2005/Atom}id").text
            authors = []
            for author in entry.findall("{http://www.w3.org/2005/Atom}author"):
                name = author.find("{http://www.w3.org/2005/Atom}name").text
                authors.append(name)

            results.append({
                "title": title,
                "url": link,
                "source_type": "arxiv",
                "authors": authors,
                "published_date": published,
                "summary": summary
            })
        except:
            continue

    return results



import time
def search_web(query: str, max_results: int = 3) -> list:
    results = []
    try:
        time.sleep(1)
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results, timeout=10):
                results.append({
                    "title": r.get("title", "").strip(),
                    "url": r.get("href", ""),
                    "source_type": "web",
                    "authors": [],
                    "published_date": "",
                    "summary": r.get("body", "").strip()
                })
    except Exception as e:
        print(f"Web search failed for query '{query}': {e}")

    return results
