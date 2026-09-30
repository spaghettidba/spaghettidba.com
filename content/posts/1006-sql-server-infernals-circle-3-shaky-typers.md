---
title: "SQL Server Infernals - Circle 3: Shaky Typers"
date: "2015-07-02T09:53:29"
slug: "sql-server-infernals-circle-3-shaky-typers"
source_url: "http://spaghettidba.com/2015/07/02/sql-server-infernals-circle-3-shaky-typers/"
url: "/2015/07/02/sql-server-infernals-circle-3-shaky-typers/"
categories: ["SQL Server", "SQL Server Infernals"]
tags: ["Data-Types", "Database Design", "Worst Practices"]
---

<img class="alignnone size-full wp-image-976" src="/wp-content/uploads/2015/06/infernals1.png" alt="Infernals" width="604" height="158" />

Choosing the right data type for your columns is first of all a design decision that has tremendous impact on the correctness of the database schema. It is not just about performance or space usage: the data type is the first constraint on your data and it decides what can be persisted in your columns and what is not acceptable.

Choosing the wrong data type for your columns is a mistake that might make your life as a DBA look like hell.
<h2>What they say in Heaven</h2>
Guided by angelic spells, the hands that design databases in Heaven always choose the right data type. Database architects always look at the logical schema and ask the right questions about each attribute and they always manage to understand what the attribute is used for and what it will be used for in the future.
<h2>What will put you to hell</h2>
Choosing the wrong data type is like trying to fit a square peg in a round hole. The worst thing about it is that you end up damaging the peg… ahem… the data.

<a href="/wp-content/uploads/2015/07/squarepegroundhole.png"><img class="alignnone size-full wp-image-1008" src="/wp-content/uploads/2015/07/squarepegroundhole.png" alt="SquarePegRoundHole" width="349" height="261" /></a>
<ol>
	<li><strong>Using numeric data types for non-numeric attributes</strong>: Even if a telephone number contains only digits and it’s called telephone <em>number</em>, it is not a number at all. It does not allow mathematical operations and it has no order relation (saying that a telephone number is greater than another one makes no sense). In fact, a telephone number is a code you have to dial to contact a telephone extension. The same can be said for ZIP codes, which only allow numeric digits, but are nothing like a number. Storing this data in a numeric column is looking for trouble.</li>
</ol>
<ol start="2">
	<li><strong>Storing data as their human-readable representation</strong>: A Notable example is dates stored as (var)char. The string representation of a date is not a date at all: without the validation rules included in the date types, any invalid date could be saved in your column, including ‘2015-02-30’ or ‘2015-33-99’. Moreover, varchar columns do not allow date manipulation functions, such as DATEADD, DATEDIFF, YEAR, MONTH and so on. Another reason why this is a terrible idea is that dates have their own sorting rules, which you lose when you store them as strings. You also need more storage space to save a string representation of a date compared to the proper date type. If you really want to convert a date to a string, you can find many algorithms and functions to perform the conversion in <a href="http://www.sqlservercentral.com/articles/T-SQL/88152/">this article I wrote for SQLServerCentral in 2012</a>, but please do it in your presentation layer, not when storing the data in your tables.
Another surprisingly common mistake in the AS/400 world is storing dates in three separate integer columns for year, month and day. I have no idea where this pattern comes from, but it definitely belongs to hell.
While much more uncommon in the wild, the same applies to numbers: storing them as varchars is a terrible idea.
<strong>Extra evil bonus:</strong> you get double evil points for storing dates and numbers as nvarchar: double the storage, double the pain.</li>
</ol>
<ol start="3">
	<li><strong>Using deprecated data types</strong>: (n)text and image are things of the past: get over it. The replacement (n)varchar(max) and varbinary(max) are much more powerful and flexible.</li>
</ol>
<ol start="4">
	<li><strong>Using “extended” data type just to “be safe”: </strong>This applies both to numeric and character columns: using a bigger data type just to play it safe can be a good idea at times, but not when the size of the column is well known upfront and is instead a vital constraint on the data itself. For instance, a ZIP code longer than 5 characters is obviously an error. A social security number longer than 9 digits is not valid.
