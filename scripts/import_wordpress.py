#!/usr/bin/env python3
"""Import published posts and pages from a WordPress eXtended RSS export."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from html import escape, unescape
from pathlib import Path
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
STATIC_DIR = ROOT / "static"
USER_AGENT = "spaghettidba-hugo-archive/1.0 (public blog migration)"
URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+|(?<!:)//[^\s\"'<>]+")
SAFE_SLUG = re.compile(r"[^a-zA-Z0-9_-]+")
SOURCECODE_PATTERN = re.compile(
    r"\[sourcecode\b([^\]]*)\](.*?)\[/sourcecode\s*\]",
    re.IGNORECASE | re.DOTALL,
)
CODE_PATTERN = re.compile(
    r"\[code\b([^\]]*)\](.*?)\[/code\s*\]",
    re.IGNORECASE | re.DOTALL,
)
CAPTION_PATTERN = re.compile(
    r"\[caption\b([^\]]*)\](.*?)\[/caption\s*\]",
    re.IGNORECASE | re.DOTALL,
)
GIST_PATTERN = re.compile(r"\[gist\]\s*([a-f0-9]{5,64})\s*\[/gist\s*\]", re.IGNORECASE)
YOUTUBE_PATTERN = re.compile(r"\[youtube\s*=\s*([^\]]+)\]", re.IGNORECASE)
LANGUAGE_PATTERN = re.compile(r"""language\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s]+))""", re.IGNORECASE)
ATTRIBUTE_PATTERN = re.compile(
    r"""([a-zA-Z_][\w-]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s]+))"""
)
NAMESPACES = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}
EXCLUDED_PAGE_PATHS = {"/speaking/"}
CURATED_PAGE_PATHS = {"/about/"}


def parse_export(path):
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            xml_files = [name for name in archive.namelist() if name.lower().endswith(".xml")]
            if len(xml_files) != 1:
                raise ValueError(f"Expected one WXR XML file in {path}, found {len(xml_files)}")
            data = archive.read(xml_files[0]).decode("utf-8-sig", errors="replace")
    else:
        data = path.read_text(encoding="utf-8-sig", errors="replace")
    data = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", data)
    root = ET.fromstring(data)
    channel = root.find("channel")
    if channel is None:
        raise ValueError(f"No RSS channel found in WordPress export: {path}")

    posts, pages, media = [], [], []
    for item in channel.findall("item"):
        post_type = item.findtext("wp:post_type", default="post", namespaces=NAMESPACES)
        status = item.findtext("wp:status", default="", namespaces=NAMESPACES)
        if post_type == "attachment":
            attachment_url = item.findtext("wp:attachment_url", default="", namespaces=NAMESPACES)
            if attachment_url:
                media.append(attachment_url)
            continue
        if status != "publish" or post_type not in {"post", "page"}:
            continue
        if post_type == "page":
            page_path = urlsplit(item.findtext("link", default="")).path.rstrip("/") + "/"
            if page_path in EXCLUDED_PAGE_PATHS:
                continue
        terms = {"category": [], "post_tag": []}
        for term in item.findall("category"):
            domain = term.get("domain")
            if domain in terms and term.text:
                terms[domain].append(term.text)
        record = {
            "id": item.findtext("wp:post_id", default="", namespaces=NAMESPACES),
            "title": item.findtext("title", default=""),
            "link": item.findtext("link", default=""),
            "slug": item.findtext("wp:post_name", default="", namespaces=NAMESPACES),
            "date_gmt": item.findtext("wp:post_date_gmt", default="", namespaces=NAMESPACES),
            "date": item.findtext("wp:post_date", default="", namespaces=NAMESPACES),
            "content": item.findtext("content:encoded", default="", namespaces=NAMESPACES),
            "excerpt": item.findtext("excerpt:encoded", default="", namespaces=NAMESPACES),
            "categories": sorted(set(terms["category"])),
            "tags": sorted(set(terms["post_tag"])),
        }
        (posts if post_type == "post" else pages).append(record)
    if not posts:
        raise ValueError(f"No published posts found in WordPress export: {path}")
    return posts, pages, media


def source_url(item):
    return item["link"]


def source_path(item):
    path = urlsplit(source_url(item)).path
    return path if path.endswith("/") else path + "/"


def slug_filename(item):
    slug = SAFE_SLUG.sub("-", item.get("slug") or str(item["id"])).strip("-") or str(item["id"])
    return f"{item['id']}-{slug}.md"


def is_upload_url(url):
    parsed = urlsplit(url if not url.startswith("//") else f"https:{url}")
    host = (parsed.hostname or "").lower()
    if host not in {"spaghettidba.com", "www.spaghettidba.com", "spaghettidba.wordpress.com"}:
        return None
    marker = "/wp-content/uploads/"
    if not parsed.path.startswith(marker):
        return None
    return parsed


def local_upload_path(url):
    parsed = is_upload_url(url)
    if not parsed:
        return None
    relative = Path("wp-content") / "uploads" / Path(unquote(parsed.path).split("/wp-content/uploads/", 1)[1])
    destination = (STATIC_DIR / relative).resolve()
    if STATIC_DIR.resolve() not in destination.parents:
        raise ValueError(f"Unsafe media path from {url}")
    return "/" + quote(relative.as_posix(), safe="/-._~")


def rewrite_url(match, internal_paths):
    raw = match.group(0)
    trailing = ""
    while raw and raw[-1] in ".,);":
        trailing = raw[-1] + trailing
        raw = raw[:-1]
    candidate = f"https:{raw}" if raw.startswith("//") else raw
    parsed = urlsplit(candidate)
    host = (parsed.hostname or "").lower()
    if host in {"spaghettidba.com", "www.spaghettidba.com", "spaghettidba.wordpress.com"}:
        local_path = internal_paths.get(parsed.path)
        if local_path:
            return local_path + (f"#{parsed.fragment}" if parsed.fragment else "") + trailing
    local_media = local_upload_path(candidate)
    if local_media:
        return local_media + trailing
    return raw + trailing


def content_html(item, internal_paths):
    content = URL_PATTERN.sub(lambda match: rewrite_url(match, internal_paths), item["content"])

    def parse_attributes(raw):
        return {
            match.group(1).lower(): next(
                (value for value in match.groups()[1:] if value is not None), ""
            )
            for match in ATTRIBUTE_PATTERN.finditer(raw)
        }

    def render_caption(match):
        attributes = parse_attributes(match.group(1))
        alignment = attributes.get("align", "")
        classes = ["wp-caption"]
        if alignment in {"alignnone", "aligncenter", "alignleft", "alignright"}:
            classes.append(alignment)
        attachment_id = attributes.get("id", "")
        figure_id = (
            f' id="{attachment_id}"'
            if re.fullmatch(r"[a-zA-Z0-9_-]+", attachment_id)
            else ""
        )
        width = attributes.get("width", "")
        style = f' style="width: {width}px; max-width: 100%;"' if width.isdigit() else ""
        body = match.group(2).strip()
        image_pattern = re.compile(
            r"(<a\b[^>]*>\s*<img\b[^>]*>\s*</a>|<img\b[^>]*>)",
            re.IGNORECASE | re.DOTALL,
        )
        image = image_pattern.search(body)
        if image:
            image_html = image.group(0)
            trailing_caption = (body[:image.start()] + body[image.end():]).strip()
        else:
            image_html = body
            trailing_caption = ""
        caption = escape(unescape(attributes.get("caption", "")), quote=False).strip()
        if trailing_caption:
            caption = f"{caption} {trailing_caption}".strip()
        figcaption = (
            f'<figcaption class="wp-caption-text">{caption}</figcaption>'
            if caption
            else ""
        )
        return (
            f'\n\n<figure{figure_id} class="{" ".join(classes)}"{style}>\n'
            f"{image_html}\n{figcaption}\n</figure>\n\n"
        )

    content = CAPTION_PATTERN.sub(render_caption, content)

    def render_code(match, language_attributes):
        language_match = LANGUAGE_PATTERN.search(match.group(1))
        if not language_match:
            for language_attribute in language_attributes:
                language_match = re.search(
                    rf"""\b{language_attribute}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s]+))""",
                    match.group(1),
                    re.IGNORECASE,
                )
                if language_match:
                    break
        language = next(
            (value for value in language_match.groups() if value), "text"
        ).lower() if language_match else "text"
        code = unescape(match.group(2)).strip("\r\n")
        longest_backticks = max(
            (len(run) for run in re.findall(r"`+", code)),
            default=0,
        )
        fence = "`" * max(3, longest_backticks + 1)
        return f"\n\n{fence}{language}\n{code}\n{fence}\n\n"

    content = SOURCECODE_PATTERN.sub(lambda match: render_code(match, ("language",)), content)
    content = CODE_PATTERN.sub(lambda match: render_code(match, ("language", "lang")), content)

    def render_gist(match):
        gist_id = match.group(1).lower()
        return (
            f'<script src="https://gist.github.com/{gist_id}.js">'
            f"</script>"
        )

    content = GIST_PATTERN.sub(render_gist, content)

    def render_youtube(match):
        video_url = match.group(1).strip()
        parsed = urlsplit(video_url if "://" in video_url else f"https://{video_url}")
        host = (parsed.hostname or "").lower()
        video_id = ""
        if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif host == "youtu.be":
            video_id = parsed.path.strip("/").split("/", 1)[0]
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return match.group(0)
        return (
            '<div class="video-embed">'
            f'<iframe src="https://www.youtube-nocookie.com/embed/{video_id}" '
            'title="YouTube video" loading="lazy" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'allowfullscreen></iframe>'
            "</div>"
        )

    return YOUTUBE_PATTERN.sub(render_youtube, content)


def plain_text(html):
    return unescape(re.sub(r"<[^>]+>", " ", html)).strip()


def write_content(item, section, internal_paths=None):
    internal_paths = internal_paths or {}
    rendered = content_html(item, internal_paths)
    filename = slug_filename(item)
    target_dir = CONTENT_DIR / section
    target_dir.mkdir(parents=True, exist_ok=True)
    date = item.get("date") or item.get("date_gmt")
    if date:
        date = date.replace(" ", "T", 1)
    title = unescape(re.sub(r"<[^>]+>", "", item["title"])).strip()
    path = urlsplit(source_url(item)).path
    metadata = {
        "title": title,
        "date": date,
        "slug": item.get("slug", ""),
        "source_url": source_url(item),
        "url": path if path.endswith("/") else path + "/",
    }
    if section == "posts":
        metadata["categories"] = item["categories"]
        metadata["tags"] = item["tags"]
    excerpt = plain_text(item.get("excerpt", ""))
    if excerpt:
        metadata["description"] = excerpt
    front_matter = ["---"]
    front_matter.extend(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items())
    front_matter.append("---")
    target = target_dir / filename
    target.write_text("\n".join(front_matter) + "\n\n" + rendered.strip() + "\n", encoding="utf-8")
    return rendered


def remove_stale_imports(section, items):
    target_dir = CONTENT_DIR / section
    expected_names = {slug_filename(item) for item in items}
    source_markers = {
        f"source_url: {json.dumps(source_url(item), ensure_ascii=False)}"
        for item in items
    }
    if not target_dir.exists():
        return
    for existing in target_dir.glob("*.md"):
        if existing.name in expected_names:
            continue
        content = existing.read_text(encoding="utf-8")
        if any(marker in content for marker in source_markers):
            existing.unlink()


def fetch_media(url):
    parsed = is_upload_url(url)
    if not parsed:
        return None
    local_path = local_upload_path(url)
    relative_path = unquote(local_path.lstrip("/"))
    destination = STATIC_DIR / Path(relative_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return None
    request = Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=60) as response:
                destination.write_bytes(response.read())
            return None
        except (HTTPError, URLError, TimeoutError) as error:
            if attempt == 2:
                return f"{url}: {error}"
            time.sleep(attempt + 1)
    return None


def main():
    parser = argparse.ArgumentParser(description="Import published WordPress.com content into Hugo.")
    parser.add_argument(
        "export",
        nargs="?",
        type=Path,
        default=ROOT / "spaghettidba.wordpress.com.2026-09-30.000.xml",
        help="WordPress WXR XML file or a ZIP containing one (defaults to the project-root export).",
    )
    args = parser.parse_args()
    posts, pages, media = parse_export(args.export)

    internal_paths = {}
    for item in posts + pages:
        path = urlsplit(source_url(item)).path
        internal_paths[path] = path if path.endswith("/") else path + "/"

    media_urls = {url for url in media if is_upload_url(url)}
    preserved_pages = 0
    for section, items in (("posts", posts), ("pages", pages)):
        remove_stale_imports(section, items)
        for item in items:
            if section == "pages" and source_path(item) in CURATED_PAGE_PATHS:
                preserved_pages += 1
                continue
            rendered = write_content(item, section, internal_paths)
            media_urls.update(
                match.group(0).rstrip(".,);")
                for match in URL_PATTERN.finditer(rendered)
                if is_upload_url(match.group(0).rstrip(".,);"))
            )

    errors = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_media, url) for url in sorted(media_urls)]
        for future in as_completed(futures):
            error = future.result()
            if error:
                errors.append(error)

    print(f"Imported {len(posts)} published posts and {len(pages) - preserved_pages} source pages.")
    if preserved_pages:
        print(f"Preserved {preserved_pages} locally curated page(s).")
    print(f"Downloaded {len(media_urls) - len(errors)} of {len(media_urls)} referenced media files.")
    if errors:
        for error in errors:
            print(f"Media download failed: {error}")
        raise SystemExit(f"Import incomplete: {len(errors)} media files could not be downloaded.")


if __name__ == "__main__":
    main()
