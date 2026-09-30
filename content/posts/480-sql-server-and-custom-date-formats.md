---
title: "SQL Server and Custom Date Formats"
date: "2012-03-23T12:49:47"
slug: "sql-server-and-custom-date-formats"
source_url: "http://spaghettidba.com/2012/03/23/sql-server-and-custom-date-formats/"
url: "/2012/03/23/sql-server-and-custom-date-formats/"
categories: ["SQL Server", "SQL Server Central", "T-SQL"]
tags: ["SQL"]
---

Today <a href="http://www.sqlservercentral.com">SQL Server Central</a> is featuring my article <a href="http://www.sqlservercentral.com/articles/T-SQL/88152/">Dealing with custom date formats in T-SQL</a>.

<a href="http://www.sqlservercentral.com/articles/T-SQL/88152/"><img class="alignnone size-full wp-image-483" title="Headlines" src="/wp-content/uploads/2012/03/headlines.png" alt="" width="444" height="202" /></a>

There's a lot of code on that page and I thought that making it available for download would make it easier to play with.

You can download the code from this page or from the <a href="https://gist.github.com/search?utf8=✓&amp;q=user%3Aspaghettidba+%23blog">Code Repository</a>.
<ul>
	<li><a href="https://gist.github.com/spaghettidba/2e58644556dbb162487306382c1f57b1">CustomDateFormat.cs</a></li>
	<li><a href="https://gist.github.com/spaghettidba/254c03ba4d87e853d6c5c2c30de8aa46">formatDate_Islands_iTVF.sql</a></li>
	<li><a href="https://gist.github.com/spaghettidba/7e1e49cc3f29eb66e71d51e918d5b36f">formatDate_Recursive_iTVF.sql</a></li>
	<li><a href="https://gist.github.com/spaghettidba/d51e41f7c4399e4c6ca7ff58a23ea06c">formatDate_scalarUDF.sql</a></li>
	<li><a href="https://gist.github.com/spaghettidba/726f135b3422f567ba7778e3949df396">parseDate_Islands_iTVF.sql</a></li>
</ul>
<div></div>
<div>I was also asked to include a performance chart for the different methods included in the article. Here's a quick'n'dirty Excel bar chart (I didn't include the recursive iTVF for the sake of readability).</div>
<div> </div>
<div></div>
<div><a href="/wp-content/uploads/2012/03/performance.png"><img class="alignnone size-full wp-image-488" title="Performance" src="/wp-content/uploads/2012/03/performance.png" alt="" width="490" height="298" /></a></div>
I hope you enjoy reading the article as much as I enjoyed writing it.
