#!/usr/bin/env python3
"""Import published posts and pages from a WordPress eXtended RSS export."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from html import escape, unescape
from html.parser import HTMLParser
from datetime import datetime
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
ALLOWED_COMMENT_TAGS = {
    "a", "b", "blockquote", "br", "code", "del", "em", "i", "li",
    "ol", "p", "pre", "s", "span", "strong", "sub", "sup", "u", "ul",
}
VOID_COMMENT_TAGS = {"br"}
BLOCKED_COMMENT_TAGS = {"iframe", "object", "script", "style", "svg"}
ARCHIVED_COMMENTS_START = "<!-- archived WordPress comments: start -->"
ARCHIVED_COMMENTS_END = "<!-- archived WordPress comments: end -->"


class CommentHTMLSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self.open_tags = []
        self.blocked_tags = []

    def handle_starttag(self, tag, attrs):
        if self.blocked_tags:
            if tag in BLOCKED_COMMENT_TAGS:
                self.blocked_tags.append(tag)
            return
        if tag in BLOCKED_COMMENT_TAGS:
            self.blocked_tags.append(tag)
            return
        if tag not in ALLOWED_COMMENT_TAGS:
            return

        if tag == "a":
            href = dict(attrs).get("href", "").strip()
            parsed = urlsplit(href)
            safe_href = (
                parsed.scheme.lower() in {"http", "https", "mailto"}
                or (not parsed.scheme and not href.startswith(("//", "\\\\")))
            )
            if href and safe_href:
                self.output.append(
                    f'<a href="{escape(href, quote=True)}" '
                    'rel="nofollow ugc noopener noreferrer">'
                )
            else:
                self.output.append("<a>")
        else:
            self.output.append(f"<{tag}>")

        if tag not in VOID_COMMENT_TAGS:
            self.open_tags.append(tag)

    def handle_endtag(self, tag):
        if self.blocked_tags:
            if tag == self.blocked_tags[-1]:
                self.blocked_tags.pop()
            return
        if tag not in self.open_tags:
            return
        while self.open_tags:
            open_tag = self.open_tags.pop()
            self.output.append(f"</{open_tag}>")
            if open_tag == tag:
                break

    def handle_data(self, data):
        if not self.blocked_tags:
            escaped = escape(data, quote=False)
            escaped = escaped.replace("\r\n", "\n").replace("\r", "\n")
            self.output.append(escaped.replace("\n", "<br>"))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_COMMENT_TAGS:
            self.handle_endtag(tag)

    def render(self, source):
        self.feed(source)
        self.close()
        while self.open_tags:
            self.output.append(f"</{self.open_tags.pop()}>")
        return "".join(self.output).strip()


def parse_comments(item):
    comments = []
    for comment in item.findall("wp:comment", NAMESPACES):
        comment_type = comment.findtext("wp:comment_type", default="", namespaces=NAMESPACES)
        approved = comment.findtext("wp:comment_approved", default="", namespaces=NAMESPACES)
        if approved != "1" or comment_type not in {"", "comment"}:
            continue
        comments.append({
            "id": comment.findtext("wp:comment_id", default="", namespaces=NAMESPACES),
            "parent_id": comment.findtext("wp:comment_parent", default="0", namespaces=NAMESPACES),
            "author": comment.findtext("wp:comment_author", default="", namespaces=NAMESPACES),
            "date": comment.findtext("wp:comment_date", default="", namespaces=NAMESPACES),
            "date_gmt": comment.findtext("wp:comment_date_gmt", default="", namespaces=NAMESPACES),
            "content": comment.findtext("wp:comment_content", default="", namespaces=NAMESPACES),
        })
    return comments


def comment_date_markup(comment):
    local_date = comment["date"]
    try:
        local_datetime = datetime.strptime(local_date, "%Y-%m-%d %H:%M:%S")
        display_date = (
            f"{local_datetime.strftime('%B')} {local_datetime.day}, "
            f"{local_datetime.year} at {local_datetime.strftime('%H:%M')}"
        )
        machine_date = local_datetime.isoformat()
    except ValueError:
        display_date = local_date
        machine_date = local_date

    gmt_date = comment["date_gmt"]
    if gmt_date and not gmt_date.startswith("0000-00-00"):
        try:
            machine_date = datetime.strptime(
                gmt_date, "%Y-%m-%d %H:%M:%S"
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            pass
    return (
        f'<time datetime="{escape(machine_date, quote=True)}">'
        f"{escape(display_date, quote=False)}</time>"
    )


def render_archived_comment(comment, children, internal_paths):
    comment_id = comment["id"] or "unknown"
    anchor = f"wordpress-comment-{comment_id}"
    body = URL_PATTERN.sub(
        lambda match: rewrite_url(match, internal_paths),
        comment["content"],
    )
    content = CommentHTMLSanitizer().render(body)
    author = escape(comment["author"] or "Anonymous", quote=False)
    rendered = (
        f'<li id="{escape(anchor, quote=True)}" class="archived-comment">'
        '<article>'
        f'<header><strong>{author}</strong> {comment_date_markup(comment)}</header>'
        f'<section class="archived-comment-content">{content}</section>'
        "</article>"
    )
    if children[comment_id]:
        rendered += '<ol class="archived-comment-replies">'
        rendered += "".join(
            render_archived_comment(child, children, internal_paths)
            for child in children[comment_id]
        )
        rendered += "</ol>"
    return rendered + "</li>"


def archived_comments_html(comments, internal_paths):
    by_id = {comment["id"]: comment for comment in comments if comment["id"]}
    children = {comment_id: [] for comment_id in by_id}
    roots = []

    for comment in comments:
        comment_id = comment["id"]
        parent_id = comment["parent_id"]
        current_parent = parent_id
        seen = {comment_id}
        has_parent_cycle = False
        while current_parent in by_id:
            if current_parent in seen:
                has_parent_cycle = True
                break
            seen.add(current_parent)
            current_parent = by_id[current_parent]["parent_id"]

        if parent_id in by_id and parent_id != comment_id and not has_parent_cycle:
            children[parent_id].append(comment)
        else:
            roots.append(comment)

    sort_key = lambda comment: (comment["date"], int(comment["id"] or 0))
    roots.sort(key=sort_key)
    for replies in children.values():
        replies.sort(key=sort_key)

    rendered_roots = "".join(
        render_archived_comment(comment, children, internal_paths)
        for comment in roots
    )
    count = len(comments)
    return (
        '\n\n<div class="archived-comments-container">\n'
        '<details class="archived-comments">'
        f"<summary>Archived WordPress comments ({count})</summary>"
        '<p class="archived-comments-note">'
        "Historical comments from the original site; this archive is read-only."
        "</p>"
        f'<ol class="archived-comments-list">{rendered_roots}</ol>'
        "</details>\n</div>\n"
    )


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
            "comments": parse_comments(item),
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
    if item["comments"]:
        rendered = rendered.rstrip() + archived_comments_html(
            item["comments"], internal_paths
        )
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


def update_curated_page_comments(item, internal_paths):
    target = CONTENT_DIR / "pages" / slug_filename(item)
    content = target.read_text(encoding="utf-8")
    has_start = ARCHIVED_COMMENTS_START in content
    has_end = ARCHIVED_COMMENTS_END in content
    if has_start != has_end:
        raise ValueError(f"Incomplete archived-comment markers in {target}")
    if has_start:
        start = content.index(ARCHIVED_COMMENTS_START)
        end = content.index(ARCHIVED_COMMENTS_END, start) + len(ARCHIVED_COMMENTS_END)
        content = content[:start] + content[end:]
    if item["comments"]:
        content = (
            content.rstrip()
            + "\n\n"
            + ARCHIVED_COMMENTS_START
            + archived_comments_html(item["comments"], internal_paths)
            + ARCHIVED_COMMENTS_END
            + "\n"
        )
    target.write_text(content, encoding="utf-8")


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
                update_curated_page_comments(item, internal_paths)
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
    archive_items = posts + pages
    archived_comments = sum(len(item["comments"]) for item in archive_items)
    items_with_comments = sum(bool(item["comments"]) for item in archive_items)
    if archived_comments:
        print(
            f"Archived {archived_comments} approved comments "
            f"across {items_with_comments} posts and pages "
            "(pingbacks and trackbacks excluded)."
        )
    if preserved_pages:
        print(f"Preserved {preserved_pages} locally curated page(s).")
    print(f"Downloaded {len(media_urls) - len(errors)} of {len(media_urls)} referenced media files.")
    if errors:
        for error in errors:
            print(f"Media download failed: {error}")
        raise SystemExit(f"Import incomplete: {len(errors)} media files could not be downloaded.")


if __name__ == "__main__":
    main()
