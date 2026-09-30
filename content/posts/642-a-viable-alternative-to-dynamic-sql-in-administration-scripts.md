---
title: "A viable alternative to dynamic SQL in administration scripts"
date: "2013-04-22T17:53:41"
slug: "a-viable-alternative-to-dynamic-sql-in-administration-scripts"
source_url: "http://spaghettidba.com/2013/04/22/a-viable-alternative-to-dynamic-sql-in-administration-scripts/"
url: "/2013/04/22/a-viable-alternative-to-dynamic-sql-in-administration-scripts/"
categories: ["SQL Server", "T-SQL"]
tags: ["DBA", "SQL", "SQLServer", "administration scripts", "dynamic sql", "software", "sp_MSForEachDb", "stored procedures"]
---

As a DBA, you probably have your toolbox full of scripts, procedures and functions that you use for the day-to-day administration of your instances.

I’m no exception and my hard drive is full of scripts that I tend to accumulate and never throw away, even if I know I will never need (or find?) them again.

However, my preferred way to organize and maintain my administration scripts is a database called “TOOLS”, which contains all the scripts I regularly use.

One of the challenges involved in keeping the scripts in a database rather than in a script file is the inability to choose a database context for the execution. When a statement is encapsulated in a view, function or stored procedure in a database, every reference to a database-specific object is limited to the database that contains the programmable object itself. The only way to overcome this limitation is the use of dynamic sql.

For instance, if I want to query the name of the tables in a database, I can use the following statement:



```sql
SELECT name FROM sys.tables
```



The statement references a catalog view specific to a single database, so if I enclose it in a stored procedure, the table names returned by this query are those found in the database that contains the stored procedure itself:



```sql
USE TOOLS;
GO

CREATE PROCEDURE getTableNames
AS
SELECT name FROM sys.tables;
GO

EXEC getTableNames;
```



This is usually not an issue, since most stored procedures will not cross the boundaries of the database they are created in. Administration scripts are different, because they are meant as a single entry point to maintain the whole SQL server instance.

In order to let the statement work against a different database, you need to choose one of the following solutions:
<ol>
	<li>dynamic SQL</li>
	<li>sp_executesql</li>
	<li>marking as a system object</li>
	<li>... an alternative way</li>
</ol>
Each of these techniques has its PROs and its CONs and I will try to describe them in this post.
<h3><b>1. Dynamic SQL</b></h3>
It’s probably the easiest way to solve the issue: you just have to concatenate the database name to the objects names.



```sql
USE TOOLS;
GO

ALTER PROCEDURE getTableNames @db_name sysname
AS
BEGIN
    DECLARE @sql nvarchar(max)
    SET @sql = 'SELECT name FROM '+ QUOTENAME(@db_name) +'.sys.tables';

    EXEC(@sql)
END
GO

EXEC getTableNames 'msdb';
```



PROS:
<ul>
	<li>very easy to implement for simple statements</li>
</ul>
CONS:
<ul>
	<li>can rapidly turn to a nightmare with big, complicated statements, as each object must be concatenated with the database name. Different objects have different ways to be related to the database: tables and views can be concatenated directly, while functions such as OBJECT_NAME accept an additional parameter to specify the database name.</li>
	<li>the statement has to be treated as a string and enclosed in quotes, which means that:
<ul>
	<li>quotes must be escaped, and escaped quotes must be escaped again and escaped and re-escaped quotes… ok, you know what I mean</li>
	<li>no development aids such as intellisense, just-in-time syntax checks and syntax coloring</li>
</ul>
</li>
</ul>
<b> </b>
<h3><b>2. sp_executesql</b></h3>
It’s a neater way to avoid concatenating the database name to each object referenced in the statement.



```sql
USE TOOLS;
GO

ALTER PROCEDURE getTableNames @db_name sysname
AS
BEGIN

    -- use a @sql variable to store the whole query
    -- without concatenating the database name

    DECLARE @sql nvarchar(max);

    SET @sql = 'SELECT name FROM sys.tables';

    -- concatenate the database name to the
    -- sp_executesql call, just once

    DECLARE @cmd nvarchar(max);

    SET @cmd = 'EXEC '+ QUOTENAME(@db_name) +'.sys.sp_executesql @sql';

    EXEC sp_executesql @cmd, N'@sql nvarchar(max)', @sql

END
GO

EXEC getTableNames 'msdb';
```



PROS:
<ul>
	<li>the dynamic sql is taken as a whole and does not need to be cluttered with multiple concatenations</li>
</ul>
CONS:
<ul>
	<li>needs some more work than a straight concatenation and can be seen as “obscure”</li>
	<li>suffers from the same issues found with plain dynamic sql, because the statement is, again, treated as a string</li>
</ul>
<h3><b>3. System object</b></h3>
Nice and easy: every stored procedure you create in the master database with the “sp_” prefix can be executed from any database context.

Using the undocumented stored procedure sp_MS_marksystemobject you can also mark the stored procedure as a “system object” and let it reference the tables in the database from which it is invoked.