Along the same lines, storing years in a int column is only going to be a waste of storage space. The same can be said about small lookup tables with just a handful of rows in them, where the key column can be a smallint or even a tinyint: it won’t save much space in the lookup table itself, but it can save lots of space in the main tables (with many more rows) where the code is referenced.</li>
</ol>
<ol start="5">
	<li><strong>Storing fixed-size information in varchar columns: </strong>Similarly to the previous sin, when your attribute has a fixed character size, there is no point in using a varying character type. If your attribute has <strong>exactly</strong> 3 characters, why use varchar(3)?
<strong>Extra evil bonus: </strong>varchar(1) will get you double points.</li>
</ol>
<ol start="6">
	<li><strong>Storing duration in time or datetime columns:</strong> Datetime and time represent points in time and they are not meant for storing durations. If you really want to store a duration, use a numeric column to store the number of seconds (it’s the ANSI standard unit measure for representing a duration). Even better, you could store the start/end date and time in two separate datetime columns. SQL Server 2016 also supports <a href="https://msdn.microsoft.com/en-us/library/dn935015.aspx">periods</a>.<strong> </strong></li>
</ol>
<ol start="7">
	<li><strong>Getting Unicode wrong:</strong> Choosing nvarchar for attributes that will never contain Unicode data and choosing varchar for attributes that can contain Unicode data are equally evil and will get you instant damnation. For instance, a ZIP code will only contain numeric characters, so using Unicode data types will have the only outcome of wasting space. At the same time, storing customer business names or annotations in varchar columns means that you won’t be able to persist international characters. While it may appear quite unlikely that such characters will ever appear in your database, you will regret your decision when that happens (and it will).<strong> </strong></li>
</ol>
<ol start="8">
	<li><strong>Messing with XML: </strong>I’m not a big fan of XML in the database, but sometimes it can come handy. Storing XML data in a plain varchar column is a very bad idea. The XML data type provides validation rules that won’t allow in invalid or malformed XML and also provides functions to manipulate the XML data. Storing schema-less XML is another bad idea: if you have an XML schema use it, otherwise you will end up saving invalid data. On the other hand, using XML to go “beyond relational” and mimic Oracle’s nested tables will only get you damned. Fun times.<strong> </strong></li>
</ol>
<ol start="9">
	<li><strong>Using different data types in different tables for the same attribute:</strong> there’s only one thing worse than getting your data types wrong: getting them wrong in multiple places. Once you decided the data type to store an attribute, don’t change your mind when designing new tables. If it is a varchar(10), don’t use varchar(15) in your next table. Usually proper foreign key constraints help you avoid this issue, but it’s not always the case.
If this query returns rows, chances are that you have schizophrenic columns in your database schema:



```sql
WITH my_schema AS (
    SELECT OBJECT_NAME(c.object_id) AS table_name,
        c.name AS column_name,
        t.name AS type_name,
        c.max_length,
        c.precision,
        c.scale
    FROM sys.columns AS c
    INNER JOIN sys.types AS t
        ON c.system_type_id = t.system_type_id
),
incarnations AS (
    SELECT *,
        DENSE_RANK() OVER (
            PARTITION BY column_name
            ORDER BY type_name, max_length, precision, scale
        ) AS incarnation_number
    FROM my_schema
),
incarnation_count AS (
    SELECT *,
        MAX(incarnation_number) OVER (
            PARTITION BY column_name
        ) AS incarnation_count
    FROM incarnations
)
SELECT *
FROM incarnation_count
WHERE incarnation_count > 1
ORDER BY incarnation_count DESC,
    column_name,
    type_name,
    max_length,
    precision,
    scale;
```



