import os
import re
from functools import lru_cache
from pathlib import Path


def _resolve_docs_dir() -> Path:
    override = os.environ.get("OPENHEXA_DOCS_DIR")
    if override:
        return Path(override)
    here = Path(__file__).resolve()
    candidates = (
        here.parents[2] / "docs" / "en",  # docker image: /code/docs/en
        here.parents[3] / "docs" / "en",  # local dev: <repo>/docs/en
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


DOCS_DIR = _resolve_docs_dir()

_ALLOWED_SLUGS = frozenset(
    {
        "writing-pipelines",
        "cli",
        "sdk",
        "toolbox",
        "notebooks-advanced",
        "static-webapps",
    }
)

_HERO_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL)
_MD_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_TAG_RE = re.compile(r"<[^>]+>")
_HERO_BLOCK_RE = re.compile(r'<div\s+class="hero-section".*?</div>\s*</div>', re.DOTALL)


def _strip_tags(text: str) -> str:
    return _TAG_RE.sub("", text).strip()


def _extract_title(text: str, fallback: str) -> str:
    m = _HERO_H1_RE.search(text)
    if m:
        title = _strip_tags(m.group(1))
        if title:
            return title
    m = _MD_H1_RE.search(text)
    if m:
        return m.group(1).strip()
    return fallback


def _extract_summary(text: str) -> str:
    body = _HERO_BLOCK_RE.sub("", text, count=1)
    skip_prefixes = ("#", "<", "!", "```", "- ", "* ", "|", "    ")
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(skip_prefixes):
            continue
        if re.match(r"^\d+\.\s", s):
            continue
        cleaned = _strip_tags(s)
        cleaned = re.sub(r"\s+", " ", cleaned)
        if cleaned:
            return cleaned[:240]
    return ""


@lru_cache
def _load() -> dict[str, dict]:
    docs: dict[str, dict] = {}
    if not DOCS_DIR.is_dir():
        return docs
    for path in sorted(DOCS_DIR.glob("*.md")):
        slug = path.stem
        if slug not in _ALLOWED_SLUGS:
            continue
        text = path.read_text(encoding="utf-8")
        docs[slug] = {
            "name": slug,
            "title": _extract_title(text, slug),
            "summary": _extract_summary(text),
            "content": text,
        }
    return docs


def get_index() -> list[dict]:
    """Return [{name, title, summary}, ...] for every available doc."""
    return [
        {"name": d["name"], "title": d["title"], "summary": d["summary"]}
        for d in _load().values()
    ]


def read_doc(name: str) -> dict | None:
    """Return {name, title, content} for the given doc, or None if unknown."""
    doc = _load().get(name)
    if doc is None:
        return None
    return {"name": doc["name"], "title": doc["title"], "content": doc["content"]}


def available_doc_names() -> list[str]:
    return list(_load().keys())
