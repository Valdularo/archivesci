#!/usr/bin/env python3
"""Build the local search index from the mirrored collection pages."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
OUTPUT = ROOT / "catalog.js"
TRANSCRIPT_NAVIGATION = ARCHIVE / "transcript-navigation.js"
TRANSCRIPT_NAVIGATION_TAG = '<script defer charset="utf-8" src="transcript-navigation.js"></script>'
TRANSCRIPT_NAVIGATION_PATTERN = re.compile(
    r"<script\b[^>]*\bsrc=[\"']transcript-navigation\.js[\"'][^>]*></script>",
    re.IGNORECASE,
)


class CollectionParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.heading = []
        self.in_heading = False
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and attrs.get("id") == "main":
            self.in_main = True
        elif tag == "h2" and self.in_main:
            self.in_heading = True
        elif tag == "tr" and self.in_main:
            self.row = []
        elif tag == "td" and self.row is not None:
            self.cell = {"text": [], "href": None}
        elif tag == "a" and self.cell is not None and self.cell["href"] is None:
            self.cell["href"] = attrs.get("href")

    def handle_data(self, data):
        if self.in_heading:
            self.heading.append(data)
        if self.cell is not None:
            self.cell["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "h2":
            self.in_heading = False
        elif tag == "td" and self.cell is not None:
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def collection_title(filename):
    name = Path(filename).stem
    if name.startswith("Chapter_"):
        name = name.removeprefix("Chapter_").rsplit("_", 1)[0]
        return "Chapter " + name.replace("_", " ")
    name = re.sub(r"_\d+$", "", name)
    return name.replace("__", " & ").replace("_", " ").title().replace("Npc", "NPC")


def collection_sort_key(path):
    chapter = re.match(r"Chapter_(\d+)\.(\d+)(?:_and_Beyond)?_", path.name)
    if chapter:
        beyond = "_and_Beyond_" in path.name
        return (0, int(chapter.group(1)), int(chapter.group(2)), int(beyond), path.name)
    return (1, path.name.casefold())


def parse_collection(path):
    parser = CollectionParser()
    parser.feed(path.read_text(encoding="latin-1", errors="replace"))
    if "Archive Databanks" not in "".join(parser.heading):
        return None

    records = []
    for row in parser.rows:
        if len(row) < 2:
            continue
        href = row[0]["href"]
        if not href:
            continue
        parsed = urlparse(href)
        if parsed.scheme or parsed.netloc or parsed.path.startswith(("/", "#")):
            continue
        target = unquote(parsed.path)
        if not target.lower().endswith((".htm", ".html")):
            continue
        target_path = (ARCHIVE / target).resolve()
        if not target_path.is_relative_to(ARCHIVE.resolve()):
            continue
        records.append(
            {
                "title": " ".join("".join(row[0]["text"]).split()),
                "summary": " ".join("".join(row[1]["text"]).split()),
                "path": f"archive/{target}",
                "available": target_path.is_file(),
            }
        )
    return records


def build_transcript_navigation(records):
    available = [record for record in records if record["available"]]
    navigation = {}
    for index, record in enumerate(available):
        navigation[Path(record["path"]).name] = {
            "title": record["title"],
            "collection": record["collection"],
            "position": index + 1,
            "total": len(available),
            "previous": (
                {
                    "path": Path(available[index - 1]["path"]).name,
                    "title": available[index - 1]["title"],
                }
                if index > 0
                else None
            ),
            "next": (
                {
                    "path": Path(available[index + 1]["path"]).name,
                    "title": available[index + 1]["title"],
                }
                if index + 1 < len(available)
                else None
            ),
        }

    payload = json.dumps(navigation, ensure_ascii=True, separators=(",", ":"))
    TRANSCRIPT_NAVIGATION.write_text(
        f"""(() => {{
  const entries = {payload};
  const current = entries[decodeURIComponent(location.pathname.split('/').pop())];
  const transcript = document.querySelector('.transcript-content');
  if (!current || !transcript) return;

  const navigation = document.createElement('nav');
  navigation.className = 'transcript-navigation';
  navigation.setAttribute('aria-label', 'Transcript sequence');

  function createLink(entry, direction, label) {{
    if (!entry) {{
      const unavailable = document.createElement('span');
      unavailable.className = 'transcript-navigation-link is-unavailable';
      unavailable.setAttribute('aria-disabled', 'true');
      unavailable.textContent = label;
      return unavailable;
    }}

    const link = document.createElement('a');
    link.className = `transcript-navigation-link is-${{direction}}`;
    link.href = entry.path;
    link.textContent = label;
    link.title = entry.title;
    return link;
  }}

  const previous = createLink(current.previous, 'previous', '\\u2190 Previous transcript');
  const position = document.createElement('span');
  position.className = 'transcript-navigation-position';
  position.textContent = `${{current.position}} of ${{current.total}} \\u00b7 ${{current.collection}}`;
  const next = createLink(current.next, 'next', 'Next transcript \\u2192');

  navigation.append(previous, position, next);
  transcript.prepend(navigation);
}})();
""",
        encoding="utf-8",
    )

    for record in available:
        transcript_path = ROOT / record["path"]
        source = transcript_path.read_bytes().decode("latin-1")
        existing_tag = TRANSCRIPT_NAVIGATION_PATTERN.search(source)
        if existing_tag:
            line_end = existing_tag.end()
            if source.startswith("\r\n", line_end):
                line_end += 2
            elif source.startswith("\n", line_end):
                line_end += 1
            source = (
                source[: existing_tag.start()]
                + TRANSCRIPT_NAVIGATION_TAG
                + "\n"
                + source[line_end:]
            )
            transcript_path.write_bytes(source.encode("latin-1"))
            continue
        closing_head = re.search(r"</head\s*>", source, re.IGNORECASE)
        if not closing_head:
            raise ValueError(f"Transcript has no closing head tag: {transcript_path}")
        source = (
            source[: closing_head.start()]
            + f"    {TRANSCRIPT_NAVIGATION_TAG}\n"
            + source[closing_head.start() :]
        )
        transcript_path.write_bytes(source.encode("latin-1"))


def main():
    collections = []
    records = []
    for path in sorted(ARCHIVE.glob("*.html"), key=collection_sort_key):
        entries = parse_collection(path)
        if entries is None:
            continue
        collection = {
            "id": path.name,
            "title": collection_title(path.name),
            "path": f"archive/{path.name}",
            "count": len(entries),
        }
        collections.append(collection)
        for entry in entries:
            records.append(
                {
                    **entry,
                    "collectionId": collection["id"],
                    "collection": collection["title"],
                }
            )

    build_transcript_navigation(records)

    payload = json.dumps(
        {"collections": collections, "records": records},
        ensure_ascii=True,
        separators=(",", ":"),
    )
    OUTPUT.write_text(f"window.ARCHIVE_CATALOG={payload};\n", encoding="utf-8")
    missing = sum(not entry["available"] for entry in records)
    print(f"Indexed {len(records)} entries in {len(collections)} collections ({missing} transcript files not captured).")


if __name__ == "__main__":
    main()