</li>
</ol>
The lack of proper constraints will be the topic of the next post, when we will meet the anarchic designers. Stay tuned!

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (13)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-8056" class="archived-comment"><article><header><strong>suxstellino (Alessandro Alpi)</strong> <time datetime="2015-07-02T11:51:18Z">July 2, 2015 at 12:51</time></header><section class="archived-comment-content">Reblogged this on <a href="https://suxstellino.wordpress.com/2015/07/02/sql-server-infernals-circle-3-shaky-typers/" rel="nofollow ugc noopener noreferrer">Alessandro Alpi's Blog</a>.</section></article></li><li id="wordpress-comment-8058" class="archived-comment"><article><header><strong>regbac</strong> <time datetime="2015-07-03T05:23:05Z">July 3, 2015 at 06:23</time></header><section class="archived-comment-content">Reblogged this on <a href="https://theblobfarm.wordpress.com/2015/07/03/sql-server-infernals-circle-3-shaky-typers/" rel="nofollow ugc noopener noreferrer">The Blobfarm</a> and commented: <br>Gianluca's post is spot-on if you are looking for advice when picking data types for your database design !!</section></article></li><li id="wordpress-comment-8092" class="archived-comment"><article><header><strong>Henn Sarv</strong> <time datetime="2015-07-10T10:32:17Z">July 10, 2015 at 11:32</time></header><section class="archived-comment-content">One strange datatype is nullable bit. I've not checked actual implementation but it looks like implemented in variable block (cost 3 bytes) + one bit in nullability mask.<br><br>Rather to use 2 bits - one about data and other about knowledge about data<br><br>crate table x<br>(<br>...<br>, gender bit null -- 0 = F, 1 = M and NULL = Unknown<br>...<br>)<br><br>rather to include<br>(<br>...<br>, gender bit not null -- 0 = F, 1 = M<br>, gender_known bit not null -- 0 = Unknown, 1 = known<br>...<br>)<br><br>in view (or query)<br><br>, case when gender_known=1 then gender end as gender   -- this is enough to add <br><br>Henn</section></article></li><li id="wordpress-comment-8093" class="archived-comment"><article><header><strong>dman2306</strong> <time datetime="2015-07-10T12:43:34Z">July 10, 2015 at 13:43</time></header><section class="archived-comment-content">I think it's short sighted to assume zipcodes are always 5 characters. What about zip+4 in the US? What about other countries? Sometimes, even when you believe a field is "exactly" a number of characters, it's still good to pad because, as you said, we don't always understand the logical data and its future uses. In your case, where you set zip code to char(5), zip+4 fails. In my case where I always use varchar(10), I'm good to go. This is why some of us add padding. If I had built my app in the 1980s when zipcodes were only 5 digits, and I set that as my length, when zip+4 came out, I would have had potentially many data layer changes. By adding padding, I just have application layer changes.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8095" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-07-10T13:46:37Z">July 10, 2015 at 14:46</time></header><section class="archived-comment-content">Thanks for your comment: it's spot on and I learnt that ZIP codes are longer than 5 digits in the US :)<br>Maybe ZIP codes are a poor example, but until the time they changed from 5 to 9 characters, the length was a constraint on the data itself: using varchar 10 from the start would have saved you the hassle of enlarging the column later (not a big deal in my opinion), but it would have let in invalid data. <br>My point is that future uses of the data should not have precedence over current uses of the data, especially when the shape of the data is a constraint for its validity.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8115" class="archived-comment"><article><header><strong>Bodhi Densmore</strong> <time datetime="2015-07-13T03:17:40Z">July 13, 2015 at 04:17</time></header><section class="archived-comment-content">Flexibility is better than raw efficiency.   The postal code constraint normally includes the state or province column.   It is a big pain to change a data type from char(9) to varchar(10), especially when foreign key constraints are involved.   Better to start with varchar(16) and a constraint that limits the data as needed.  Constraints can be changed in an instant but data type changes for length can take hours.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8117" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-07-13T07:53:45Z">July 13, 2015 at 08:53</time></header><section class="archived-comment-content">I'm sorry, but I disagree. Enlarging a column might be painful, but when the length is a constraint on the data, the length must be set exactly, without leaving room for eventual future changes. My bad for choosing ZIP code as an example, but think of SSN if it helps getting the point across better.</section></article></li></ol></li></ol></li></ol></li><li id="wordpress-comment-8099" class="archived-comment"><article><header><strong>Brian Feifarek</strong> <time datetime="2015-07-10T17:09:36Z">July 10, 2015 at 18:09</time></header><section class="archived-comment-content">Gianluca,  Thank you for a great summary of type issues that will cause headaches later.  One minor point on #6 is that the period link refers to SQL Server creating history tables, not a new datatype-- the period it uses is two datetime2 columns that SQL Server manages automatically, so it does not add any more than the sentence before it for this use case.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8100" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-07-10T17:58:26Z">July 10, 2015 at 18:58</time></header><section class="archived-comment-content">Thank you Brian. I agree that the implementation is not complete yet, but you can still mark two columns as period. All the features that could be useful in other contexts are available only to temporal tables though. Thanks for pointing it out</section></article></li></ol></li><li id="wordpress-comment-8102" class="archived-comment"><article><header><strong>Joe Celko</strong> <time datetime="2015-07-11T02:02:59Z">July 11, 2015 at 03:02</time></header><section class="archived-comment-content">Henn Sarv: <br>You should be using the ISO standard sex code  0 = unknown, 1 = male, 2 = female, 9 = lawful person (corporations, institutions, etc). <br><br>The NULL-able BIT was the result of changing this proprietary data type to a NUMERIC. In SQL, all data types are NULL-able by definition. Originally, the BIT was what us computer geeks think of as a bit = {0,1} and was automatically non-NULL-able. So we never bothered with the explicit NOT NULL constraint. The switch screwed up code even worse than replacing the original Sybase *= outer joins. You got no error messages!<br><br>Dman2306: <br>I strongly disagree with padding. When you declared the original column, did you use this DDL? <br><br> zip_code CHAR(5) NOT NULL<br>    CHECK (zip_code LIKE '[0-9][0-9][0-9][0-9][0-9]')<br><br>most of us did not do this, much less disallow impossible ZIP codes. My favorite was '99999' which routed lots of junk mail to an Eskimo village in Alaska. The old COBOL convention had been to fill unknown values with 9's (see my remarks on ISO sex codes above), so bulk mailers inherited that kind of data. Arrgh! But it gave the Eskimos winter fuel to burn. <br><br>By allowing garbage data, you put an undue burden on the applications. When we did get ZIP+4, we needed an ALTER TABLE with a <br><br>CHECK (zip_code LIKE '[0-9][0-9][0-9][0-9][0-9][ 0-9][ 0-9][ 0-9][ 0-9]') <br><br>so we could trim the trailing blanks if the application needed only the original ZIP. The +4 changes more than people think, so lots of sites do not use it unless they do bulk mailings. I still get ZIP+4 rejected in on-line forms.</section></article></li><li id="wordpress-comment-8119" class="archived-comment"><article><header><strong>Tim</strong> <time datetime="2015-07-13T14:36:04Z">July 13, 2015 at 15:36</time></header><section class="archived-comment-content">I'm not sure SSNs are any better than zip codes: there are already &gt;300 million people in the US so no capacity for a check digit. And pretty soon there will have to be a format change to prevent reuse of existing numbers</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8120" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-07-13T14:46:50Z">July 13, 2015 at 15:46</time></header><section class="archived-comment-content">Well, it looks like I'm not well informed about the situation in the US. I hope the point is clear anyway.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8121" class="archived-comment"><article><header><strong>Joe Celko</strong> <time datetime="2015-07-13T16:49:14Z">July 13, 2015 at 17:49</time></header><section class="archived-comment-content">Actually SSN is awful. There is no check digit and we have so many illegals there is a 3-5% forgery rate. Now, to make it worse, the old pattern for allocation is void and the numbers are random!</section></article></li></ol></li></ol></li></ol></details>
</div>
