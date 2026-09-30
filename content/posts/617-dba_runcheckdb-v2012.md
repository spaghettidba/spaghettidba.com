---
title: "dba_runCHECKDB v2(012)"
date: "2013-02-27T20:48:44"
slug: "dba_runcheckdb-v2012"
source_url: "http://spaghettidba.com/2013/02/27/dba_runcheckdb-v2012/"
url: "/2013/02/27/dba_runcheckdb-v2012/"
categories: ["SQL Server", "T-SQL"]
tags: ["CHECKDB", "SQL", "SQLServer", "stored procedures"]
---

If you are one among the many that downloaded my consistency check stored procedure called “<a href="/2011/11/28/email-alert-dbcc-checkdb/">dba_RunCHECKDB</a>”, you may have noticed a “small” glitch… it doesn’t work on SQL Server 2012!

This is due to the resultset definition of <a href="http://msdn.microsoft.com/en-us/library/ms176064.aspx">DBCC CHECKDB</a>, which has changed again in SQL Server 2012. Trying to pipe the results of that command in the table definition for SQL Server 2008 produces a column mismatch and it obviously fails.

Fixing the code is very easy indeed, but I could never find the time to post the corrected version until today.

Also, I had to discover the new table definition for DBCC CHECKDB, and it was not just as easy as it used to be in SQL Server 2008. In fact, a couple of days ago I posted a way to <a href="/2013/02/26/discovering-resultset-definition-of-dbcc-commands-sql-server-2102/">discover the new resultset definition</a> working around the cumbersome metadata discovery feature introduced in SQL Server 2012.

Basically, the new output of DBCC CHECKDB now includes 6 new columns:



```sql
    CREATE TABLE ##DBCC_OUTPUT(
        Error int NULL,
        [Level] int NULL,
        State int NULL,
        MessageText nvarchar(2048) NULL,
        RepairLevel nvarchar(22) NULL,
        Status int NULL,
        DbId int NULL, -- was smallint in SQL2005
        DbFragId int NULL,      -- new in SQL2012
        ObjectId int NULL,
        IndexId int NULL,
        PartitionId bigint NULL,
        AllocUnitId bigint NULL,
        RidDbId smallint NULL,  -- new in SQL2012
        RidPruId smallint NULL, -- new in SQL2012
        [File] smallint NULL,
        Page int NULL,
        Slot int NULL,
        RefDbId smallint NULL,  -- new in SQL2012
        RefPruId smallint NULL, -- new in SQL2012
        RefFile smallint NULL,  -- new in SQL2012
        RefPage int NULL,
        RefSlot int NULL,
        Allocation smallint NULL
    )
```



If you Google the name of one of these new columns, you will probably find a lot of blog posts (no official documentation, unfortunately) that describes the new output of DBCC CHECKDB, but none of them is strictly correct: all of them indicate the smallint columns as int.

Not a big deal, actually, but still incorrect.

I will refrain from posting the whole procedure here: I updated the code in the <a href="/2011/11/28/email-alert-dbcc-checkdb/">original post</a>, that you can find clicking <a href="/2011/11/28/email-alert-dbcc-checkdb/">here</a>. You can also download the code from the <a href="/code-repository/">Code Repository</a>.

As usual, suggestions and comments are welcome.
