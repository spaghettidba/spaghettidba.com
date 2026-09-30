---
title: "Uniquifiers: all rows or the duplicate keys only?"
date: "2014-03-14T18:39:49"
slug: "uniquifiers-all-rows-or-the-duplicate-keys-only"
source_url: "http://spaghettidba.com/2014/03/14/uniquifiers-all-rows-or-the-duplicate-keys-only/"
url: "/2014/03/14/uniquifiers-all-rows-or-the-duplicate-keys-only/"
categories: ["SQL Server"]
tags: ["DBCC", "T-SQL", "internals", "undocumented"]
---

Some days ago I was talking with my friend <a href="https://twitter.com/mauridb">Davide Mauri</a> about the uniquifier that SQL Server adds to clustered indexes when they are not declared as UNIQUE.

We were not completely sure whether this behaviour applied to duplicate keys only or to all keys, even when unique.

The best way to discover the truth is a script to test what happens behind the scenes:



```sql
-- =============================================
-- Author:      Gianluca Sartori - @spaghettidba
-- Create date: 2014-03-15
-- Description: Checks whether the UNIQUIFIER column
--              is added to a column only on
--              duplicate clustering keys or all
--              keys, regardless of uniqueness
-- =============================================

USE tempdb
GO

IF OBJECT_ID('sizeOfMyTable') IS NOT NULL
    DROP VIEW sizeOfMyTable;
GO

-- Create a view to query table size information
-- Not very elegant, but saves a lot of typing

CREATE VIEW sizeOfMyTable
AS
SELECT OBJECT_NAME(si.object_id) AS table_name,
    si.name AS index_name,
    SUM(total_pages) AS total_pages,
    SUM(used_pages) AS used_pages,
    SUM(data_pages) AS data_pages
FROM sys.partitions AS p
INNER JOIN sys.allocation_units AS AU
    ON P.hobt_id = AU.container_id
INNER JOIN sys.indexes AS si
    ON si.index_id = p.index_id
    AND si.object_id = p.object_id
WHERE si.object_id = OBJECT_ID('#testUniquifier')
GROUP BY OBJECT_NAME(si.object_id),
    si.name
GO

IF OBJECT_ID('#testUniquifier') IS NOT NULL
    DROP TABLE #testUniquifier;

-- Create a test table

CREATE TABLE #testUniquifier (
    i int NOT NULL
)

-- Results table: will receive table size
-- in different scenarios

DECLARE @results TABLE(
    description varchar(500),
    table_name sysname,
    index_name sysname,
    total_pages int,
    used_pages int,
    data_pages int
);

-- INSERTS 100K UNIQUE VALUES

INSERT INTO #testUniquifier
SELECT TOP(100000) ROW_NUMBER() OVER(ORDER BY (SELECT NULL))
FROM sys.all_columns AS AC
CROSS JOIN sys.all_columns AS AC1;

-- -----------------------------------------------------------------
-- TEST1: CREATES A UNIQUE CLUSTERED INDEX (NO UNIQUIFIER)
-- -----------------------------------------------------------------

CREATE UNIQUE CLUSTERED INDEX UK_test ON #testUniquifier(i);

INSERT @results
SELECT 'Unique clustered index' AS description, * FROM sizeOfMyTable;

DROP INDEX UK_test ON #testUniquifier

-- -----------------------------------------------------------------
-- TEST2: CREATES A NON-UNIQUE CLUSTERED INDEX
--        NO DUPLICATES ARE PRESENT YET
-- -----------------------------------------------------------------

CREATE CLUSTERED INDEX IX_test ON #testUniquifier(i)

INSERT @results
SELECT 'Non-Unique clustered index, no duplicates' AS description, * FROM sizeOfMyTable

DROP INDEX IX_test ON #testUniquifier

-- -----------------------------------------------------------------
-- TEST3: CREATES A NON-UNIQUE CLUSTERED INDEX
--        10000 DUPLICATE VALUES ARE PRESENT
-- -----------------------------------------------------------------

UPDATE TOP(10000) #testUniquifier SET i = 1

CREATE CLUSTERED INDEX IX_test ON #testUniquifier(i)

INSERT @results
SELECT 'Non-Unique clustered index, some duplicates' AS description, * FROM sizeOfMyTable

DROP INDEX IX_test ON #testUniquifier

-- -----------------------------------------------------------------
-- TEST4: CREATES A NON-UNIQUE CLUSTERED INDEX
--        ALL ROWS CONTAIN THE SAME VALUE (1)
-- -----------------------------------------------------------------

UPDATE #testUniquifier SET i = 1

CREATE CLUSTERED INDEX IX_test ON #testUniquifier(i)

INSERT @results
SELECT 'Non-Unique clustered index, all duplicates' AS description, * FROM sizeOfMyTable

-- -----------------------------------------------------------------
-- Display results
-- -----------------------------------------------------------------

SELECT *
FROM @results;
```



