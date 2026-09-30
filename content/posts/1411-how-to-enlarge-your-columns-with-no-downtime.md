---
title: "How To Enlarge Your Columns With No Downtime"
date: "2017-11-15T19:44:45"
slug: "how-to-enlarge-your-columns-with-no-downtime"
source_url: "http://spaghettidba.com/2017/11/15/how-to-enlarge-your-columns-with-no-downtime/"
url: "/2017/11/15/how-to-enlarge-your-columns-with-no-downtime/"
categories: ["SQL Server", "T-SQL"]
tags: ["Row Compression", "SQL", "SQLServer"]
---

Let's face it: column enlargement is a very sensitive topic. I get thousands of emails every month on this particular topic, although most of them end up in my spam folder. Go figure...

The inconvenient truth is that enlarging a fixed size column is a long and painful operation, that will make you wish there was a magic lotion or pill to use on your column to enlarge it on the spot.

<img class=" size-full wp-image-1424 aligncenter" src="/wp-content/uploads/2017/11/lotion.jpg" alt="lotion" width="475" height="475" />

Unfortunately, there is no such magic pill, but turns out you can use some SQL Server features to make the column enlargement less painful for your users.

First, let's create a table with one smallint column, that we will try to enlarge later.



```sql
-- Go to a safe place
USE tempdb;
GO

IF OBJECT_ID('EnlargeTest') IS NOT NULL
    DROP TABLE EnlargeTest;

-- Create test table
CREATE TABLE EnlargeTest (
    SomeColumn smallint
);

-- Insert 1 million rows
INSERT INTO EnlargeTest (SomeColumn)
SELECT TOP(1000000) 1
FROM master.dbo.spt_values AS A
CROSS JOIN master.dbo.spt_values AS B;
```



If you try to enlarge this column with a straight "ALTER TABLE" command, you will have to wait for SQLServer to go through all the rows and write the new data type. Smallint is a data type that is stored in 2 bytes, while int requires 4 bytes, so SQL Server will have to enlarge each and every row to accommodate 2 extra bytes.

This operation requires some time and also causes a lot of page splits, especially if the pages are completely full.



```sql
SET STATISTICS IO, TIME ON;

-- Enlarge column
ALTER TABLE EnlargeTest ALTER COLUMN SomeColumn int;

SET STATISTICS IO, TIME OFF;

/*

(1000000 rows affected)
SQL Server parse and compile time:
   CPU time = 0 ms, elapsed time = 0 ms.
Table 'EnlargeTest'. Scan count 9, logical reads 3001171, physical reads 0, read-ahead reads 0, lob logical reads 0, lob physical reads 0, lob read-ahead reads 0.
Table 'Worktable'. Scan count 8, logical reads 2064041, physical reads 0, read-ahead reads 0, lob logical reads 0, lob physical reads 0, lob read-ahead reads 0.

 SQL Server Execution Times:
   CPU time = 13094 ms,  elapsed time = 11012 ms.

 */
```



The worst part of this approach is that, while the ALTER TABLE statement is running, nobody can access the table.

To overcome this inconvenience, there is a magic column enlargement pill that your table can take, and it's called <strong>Row Compression</strong>.



<figure id="attachment_1425" class="wp-caption aligncenter" style="width: 390px; max-width: 100%;">
<img class="wp-image-1425 size-full" src="/wp-content/uploads/2017/11/pharmapack.jpg" alt="" width="390" height="305" />
<figcaption class="wp-caption-text">Row compression pills. They used to be expensive, SQL Server 2016 SP1 made them cheap.</figcaption>
</figure>



Let's try and revert to the original column size and take the Row Compression pill:



```sql
-- Let's revert to smallint
ALTER TABLE EnlargeTest ALTER COLUMN SomeColumn smallint;

-- Add row compression
ALTER TABLE EnlargeTest REBUILD WITH (DATA_COMPRESSION = ROW);
```



With Row Compression, your fixed size columns can use only the space needed by the smallest data type where the actual data fits. This means that for an int column that contains only smallint data, the actual space usage inside the row is 1 or 2 bytes, not 4.

This is exactly what you need here:



```sql
SET STATISTICS IO, TIME ON;

-- Let's try to enlarge the column again
ALTER TABLE EnlargeTest ALTER COLUMN SomeColumn int;

SET STATISTICS IO, TIME OFF;

/*

 SQL Server Execution Times:
   CPU time = 0 ms,  elapsed time = 0 ms.

 */
```



Excellent! This time the command completes instantly and the ALTER COLUMN statement is a metadata only change.

The good news is that Row Compression is available in all editions of SQL Server since version 2016 SP1 and compression can be applied by rebuilding indexes ONLINE, with no downtime (yes, you will need Enteprise Edition for this).

The (relatively) bad news is that I tested this method on several versions of SQL Server and it only works on 2016 and above. Previous versions are not smart enough to take the compression options into account when enlarging the columns and they first enlarge and then reduce the columns when executing the ALTER COLUMN command. Another downside to this method is that row compression will refuse to work if the total size of your columns exceeds 8060 bytes, <a href="https://docs.microsoft.com/en-us/sql/relational-databases/data-compression/data-compression">as the documentation states</a>.

Bottom line is: painless column enlargement is possible, if you take the Row Compression pills. Just don't overdo it: you don't want to enlarge your columns too much, do you?