```sql
USE master;
GO

ALTER PROCEDURE sp_getTableNames
AS
BEGIN
    SELECT name FROM sys.tables
END
GO

EXEC sys.sp_MS_marksystemobject 'sp_getTableNames'
GO

USE msdb;
GO

EXEC sp_getTableNames;
```



PROS:
<ul>
	<li>no need to use dynamic sql</li>
</ul>
CONS:
<ul>
	<li>requires creating objects in the “master” database, which is something I tend to avoid</li>
	<li>works with stored procedures only (actually, it works with other objects, such as tables and views, but you have to use the “sp_” prefix. The day I will find a view named “sp_getTableNames” in the master database it won’t be safe to stay near me)</li>
</ul>
<h3><b>An alternative method: </b></h3>
It would be really helpful if we could store the statement we want to execute inside an object that doesn’t involve dynamic sql and doesn’t need to be stored in the master database. In other words, we need a way to get the best of both worlds.

Is there such a solution? Apparently, there isn’t.

The ideal object to store a statement and reuse it later is a view, but there is no way to “execute” a view against a different database. In fact you don’t execute a view, you just select from it, which is quite a different thing.

What you “execute” when you select from a view is the statement in its definition (not really, but let me simplify).

So, what we would need to do is just read the definition from a view and use the statement against the target database. Sounds straightforward, but it’s not.

The definition of a view also contains the “CREATE VIEW” statement and stripping it off is not just as easy as it seems.

Let’s see the issue with an example: I will create a view to query the last update date of the index statistics in a database, using the query from <a href="http://sqlserverperformance.wordpress.com/tag/dmv-queries/">Glenn Berry’s Diagnostic Queries</a>.



```sql
USE TOOLS;
GO

-- When were Statistics last updated on all indexes?  (Query 48)
CREATE VIEW statisticsLastUpdate
AS
SELECT
     DB_NAME() AS database_name
    ,o.NAME AS stat_name
    ,i.NAME AS [Index Name]
    ,STATS_DATE(i.[object_id], i.index_id) AS [Statistics Date]
    ,s.auto_created
    ,s.no_recompute
    ,s.user_created
    ,st.row_count
FROM sys.objects AS o WITH (NOLOCK)
INNER JOIN sys.indexes AS i WITH (NOLOCK)
    ON o.[object_id] = i.[object_id]
INNER JOIN sys.stats AS s WITH (NOLOCK)
    ON i.[object_id] = s.[object_id]
    AND i.index_id = s.stats_id
INNER JOIN sys.dm_db_partition_stats AS st WITH (NOLOCK)
    ON o.[object_id] = st.[object_id]
    AND i.[index_id] = st.[index_id]
WHERE o.[type] = 'U';
```



I just had to remove ORDER BY and OPTION(RECOMPILE) because query hints cannot be used in views.

Querying the object definition returns the whole definition of the view, not only the SELECT statement:



```sql
SELECT OBJECT_DEFINITION(OBJECT_ID('statisticsLastUpdate')) AS definition
```




```text
definition
-------------------------------------------------------------------
-- When were Statistics last updated on all indexes?  (Query 48)
CREATE VIEW statisticsLastUpdate
AS
SELECT
     DB_NAME() AS database_name
    ,o.NAME AS stat_name
    ,i.NAME AS [Index Name]
    ,STATS_DATE(i.[object_id], i.index_id) AS [Statistics Date]
    ,s.auto_created
    ,s.no_recompute

(1 row(s) affected)
```



In order to extract the SELECT statement, we would need something able to parse (properly!) the view definition and we all know how complex it can be.

Fortunately, SQL Server ships with an undocumented function used in replication that can help solving the problem: its name is fn_replgetparsedddlcmd.

This function accepts some parameters, lightly documented in the code: fn_replgetparsedddlcmd (@ddlcmd, @FirstToken, @objectType, @dbname, @owner, @objname, @targetobject)

Going back to the example, we can use this function to extract the SELECT statement from the view definition:



```sql
SELECT master.sys.fn_replgetparsedddlcmd(
    OBJECT_DEFINITION(OBJECT_ID('statisticsLastUpdate'))
        ,'CREATE'
        ,'VIEW'
        ,DB_NAME()
        ,'dbo'
        ,'statisticsLastUpdate'
        ,NULL
) AS statement
```




```text
statement
---------------------------------------------------------------------
AS
SELECT
     DB_NAME() AS database_name
    ,o.NAME AS stat_name
    ,i.NAME AS [Index Name]
    ,STATS_DATE(i.[object_id], i.index_id) AS [Statistics Date]
    ,s.auto_created
    ,s.no_recompute
    ,s.user_created
    ,st.row_count

(1 row(s) affected)
```



The text returned by the function still contains the “AS” keyword, but removing it is a no-brainer:



```sql
DECLARE @cmd nvarchar(max)
SELECT @cmd = master.sys.fn_replgetparsedddlcmd(
    OBJECT_DEFINITION(OBJECT_ID('statisticsLastUpdate'))
        ,'CREATE'
        ,'VIEW'
        ,DB_NAME()
        ,'dbo'
        ,'statisticsLastUpdate'
        ,NULL
    )

SELECT @cmd = RIGHT(@cmd, LEN(@cmd) - 2) -- Removes "AS"

SELECT @cmd AS statement
```




```text
statement
-------------------------------------------------------------------

SELECT
     DB_NAME() AS database_name
    ,o.NAME AS stat_name
    ,i.NAME AS [Index Name]
    ,STATS_DATE(i.[object_id], i.index_id) AS [Statistics Date]
    ,s.auto_created
    ,s.no_recompute
    ,s.user_created
    ,st.row_count

(1 row(s) affected)
```



Now that we are able to read the SELECT statement from a view’s definition, we can execute that statement against any database we like, or even against all the databases in the instance.



```sql
-- =============================================
-- Author:      Gianluca Sartori - spaghettidba
-- Create date: 2013-04-16
-- Description: Extracts the view definition
--              and runs the statement in the
--              database specified by @db_name
--              If the target database is a pattern,
--              the statement gets executed against
--              all databases matching the pattern.
-- =============================================

CREATE PROCEDURE [dba_execute_view]
     @view_name sysname
    ,@db_name sysname
AS
BEGIN

SET NOCOUNT,
    XACT_ABORT,
    QUOTED_IDENTIFIER,
    ANSI_NULLS,
    ANSI_PADDING,
    ANSI_WARNINGS,
    ARITHABORT,
    CONCAT_NULL_YIELDS_NULL ON;
    SET NUMERIC_ROUNDABORT OFF;

DECLARE @cmd nvarchar(max)
DECLARE @sql nvarchar(max)

DECLARE @vw_schema sysname
DECLARE @vw_name sysname

IF OBJECT_ID(@view_name) IS NULL
BEGIN
    RAISERROR('No suitable object found for name %s',16,1,@view_name)
    RETURN
END

IF DB_ID(@db_name) IS NULL
    AND @db_name NOT IN ('[USER]','[SYSTEM]')
    AND @db_name IS NOT NULL
BEGIN
    RAISERROR('No suitable database found for name %s',16,1,@view_name)
    RETURN
END

SELECT @vw_schema = OBJECT_SCHEMA_NAME(OBJECT_ID(@view_name)),
    @vw_name = OBJECT_NAME(OBJECT_ID(@view_name))

SELECT @cmd = master.sys.fn_replgetparsedddlcmd(
    OBJECT_DEFINITION(OBJECT_ID(@view_name))
        ,'CREATE'
        ,'VIEW'
        ,DB_NAME()
        ,@vw_schema
        ,@vw_name
        ,NULL
    )

SELECT @cmd = RIGHT(@cmd, LEN(@cmd) - 2) -- Removes "AS"

-- CREATE A TARGET TEMP TABLE
SET @sql = N'
    SELECT TOP(0) * INTO #results FROM ' + @view_name + ';

    INSERT #results
    EXEC [dba_ForEachDB]
        @statement = @cmd,
        @name_pattern = @db_name;

    SELECT * FROM #results;'

EXEC sp_executesql
     @sql
    ,N'@cmd nvarchar(max), @db_name sysname'
    ,@cmd
    ,@db_name

END
```



The procedure depends on <a href="/2011/09/09/a-better-sp_msforeachdb/">dba_ForEachDB</a>, the stored procedure I posted a couple of years ago that replaces the one shipped by Microsoft. If you still prefer their version, you’re free to modify the code as you wish.

Now that we have a stored procedure that “executes” a view, we can use it to query statistics update information from a different database:



```sql
EXEC [dba_execute_view] 'statisticsLastUpdate', 'msdb'
```



<a href="/wp-content/uploads/2013/04/single_db.png"><img class="alignnone size-full wp-image-645" alt="single_db" src="/wp-content/uploads/2013/04/single_db.png" width="604" height="99" /></a>

We could also query the same information from all user databases:



```sql
EXEC [dba_execute_view] 'statisticsLastUpdate', '[USER]'
```



<a href="/wp-content/uploads/2013/04/multidb.png"><img class="alignnone size-full wp-image-646" alt="multidb" src="/wp-content/uploads/2013/04/multidb.png" width="604" height="92" /></a>

That’s it, very easy and straightforward.

Just one suggestion for the SELECT statements in the views: add a DB_NAME() column, in order to understand where the data comes from, or it’s going to be a total mess.
<h3><b>Next steps:</b></h3>
This is just the basic idea, the code can be improved in many ways.

For instance, we could add a parameter to decide whether the results must be piped to a temporary table or not. As you probably know, INSERT…EXEC cannot be nested, so you might want to pipe the results to a table in a different way.

Another thing you might want to add is the ability to order the results according to an additional parameter.

To sum it up, with a little help from Microsoft, we can now safely create a database packed with all our administration stuff and execute the queries against any database in our instance.
