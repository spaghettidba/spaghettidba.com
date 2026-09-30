# spaghettidba.com

A Hugo archive of the public posts and pages from [spaghettidba.com](https://spaghettidba.com/).

## Theme

The site uses Beautiful Hugo v3.3.0 as a Git submodule. This release is pinned to work with the Hugo 0.110 version available in the current environment. Initialize the theme after cloning with:

```powershell
git submodule update --init --recursive
```

## Comments

Posts use giscus with the `General` GitHub Discussions category in `spaghettidba/spaghettidba.com`. The widget maps discussions by pathname, so the existing post permalinks remain unchanged. Historical WordPress comments are imported as collapsed, read-only threads that retain their original authors, dates, and reply nesting, including on pages where archived comments exist. Pingbacks and trackbacks are excluded.

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

The supplied WXR export contains 121 published posts, 3 published pages, and 327 media attachments. The Speaking page is omitted; the About page is maintained locally and preserved during imports.

```powershell
python scripts\import_wordpress.py path\to\wordpress-export.xml
```

The importer also accepts a ZIP containing a single WXR XML file. It imports published content only, preserves original post paths, publication dates, categories, tags, and HTML formatting, converts WordPress `[sourcecode]` and `[code]` blocks to fenced code blocks, `[caption]` shortcodes to HTML figures with captions, and `[gist]` and `[youtube]` embeds to their HTML embeds. It downloads referenced WordPress uploads; ordinary external links remain unchanged.