As you can see, the uniquifier is added only to the keys that are duplicated:

<a href="/wp-content/uploads/2014/03/uniquifier.png"><img class="size-full wp-image-792 alignnone" alt="uniquifier" src="/wp-content/uploads/2014/03/uniquifier.png" width="604" height="86" /></a>

<span style="line-height:1.5em;">Another way to discover the same results would be looking at the output of DBCC PAGE().</span>

Looking at the text output of DBCC PAGE, uniquifiers are displayed as 0 (zero) when the values are not set, but the values are actually missing from the page.

This becomes even clearer when using DBCC PAGE WITH TABLERESULTS:



```sql
IF OBJECT_ID('tempdb..#formatteddata') IS NOT NULL	
    DROP TABLE #formatteddata;

SELECT *, ROWNUM = ROW_NUMBER() OVER (ORDER BY page_id, slot_id)
INTO #formatteddata
FROM #testUniquifier
CROSS APPLY sys.fn_PhysLocCracker(%%physloc%%);

IF OBJECT_ID('tempdb..#dbccpage') IS NOT NULL
    DROP TABLE #dbccpage;


CREATE TABLE #dbccpage (
    page_id int,
    ParentObject varchar(128),
    Object varchar(128),
    Field varchar(128),
    value varchar(4000),
    Slot AS SUBSTRING(Object, NULLIF(CHARINDEX('Slot ',Object,1),0) + 5, ISNULL(NULLIF(CHARINDEX(' ',Object,6),0),0) - 5)
)

DECLARE @current_page_id int;

DECLARE pages CURSOR STATIC LOCAL FORWARD_ONLY READ_ONLY
FOR
SELECT DISTINCT page_id 
FROM #formatteddata

OPEN pages

FETCH NEXT FROM pages INTO @current_page_id

WHILE @@FETCH_STATUS = 0
BEGIN 
    INSERT INTO #dbccpage (ParentObject, Object, Field, value)
    EXEC sp_executesql N'DBCC PAGE (2, 1, @pageid, 3) WITH TABLERESULTS;', N'@pageid int', @current_page_id

    UPDATE #dbccpage 
    SET page_id = @current_page_id
    WHERE page_id IS NULL

    FETCH NEXT FROM pages INTO @current_page_id
END

CLOSE pages;
DEALLOCATE pages;


WITH PageData AS  (
    SELECT page_id, slot, field, value
    FROM #dbccpage
    WHERE field IN ('i', 'UNIQUIFIER')
),
Uniquifiers AS (
    SELECT *
    FROM PageData
    PIVOT (MAX(value) FOR field IN ([i], [UNIQUIFIER])) AS pvt
),
sourceData AS (
    SELECT *
    FROM #formatteddata
)
SELECT src.ROWNUM, 
    src.i, 
    src.page_id,
    src.slot_id,
    UNIQUIFIER
FROM sourceData AS src
LEFT JOIN Uniquifiers AS unq
    ON src.slot_id = unq.slot
    AND src.page_id = unq.page_id
ORDER BY ROWNUM;
```



If you run the code in the different situations outlined before (unique clustered index, non-unique clustered index with or without duplicate keys) you will find the uniquifiers associated with each duplicate key and you will also notice that no uniquifier is generated for the keys that are unique.
