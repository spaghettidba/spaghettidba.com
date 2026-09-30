---
title: "SQL Server Infernals - Circle 5: Inconsistent Baptists"
date: "2015-07-17T17:25:08"
slug: "sql-server-infernals-circle-5-inconsistent-baptists"
source_url: "http://spaghettidba.com/2015/07/17/sql-server-infernals-circle-5-inconsistent-baptists/"
url: "/2015/07/17/sql-server-infernals-circle-5-inconsistent-baptists/"
categories: ["SQL Server", "SQL Server Infernals"]
tags: ["Database Design", "Naming Conventions", "Worst Practices"]
---

<img class="alignnone size-full wp-image-976" src="/wp-content/uploads/2015/06/infernals1.png" alt="Infernals" width="604" height="158" />

There’s a place in the SQL Server hell where you can find poor souls wandering the paths of their circle, shouting nonsense table names or system-generated constraint names, trying to baptize everything they find on their way in a different manner. They might seem innocuous at a first glance, but beware those damned souls, as they can raise confusion and endanger performance.
<h2>What they say in Heaven</h2>
Guided by the Intelligent Designer’s hands, database architects in Heaven always name their tables, columns and all database objects following the rules in the <a href="http://metadata-standards.org/11179/">ISO 11179 standard</a>. However, standards aside, the most important thing they do is adhere to a single naming convention, so that every angelic DBA and developer can sing in the same language.

It has to be said that even in Heaven some angels prefer specific naming conventions and some other angels might prefer different ones (say plural or singular table names), but as soon as they start to design a database, every disagreement magically disappears and they all sing in harmony.
<h2>Damnation by namification</h2>
Some naming conventions are better than others, but many times it all comes down to personal preference. It’s a highly debatable subject and I will refrain from posting here what my preference is. If you want to learn more about naming conventions, <a href="http://kejser.org/database-naming-conventions/general-database-conventions/">take advice from one of the masters</a>.

That said, some naming conventions are really bad and adopting them is a one way ticket to the SQL Server hell:

&nbsp;
<ol>
	<li><strong>Hungarian Notation</strong>: my friends in Hungary will forgive me if I say that their notation doesn’t play well with database objects. In fact, the <a href="https://en.wikipedia.org/wiki/Hungarian_notation">Hungarian Notation</a> was conceived in order to overcome the lack of proper data types in the BCPL language, putting a metadata prefix in each variable name. For instance, a variable holding a string would carry the “str” prefix, while a variable holding a long integer would carry the “l” prefix.
SQL Server (and all modern relational databases) have proper data type support and all sorts of metadata discovery features, so there is no point in naming a table “tbl_customer” or a view “vwSales”. Moreover, if the DBA decides to break a table in two and expose its previous structure as a view (in order to prevent breaking existing code), having the “tbl” prefix in the view name completely defeats the purpose of identifying the object type by its prefix.
Next time you’re tempted to use the Hungarian Notation ask yourself: “is my name John or DBA_John?”



<figure id="attachment_1019" class="wp-caption alignnone" style="width: 604px; max-width: 100%;">
<img class="wp-image-1019 size-full" src="/wp-content/uploads/2015/07/hungary.png" alt="Hungary" width="604" height="379" />
<figcaption class="wp-caption-text">Hungary is a nice str_country.</figcaption>
</figure>

</li>
	<li><strong>Using insanely short object names: </strong>Some legacy databases (yes, you, DB2/400) used to have a <a href="http://www.ibm.com/developerworks/data/library/techarticle/milligan/0108milligan.html">hard maximum of 10 characters for object names</a>. It wasn’t uncommon to see table names such as “VN30SKF0OF” or “PRB10SPE4F”: good luck figuring out what those tables represented!
Fortunately, those days are gone and today there is no single reason to use alphabet soup names for your objects. The object name is a contract between the object and its contents and it should be immediately clear what the contents are by just glancing at the name.</li>
</ol>
<ol start="3">
	<li><strong>Using insanely long object names: </strong>On the other hand, table names such as “ThisIsTheViewThatContainsOrdersWhichAreYetToBeShipped” adds nothing to clarity of the schema. “UnshippedOrders” will do just as well.</li>
</ol>
<ol start="4">
	<li><strong>Mixing Languages: </strong>if you’re fortunate enough to be a native English speaker, you have no idea what this means. In countries such as Italy or Spain, this is a real issue. Many people may end up designing different parts the database schema and each designer may be inclined to use English (the <em><a href="https://en.wikipedia.org/wiki/Lingua_franca">lingua franca</a></em> of Information Technology) or his/her first language. Needless to say that the result is a mess.</li>
</ol>
<ol start="5">
	<li><strong>Using the “sp_” prefix for stored procedures: </strong>it’s a special case of Hungarian Notation, with severe performance implications. In his blog, <a href="https://twitter.com/AaronBertrand">Aaron Bertrand</a> discussed the notorious negative impact of the “sp_” prefix, offering a <a href="http://sqlperformance.com/2012/10/t-sql-queries/sp_prefix">performance comparison with charts and crunchy numbers</a>.
