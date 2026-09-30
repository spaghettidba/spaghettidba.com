---
title: "Non-unique indexes that should be unique"
date: "2014-01-29T19:21:14"
slug: "non-unique-indexes-that-should-be-unique"
source_url: "http://spaghettidba.com/2014/01/29/non-unique-indexes-that-should-be-unique/"
url: "/2014/01/29/non-unique-indexes-that-should-be-unique/"
categories: ["SQL Server"]
tags: ["SQL", "SQLServer", "constraints", "database", "indexes", "unique"]
---

Defining the appropriate primary key and unique constraints is fundamental for a good database design.

<a href="/wp-content/uploads/2014/01/unique.png"><img class="size-full wp-image-771 alignnone" alt="unique" src="/wp-content/uploads/2014/01/unique.png" width="549" height="409" /></a>

<span style="line-height:1.5em;">One thing that I often see overlooked is that all the indexes with a key that includes completely another UNIQUE index's key should in turn be created as UNIQUE. </span><span style="line-height:1.5em;">You could argue that such an index has probably been created by mistake, but it's not always the case.</span>

If you want to check your database for indexes that can be safely made UNIQUE, you can use the following script:



```sql
SELECT OBJECT_SCHEMA_NAME(uq.object_id) AS [schema_name],
    OBJECT_NAME(uq.object_id) AS table_name,
    uq.name AS unique_index_name,
    nui.name AS non_unique_index_name
FROM sys.indexes AS uq
CROSS APPLY (
    SELECT name, object_id, index_id
    FROM sys.indexes AS nui
    WHERE nui.object_id = uq.object_id
        AND nui.index_id <> uq.index_id
        AND nui.is_unique = 0
        AND nui.has_filter = 0
        AND nui.is_hypothetical = 0
) AS nui
WHERE is_unique = 1
    AND has_filter = 0
    AND is_hypothetical = 0
    AND uq.object_id IN (
        SELECT object_id
        FROM sys.tables
    )
    AND NOT EXISTS (

        SELECT column_id
        FROM sys.index_columns AS uc
        WHERE uc.object_id = uq.object_id
            AND uc.index_id = uq.index_id
            AND uc.is_included_column = 0

        EXCEPT

        SELECT column_id
        FROM sys.index_columns AS nuic
        WHERE nuic.object_id = nui.object_id
            AND nuic.index_id = nui.index_id
            AND nuic.is_included_column = 0

    )
ORDER BY [schema_name], table_name, unique_index_name
```



You may wonder why you should bother making those indexes UNIQUE.

The answer is that constraints help the optimizer building better execution plans. Marking an index as UNIQUE tells the optimizer that one and just one row can be found for each key value: it's a valuable information that can actually help estimating the correct cardinality.

Does the script return any rows? Make those indexes UNIQUE, you'll thank me later.
