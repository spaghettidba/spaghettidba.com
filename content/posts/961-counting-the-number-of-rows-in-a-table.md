---
title: "Counting the number of rows in a table"
date: "2015-05-18T18:10:08"
slug: "counting-the-number-of-rows-in-a-table"
source_url: "http://spaghettidba.com/2015/05/18/counting-the-number-of-rows-in-a-table/"
url: "/2015/05/18/counting-the-number-of-rows-in-a-table/"
categories: ["SQL Server", "T-SQL"]
tags: ["SQL", "SQLServer"]
---

Don't be fooled by the title of this post: while counting the number of rows in a table is a trivial task for you, it is not trivial at all for SQL Server.

Every time you run your COUNT(*) query, SQL Server has to scan an index or a heap to calculate that seemingly innocuous number and send it to your application. This means a lot of unnecessary reads and unnecessary blocking.

Jes Schultz Borland <a href="http://www.brentozar.com/archive/2014/02/count-number-rows-table-sql-server/">blogged about it</a> some time ago and also Aaron Bertrand has <a href="http://sqlperformance.com/2014/10/t-sql-queries/bad-habits-count-the-hard-way">a blog post on this subject</a>. I will refrain from repeating here what they both said: go read their blogs to understand why COUNT(*) is a not a good tool for this task.

The alternative to COUNT(*) is reading the count from the table metadata, querying sys.partitions, something along these lines:



```sql
SELECT SUM(p.rows)
FROM sys.partitions p
WHERE p.object_id = OBJECT_ID('MyTable')
    AND p.index_id IN (0,1); -- heap or clustered index
```



Many variations of this query include JOINs to sys.tables, sys.schemas or sys.indexes, which are not strictly necessary in my opinion. However, the shortest version of the count is still quite verbose and error prone.

Fortunately, there's a shorter version of this query that relies on the system function <a href="https://msdn.microsoft.com/en-us/library/ms188390.aspx">OBJECTPROPERTYEX</a>:



```sql
SELECT OBJECTPROPERTYEX(OBJECT_ID('MyTable'),'cardinality')
```



Where does it read data from? STATISTICS IO doesn't return anything for this query, so I had to set up an Extended Events session to capture lock_acquired events and find out the system tables read by this function:

<a href="/wp-content/uploads/2015/05/sysalloc.png"><img class="alignnone size-full wp-image-962" src="/wp-content/uploads/2015/05/sysalloc.png" alt="sysalloc" width="604" height="191" /></a>

Basically, it's just sysallocunits and sysrowsets.

It's nice, short and easy to remember. Enjoy.
