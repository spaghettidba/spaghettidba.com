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
