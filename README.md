# spaghettidba.com

A Hugo archive of the public posts and pages from [spaghettidba.com](https://spaghettidba.com/).

## Run locally

Install Hugo, then start the development server:

```powershell
hugo server
```

Build the static site into `public/` with:

```powershell
hugo
```

## Import source content

The archive contains published WordPress posts and pages, with referenced WordPress uploads stored locally under `static/wp-content/uploads/`. The source WXR export is intentionally not tracked; it may contain unpublished drafts or private posts.

The supplied export includes 121 published posts, 3 published pages, and 327 media attachments.

```powershell
python scripts\import_wordpress.py path\to\wordpress-export.xml
```

The importer also accepts a ZIP containing a single WXR XML file. It imports published content only, preserves original post paths, publication dates, categories, tags, and HTML formatting, converts WordPress `[sourcecode]` and `[code]` blocks to fenced code blocks, `[caption]` shortcodes to HTML figures with captions, and `[gist]` and `[youtube]` embeds to their HTML embeds. It downloads referenced WordPress uploads; ordinary external links remain unchanged.