TL;DR version: SQL Server looks up objects with the sp_ prefix in the master database first, then in the user database. While it may look like a negligible performance issue, it can explode at scale.</li>
</ol>
<ol start="6">
	<li><strong>Using reserved keywords or illegal characters: </strong>While it’s still possible to <a href="https://www.simple-talk.com/sql/t-sql-programming/laying-out-sql-code/">include almost anything inside square brackets</a>, the use of spaces, quotes or any other illegal character is a totally unneeded masochistic habit. Reserved keywords may also add a thrilling touch of insane confusion to your T-SQL code:
<code>SELECT * FROM [TRUNCATE] [TABLE]</code>
Enough said.</li>
</ol>
<ol start="7">
	<li><strong>Using system-generated names for constraints, indexes and so on: </strong>When you don’t name your constraints and indexes explicitly, SQL Server is kind enough as to do it for you, using a semi-random system-generated name. That’s great! Uh, wait a moment: this means that two databases deployed to two different instances will contains the same index with a different name, making all your deployment scripts nearly useless. Do yourself a favor and take the time to name all your objects explicitly.</li>
</ol>
<ol start="8">
	<li><strong>No naming convention or multiple, inconsistent naming conventions: </strong>The worst of all mistakes is having multiple naming conventions, or no naming convention at all (which is equal to “as many naming conventions as objects in the database”). Naming conventions is a sort of religious subject and there are multiple valid reasons to adopt one or another: the only thing you should absolutely avoid is turning your database into a sort of Babel tower, where multiple different languages are spoken and nobody understands what the others say.

<strong> <a href="/wp-content/uploads/2015/07/babel1.png"><img class="alignnone size-full wp-image-1021" src="/wp-content/uploads/2015/07/babel1.png" alt="Babel" width="604" height="465" /></a></strong></li>
</ol>
This is the last circle of SQL Server hell dedicated to Database Design sins: in the next episode of SQL Server Infernals we will venture into the first circle dedicated to development. Stay tuned!

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (8)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-8179" class="archived-comment"><article><header><strong>Corey</strong> <time datetime="2015-07-23T13:00:52Z">July 23, 2015 at 14:00</time></header><section class="archived-comment-content">Looks like repentance is in order.  Excellent post!</section></article></li><li id="wordpress-comment-8180" class="archived-comment"><article><header><strong>lori</strong> <time datetime="2015-07-23T16:04:39Z">July 23, 2015 at 17:04</time></header><section class="archived-comment-content">very fun! Always a timely subject</section></article></li><li id="wordpress-comment-8186" class="archived-comment"><article><header><strong>Jason Hopkins</strong> <time datetime="2015-07-24T01:15:35Z">July 24, 2015 at 02:15</time></header><section class="archived-comment-content">Interesting that you chose "tibbling" as the first sin. I admit I used to go back and forth about this; but have you ever considered the lift in terms of increasing the quality of hits when crawling code? Or in other words, how tibbling reduces spurious hits. I'm convinced that for this reason alone tibbling is the way to go, though I never see anyone bring this point up.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8187" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-07-24T07:47:30Z">July 24, 2015 at 08:47</time></header><section class="archived-comment-content">We have many ways to identify the object type from the metadata that adding more metadata in the object name itself is a waste of time and a source of confusion. In SSMS you can install the SSMSBoost add-in to simply hit F2 and have the object definition scripted in a new query editor window, or right click an object and select "Locate object in Object Explorer". No, really: we don't need metadata in the object name.</section></article></li></ol></li><li id="wordpress-comment-8227" class="archived-comment"><article><header><strong>Janos Berke (@JanosBerke)</strong> <time datetime="2015-07-30T17:01:35Z">July 30, 2015 at 18:01</time></header><section class="archived-comment-content">As a Hungarian, I totally agree with you that Hungarian notation is not for database development :)</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8228" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-07-30T17:03:35Z">July 30, 2015 at 18:03</time></header><section class="archived-comment-content">Ha! I had no doubt about it, Janos! BTW, can you confirm that Hungary is a beautiful str_Country? :-)</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8335" class="archived-comment"><article><header><strong>Janos Berke (@JanosBerke)</strong> <time datetime="2015-08-18T17:09:38Z">August 18, 2015 at 18:09</time></header><section class="archived-comment-content">hahaha, it is :))))</section></article></li></ol></li></ol></li><li id="wordpress-comment-45471" class="archived-comment"><article><header><strong>Fanatico Scriptos</strong> <time datetime="2023-07-06T09:34:03Z">July 6, 2023 at 10:34</time></header><section class="archived-comment-content">Thannks for the post</section></article></li></ol></details>
</div>
