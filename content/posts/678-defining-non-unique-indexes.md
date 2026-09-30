---
title: "SQL2014: Defining non-unique indexes in the CREATE TABLE statement"
date: "2013-06-28T17:02:48"
slug: "defining-non-unique-indexes"
source_url: "http://spaghettidba.com/2013/06/28/defining-non-unique-indexes/"
url: "/2013/06/28/defining-non-unique-indexes/"
categories: ["SQL Server", "T-SQL"]
tags: ["SQL", "SQL Server 2014", "Trace", "compound index", "nonclustered index", "undocumented"]
---

Now that my SQL Server 2014 CTP1 virtual machine is ready, I started to play with it and some new features and differences with the previous versions are starting to appear.

What I want to write about today is a T-SQL enhancement to DDL statements that brings in some new interesting considerations.

SQL Server 2014 now supports a new T-SQL syntax that allows defining an index in the CREATE TABLE statement without having to issue separate CREATE INDEX statements.

Up to now, the same could be achieved only with PRIMARY KEY and UNIQUE constraints, thus allowing UNIQUE indexes only.

For instance, the following statement creates a table with a unique clustered index on order_id and a unique nonclustered index on PO_number:



```sql
CREATE TABLE #orders (
     order_id uniqueidentifier NOT NULL
        PRIMARY KEY CLUSTERED DEFAULT NEWSEQUENTIALID()
    ,PO_number varchar(50) NOT NULL UNIQUE
    ,order_date datetime NOT NULL
    ,total_amount decimal(18,3)
)
```



OK, but what if I want to add a non-unique index to my table?

SQL Server 2014 offers a new syntax to do that inline with the table DDL:



```sql
CREATE TABLE #orders (
     order_id uniqueidentifier NOT NULL
        PRIMARY KEY CLUSTERED DEFAULT NEWSEQUENTIALID()
    ,PO_number varchar(50) NOT NULL UNIQUE
     -- creates a nonclustered index on order_date
    ,order_date datetime NOT NULL INDEX IX_order_date
    ,total_amount decimal(18,3)
)
```



A similar syntax can be used to create a compound index:



```sql
CREATE TABLE #orders (
     order_id uniqueidentifier NOT NULL
        PRIMARY KEY CLUSTERED DEFAULT NEWSEQUENTIALID()
    ,PO_number varchar(50) NOT NULL UNIQUE
    ,order_date datetime NOT NULL INDEX IX_order_date
    ,total_amount decimal(18,3)
    -- creates a compound index on PO_number and order_date
    ,INDEX IX_orders_compound(PO_number, order_date)
)
```



An interesting aspect of this new syntax is that it allows creating non-unique nonclustered indexes to table variables, which is something that couldn't be done in the previous versions.

The syntax to use is the same as for permanent tables:



```sql
DECLARE @orders TABLE (
     order_id uniqueidentifier NOT NULL
        PRIMARY KEY CLUSTERED DEFAULT NEWSEQUENTIALID()
    ,PO_number varchar(50) NOT NULL UNIQUE
    ,order_date datetime NOT NULL INDEX IX_order_date
    ,total_amount decimal(18,3)
)
```



Cool! But, wait: does this mean that table variables will now behave in the same way permanent tables do?

Not exactly.

Table variables don't have statistics, and being able to create indexes on them won't change anything in this regard.

Do you want a proof? OK, the skeptics can run the following code. Please make sure you capture the actual execution plan.



```sql
SET NOCOUNT ON;

-- create the table variable
DECLARE @orders TABLE (
     order_id uniqueidentifier NOT NULL
        PRIMARY KEY CLUSTERED DEFAULT NEWSEQUENTIALID()
    ,PO_number varchar(50) NOT NULL UNIQUE
    ,order_date datetime NOT NULL INDEX IX_order_date
    ,total_amount decimal(18,3)
)

-- insert some data
INSERT INTO @orders (order_date, PO_number, total_amount)
SELECT
     order_date   = DATEADD(second, CHECKSUM(NEWID()), GETDATE())
    ,PO_number    = CAST(NEWID() AS varchar(50))
    ,total_amount = CHECKSUM(NEWID()) / 1000.0
FROM sys.all_columns

-
SELECT COUNT(*)
FROM @orders
WHERE order_date > GETDATE()
OPTION (
     -- activate some (undocumented) trace flags to show
     -- statistics usage. More information on the flags
     -- can be found on Paul White's blog:
     -- http://sqlblog.com/blogs/paul_white/archive/2011/09/21/how-to-find-the-statistics-used-to-compile-an-execution-plan.aspx

     -- redirect output to the messages tab
     QUERYTRACEON 3604
     -- show "interesting" statistics
    ,QUERYTRACEON 9292
    -- show loaded statistics
    ,QUERYTRACEON 9402
    -- add RECOMPILE to let the optimizer "see"
    -- the table cardinality
    ,RECOMPILE
)
```



The output of the above batch is empty. Looks like no stats were loaded.

The actual execution plan confirms that no stats were loaded and the estimated cardinality of the table variable is way off:

<a href="/wp-content/uploads/2013/06/plan_11.png"><img class="alignnone size-full wp-image-686" alt="plan_1" src="/wp-content/uploads/2013/06/plan_11.png" width="604" height="194" /></a>

If we repeat the test with a temporary table, we see a different behaviour.



```sql
SET NOCOUNT ON;

IF OBJECT_ID('tempdb..#orders') IS NOT NULL
    DROP TABLE #orders;

CREATE TABLE #orders (
     order_id uniqueidentifier NOT NULL
        PRIMARY KEY CLUSTERED DEFAULT NEWSEQUENTIALID()
    ,PO_number varchar(50) NOT NULL UNIQUE
    ,order_date datetime NOT NULL INDEX IX_order_date
    ,total_amount decimal(18,3)
)

INSERT INTO #orders (order_date, PO_number, total_amount)
SELECT
     order_date   = DATEADD(second, CHECKSUM(NEWID()), GETDATE())
    ,PO_number    = CAST(NEWID() AS varchar(50))
    ,total_amount = CHECKSUM(NEWID()) / 1000.0
FROM sys.all_columns

SELECT COUNT(*)
FROM #orders
WHERE order_date > GETDATE()
OPTION (
     QUERYTRACEON 3604
    ,QUERYTRACEON 9292
    ,QUERYTRACEON 9402
)
```



This time the messages tab contains some output:



```text
Stats header loaded: DbName: tempdb, ObjName: #orders, IndexId: 2, ColumnName: order_date, EmptyTable: FALSE

Stats header loaded: DbName: tempdb, ObjName: #orders, IndexId: 2, ColumnName: order_date, EmptyTable: FALSE
```



The optimizer identified the statistics on the oder_date column as "interesting" and then loaded the stats header.

Again, the actual execution plan confirms that a better estimation is available:

<a href="/wp-content/uploads/2013/06/plan_2.png"><img class="alignnone size-full wp-image-679" alt="plan_2" src="/wp-content/uploads/2013/06/plan_2.png" width="604" height="194" /></a>

The lack of statistics has always been the most significant difference between table variables and temporary tables and SQL2014 doesn't appear to change the rules (yet).

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (1)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-1729" class="archived-comment"><article><header><strong>Chris Dorch</strong> <time datetime="2013-06-28T16:20:41Z">June 28, 2013 at 17:20</time></header><section class="archived-comment-content">Nice info there... I have the 2014 bits, but been too busy to install and play!</section></article></li></ol></details>
</div>
