# spaghettidba.com

A Hugo archive of the public posts and pages from [spaghettidba.com](https://spaghettidba.com/).

## Theme

The site uses Beautiful Hugo v3.6.0 as a Git submodule, with Hugo 0.167.0 or newer.
Older theme releases reference Hugo APIs and embedded templates that have been
removed. Initialize or update the pinned theme after cloning or pulling with:

```powershell
git submodule update --init --recursive
```

## Comments

Posts use giscus with the `General` GitHub Discussions category in `spaghettidba/spaghettidba.com`. The widget maps discussions by pathname, so the existing post permalinks remain unchanged. Historical WordPress comments are imported as collapsed, read-only threads that retain their original authors, dates, and reply nesting, including on pages where archived comments exist. Pingbacks and trackbacks are excluded.

## Run locally

Use Hugo 0.167.0 or newer with the pinned theme. Generate the monthly archives,
then start the development server:

```powershell
python scripts\generate_archives.py
hugo server
```

Build the static site into `public/` with:

```powershell
python scripts\generate_archives.py
hugo
```

For Cloudflare Pages, set `HUGO_VERSION=0.167.0`, use
`python3 scripts/generate_archives.py && hugo --minify` as the build command, and
`public` as the output directory. Do not retain the old `0.110.0` version pin.

The archive generator uses Hugo's content metadata to create `/YYYY/MM/` pages for
months containing published posts. Each page lists the month's posts, newest first,
without changing article URLs. Generated content under `content/archives/` is not
tracked. Run the generator before each build and again after adding, removing, or
changing post dates while the development server is running. It excludes drafts,
future posts, and expired posts, and removes obsolete generated archives.

Category URLs use `/category/`. On Cloudflare Pages, `static/_redirects` permanently
redirects `/categories/` and its descendants to the matching `/category/` URLs,
including pagination and feeds. These HTTP redirects are not applied by `hugo server`.

The main WordPress feed aliases permanently redirect on Cloudflare Pages:

| WordPress URL (with or without trailing slash) | Destination |
| --- | --- |
| `/feed/`, `/rss/`, `/rss2/`, `/rdf/` | `/index.xml` (RSS 2.0) |
| `/feed/feed/`, `/feed/rss/`, `/feed/rss2/`, `/feed/rdf/` | `/index.xml` |
| `/atom/`, `/feed/atom/` | `/atom.xml` (Atom 1.0) |
| `/wp-feed.php`, `/wp-rss.php`, `/wp-rss2.php`, `/wp-rdf.php` | `/index.xml` |
| `/wp-atom.php` | `/atom.xml` |

Hugo generates both feeds and advertises them in the page head and the visible
RSS/Atom navigation links. Legacy RSS/RDF formats are upgraded to RSS 2.0; Atom
links keep the Atom format. Both main feeds contain the latest 10 published blog
posts, matching the archived WordPress feeds (pages are not included).

`data/wordpress_feed_entries.json` preserves the public posts' WordPress GUIDs
and UTC publication/modification dates. GUIDs are identifiers, not links: historical
`http://` values are intentionally retained even though article links use HTTPS.
Reimporting content refreshes dates but retains previously verified GUIDs. New
non-imported posts use their canonical permalink as the identifier. Feed content
includes the article body, without the archived comment threads.

The Wayback CDX index and archived page subscription links also identified
category, tag, author, and search feeds. These are restored without redirecting
filtered subscriptions to unrelated main-feed content:

| Archived feed | Current destination |
| --- | --- |
| `/category/<term>/feed/` | `/category/<term>/index.xml` |
| `/category/sql-server/<child>/feed/` | `/category/<child>/index.xml` |
| `/tag/<term>/feed/` | `/tags/<term>/index.xml` |
| `/tag/windows-8-1/feed/` | `/tags/windows-8.1/index.xml` |
| `/tag/oracle/feed/` | `/category/oracle/index.xml` (the same two posts) |
| `/author/spaghettidba/feed/` | `/index.xml` (the blog has one author) |
| `/category/failover/feed/` | `/category/failover/index.xml` |
| `/search/extendedtsqlcollector/feed/rss2/` | `/search/extendedtsqlcollector/index.xml` |

Both trailing-slash variants are accepted. The vanished Failover category and
the archived search results use explicit post lists in `content/legacy-feeds/`,
with their Wayback sources recorded in front matter. Those two lists preserve
the recovered historical membership rather than implementing a live search.
The SQL Server category feed includes its historical child categories.

Reference snapshots: [main RSS (2025)](https://web.archive.org/web/20250816121050/https://spaghettidba.com/feed/),
[Atom (2025)](https://web.archive.org/web/20250821022444/https://spaghettidba.com/feed/atom/),
and [category page feed links (2011)](https://web.archive.org/web/20111230065243/http://spaghettidba.com/category/sql-server/).
The audit found 162 feed URLs: all 89 non-comment feeds are covered; the 73
site/post/page comment feeds are intentionally not redirected to article feeds.

`functions/_middleware.js` handles `/?feed=feed|rss|rss2|rdf|atom` and equivalent
queries on `/index.php`, using the same destinations and retaining unrelated query
parameters. This requires Cloudflare Pages Functions (deploy through Git integration
or Wrangler, not a dashboard-only static upload). `static/_routes.json` limits
Function invocations to `/` and `/index.php` (with or without its trailing slash);
homepage requests therefore count as Function invocations, while other paths remain
static. Hugo's local server does not run this middleware.

Query-string requests for filtered feeds remain out of scope; the recovered
filtered feeds use the paths listed above. Comment feeds are not regenerated.
URLs on the old `wordpress.com` hostname must still be managed at WordPress.com.

## Import source content

The archive contains published WordPress posts and pages, with referenced WordPress uploads stored locally under `static/wp-content/uploads/`. The source WXR export is intentionally not tracked; it may contain unpublished drafts or private posts.

The supplied WXR export contains 121 published posts, 3 published pages, and 327 media attachments. The Speaking page is omitted; the About page is maintained locally and preserved during imports.

```powershell
python scripts\import_wordpress.py path\to\wordpress-export.xml
```

The importer also accepts a ZIP containing a single WXR XML file. It imports published content only, preserves original post paths, publication dates, categories, tags, and HTML formatting, converts WordPress `[sourcecode]` and `[code]` blocks to fenced code blocks, `[caption]` shortcodes to HTML figures with captions, and `[gist]` and `[youtube]` embeds to their HTML embeds. It downloads referenced WordPress uploads; ordinary external links remain unchanged.
