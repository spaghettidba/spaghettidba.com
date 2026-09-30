---
title: "Non-unique indexes that COULD be unique"
date: "2014-01-30T15:45:30"
slug: "non-unique-indexes-that-could-be-unique"
source_url: "http://spaghettidba.com/2014/01/30/non-unique-indexes-that-could-be-unique/"
url: "/2014/01/30/non-unique-indexes-that-could-be-unique/"
categories: ["SQL Server"]
tags: ["SQL", "SQLServer", "constraints", "database", "indexes", "unique"]
---

In my last post I showed a query to identify <a href="/2014/01/29/non-unique-indexes-that-should-be-unique/">non-unique indexes that should be unique</a>.

You maybe have some other indexes that <em><strong>could</strong></em> be unique based on the data they contain, but are not.

To find out, you just need to query each of those indexes and group by the whole key, filtering out those that have duplicate values. It may look like an overwhelming amount of work, but the good news is I have a script for that:



```sql
DECLARE @sql nvarchar(max);

WITH indexes AS (
    SELECT
         QUOTENAME(OBJECT_SCHEMA_NAME(uq.object_id)) AS [schema_name]
        ,QUOTENAME(OBJECT_NAME(uq.object_id)) AS table_name
        ,uq.name AS index_name
        ,cols.name AS cols
    FROM sys.indexes AS uq
    CROSS APPLY (
        SELECT STUFF((
            SELECT ',' + QUOTENAME(sc.name) AS [text()]
            FROM sys.index_columns AS uc
            INNER JOIN sys.columns AS sc
                ON  uc.column_id = sc.column_id
                AND uc.object_id = sc.object_id
            WHERE uc.object_id = uq.object_id
                AND uc.index_id = uq.index_id
                AND uc.is_included_column = 0
            FOR XML PATH('')
        ),1,1,SPACE(0))
    ) AS cols (name)
    WHERE is_unique = 0
        AND has_filter = 0
        AND is_hypothetical = 0
        AND type IN (1,2)
        AND object_id IN (
            SELECT object_id
            FROM sys.objects
            WHERE is_ms_shipped = 0
            AND type = 'U'
        )
)
-- Build a big statement to query index data
SELECT @sql = (
    SELECT
        'SELECT ''' + [schema_name] + ''' AS [schema_name],
            ''' + table_name + ''' AS table_name,
            ''' + index_name + ''' AS index_name,
            can_be_unique =
                CASE WHEN (
                    SELECT COUNT(*)
                    FROM (
                        SELECT ' + cols + ',COUNT(*) AS cnt
                        FROM ' + [schema_name] + '.' + [table_name] + '
                        GROUP BY ' + cols + '
                        HAVING COUNT(*) > 1
                    ) AS data
                    ) > 0
                THEN 0
                ELSE 1
                END;'
    FROM indexes
    FOR XML PATH(''), TYPE
).value('.','nvarchar(max)');

-- prepare a table to receive results
DECLARE @results TABLE (
    [schema_name] sysname,
    [table_name] sysname,
    [index_name] sysname,
    [can_be_unique] bit
)

-- execute the script and pipe the results
INSERT @results
EXEC(@sql)

-- show candidate unique indexes
SELECT *
FROM @results
WHERE can_be_unique = 1
ORDER BY [schema_name], [table_name], [index_name]
```



The script should complete quite quickly, since you have convenient indexes in place. However, I suggest that you run it against a non production copy of your database, as it will scan all non unique indexes found in the database.

The results will include all the indexes that don't contain duplicate data. Whether you should make those indexes UNIQUE, only you can tell.

Some indexes may contain unique data unintentionally, but could definitely store duplicate data in the future. If you know your data domain, you will be able to spot the difference.
