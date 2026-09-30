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

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (3)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-1528" class="archived-comment"><article><header><strong>SutoCom</strong> <time datetime="2013-03-01T19:24:30Z">March 1, 2013 at 20:24</time></header><section class="archived-comment-content">Reblogged this on <a href="http://sutocom.net/2013/03/01/3305/" rel="nofollow ugc noopener noreferrer">Sutoprise Avenue, A SutoCom Source</a>.</section></article></li><li id="wordpress-comment-1694" class="archived-comment"><article><header><strong>Stephen Swan</strong> <time datetime="2013-05-01T18:32:19Z">May 1, 2013 at 19:32</time></header><section class="archived-comment-content">This is a great script!<br><br>A couple of things on the script could be changed though.<br>1) The @AllMessages parameter should be @allMessages to be consistent and allow it to work on case-sensitive databases.<br>2)  Most people do not have SQL2000 servers anymore and could use sp_send_dbmail instead of cdosysmail. I.e.<br>                    EXECUTE [msdb].[dbo].[sp_send_dbmail] <br>				    @profile_name = @dbmail_profile,<br>				    @recipients = @dbmail_recipient,<br>				    @body = @body,<br>				    @body_format = 'HTML',<br>				    @subject = 'Consistency error found!'<br>3) I would add a drop statement to the script so that it could be easily updated using multi-server query tools.<br><br>Thanks for putting all this together.</section></article></li><li id="wordpress-comment-1789" class="archived-comment"><article><header><strong>Binyam</strong> <time datetime="2013-11-15T14:20:19Z">November 15, 2013 at 15:20</time></header><section class="archived-comment-content">I just found this today and I am loving it except for one thing; It would have been even nicer if there was a way to exclude databases. In its current for you have to do it all or do it one by one.</section></article></li></ol></details>
</div>
