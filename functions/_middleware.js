const feedTargets = new Map([
  ["feed", "/index.xml"],
  ["rss", "/index.xml"],
  ["rss2", "/index.xml"],
  ["rdf", "/index.xml"],
  ["atom", "/atom.xml"],
]);

const contentFilters = [
  "p", "page_id", "name", "pagename", "cat", "category_name", "tag", "tag_id",
  "author", "author_name", "s", "year", "monthnum", "day", "withcomments",
  "post_type",
];

export function onRequest(context) {
  const url = new URL(context.request.url);
  if (!["/", "/index.php", "/index.php/"].includes(url.pathname)) {
    return context.next();
  }
  if (contentFilters.some((key) => url.searchParams.has(key))) {
    return context.next();
  }
  const target = feedTargets.get(url.searchParams.get("feed"));
  if (!target) {
    return context.next();
  }
  url.pathname = target;
  url.searchParams.delete("feed");
  return Response.redirect(url.href, 301);
}
