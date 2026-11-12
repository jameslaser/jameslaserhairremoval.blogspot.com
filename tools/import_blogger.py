#!/usr/bin/env python3
"""Import Blogger posts into src/posts/.

Accepts either:
  * a Blogger backup file  (Blogger > Settings > Manage blog > Back up content), or
  * the blog's public Atom feed saved as a file
    (https://YOURBLOG.blogspot.com/feeds/posts/default?max-results=500)

Each published post becomes src/posts/YYYY-MM-DD-slug.html with its
title, date, labels and full HTML body. The slug is taken from the
Blogger address, so /2026/11/my-post.html keeps the same path here.

Usage:
  python3 tools/import_blogger.py blog-backup.xml            # published posts
  python3 tools/import_blogger.py blog-backup.xml --drafts   # include drafts (marked draft: true)
  python3 tools/import_blogger.py blog-backup.xml --force    # overwrite existing files
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

ATOM = "{http://www.w3.org/2005/Atom}"
APP = "{http://purl.org/atom/app#}"
BLOGGER = "{http://schemas.google.com/blogger/2018}"
KIND = "http://schemas.google.com/g/2005#kind"
RIYADH = timezone(timedelta(hours=3))

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "posts"


def text(el, tag):
    found = el.find(tag)
    return (found.text or "").strip() if found is not None and found.text else ""


def parse_date(value):
    value = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(RIYADH)


def slug_from_path(path):
    m = re.search(r"/([^/]+?)\.html?$", path or "")
    return m.group(1) if m else None


def fallback_slug(title, dt):
    s = re.sub(r"[^\w\s-]", "", title.lower(), flags=re.ASCII)
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s[:70] or f"post-{dt:%Y%m%d-%H%M}"


def entry_kind(entry):
    """Return ('post'|'page'|'comment'|'other', is_draft)."""
    # Newer Blogger backup format
    btype = text(entry, BLOGGER + "type")
    if btype:
        status = text(entry, BLOGGER + "status").upper()
        return btype.lower(), status not in ("LIVE", "")
    # Classic backup format / public feed
    kind = "post"
    for c in entry.findall(ATOM + "category"):
        if c.get("scheme") == KIND:
            kind = c.get("term", "").rsplit("#", 1)[-1]
    control = entry.find(APP + "control")
    draft = control is not None and text(control, APP + "draft") == "yes"
    return kind, draft


def labels_of(entry):
    out = []
    for c in entry.findall(ATOM + "category"):
        if c.get("scheme") == KIND:
            continue
        term = (c.get("term") or "").strip()
        if term and not term.startswith("http") and term not in out:
            out.append(term)
    return out


def post_path(entry):
    fn = text(entry, BLOGGER + "filename")
    if fn:
        return fn
    for link in entry.findall(ATOM + "link"):
        if link.get("rel") == "alternate":
            return link.get("href", "")
    return ""


def label_slug(s):
    s = re.sub(r"['’]", "", s.strip().lower())
    return re.sub(r"[\W_]+", "-", s).strip("-")


def relink(body, host):
    """Point links to the blog's own posts and labels at this site instead of Blogger."""
    if not host:
        return body
    h = re.escape(host)
    body = re.sub(rf"https?://{h}(/\d{{4}}/\d{{2}}/[^\"'?#\s]+\.html)(?:\?m=1)?", r"\1", body)

    def label(m):
        from urllib.parse import unquote
        return f"/labels/{label_slug(unquote(m.group(1)).replace('+', ' '))}/"

    body = re.sub(rf"https?://{h}/search/label/([^\"'?#\s]+)(?:\?[^\"'#\s]*)?", label, body)
    return body


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="Blogger backup .xml or saved Atom feed")
    ap.add_argument("--drafts", action="store_true", help="also import drafts (kept unpublished)")
    ap.add_argument("--host", default="jameslaserhairremoval.blogspot.com",
                    help="old blog address whose internal links should be rewritten")
    ap.add_argument("--force", action="store_true", help="overwrite posts that already exist")
    args = ap.parse_args()

    try:
        root = ET.parse(args.file).getroot()
    except ET.ParseError as e:
        sys.exit(f"Could not read {args.file} as XML: {e}")

    host = args.host
    if host:
        print(f"Rewriting links to {host} so they stay on the new site.")

    OUT.mkdir(parents=True, exist_ok=True)
    made = skipped = 0
    for entry in root.iter(ATOM + "entry"):
        kind, draft = entry_kind(entry)
        if kind != "post":
            continue
        if draft and not args.drafts:
            continue

        title = text(entry, ATOM + "title") or "Untitled"
        content_el = entry.find(ATOM + "content")
        body = (content_el.text or "") if content_el is not None else ""
        if not body.strip():
            continue
        dt = parse_date(text(entry, ATOM + "published") or text(entry, ATOM + "updated"))
        path = post_path(entry)
        slug = slug_from_path(path) or fallback_slug(title, dt)
        m = re.search(r"(/\d{4}/\d{2}/[^/?#]+\.html?)$", path)
        blogger_path = m.group(1) if m else None
        labels = labels_of(entry)

        dest = OUT / f"{dt:%Y-%m-%d}-{slug}.html"
        if dest.exists() and not args.force:
            skipped += 1
            continue

        front = ["---", f"title: {yaml_str(title)}", f"date: {dt.isoformat()}", f"slug: {yaml_str(slug)}"]
        if blogger_path:
            front.append(f"bloggerPath: {yaml_str(blogger_path)}")
        front.append("labels:" + ("" if labels else " []"))
        front += [f"  - {yaml_str(l)}" for l in labels]
        if draft:
            front.append("draft: true")
        front.append("---")
        dest.write_text("\n".join(front) + "\n" + relink(body.strip(), host) + "\n", encoding="utf-8")
        made += 1
        print(f"  + {dest.relative_to(ROOT)}")

    print(f"Imported {made} post(s)" + (f", skipped {skipped} existing (use --force to overwrite)" if skipped else "") + ".")


if __name__ == "__main__":
    main()
