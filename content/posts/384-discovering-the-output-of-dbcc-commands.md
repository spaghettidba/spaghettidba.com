---
title: "Discovering resultset definition of DBCC commands"
date: "2011-11-16T15:54:03"
slug: "discovering-the-output-of-dbcc-commands"
source_url: "http://spaghettidba.com/2011/11/16/discovering-the-output-of-dbcc-commands/"
url: "/2011/11/16/discovering-the-output-of-dbcc-commands/"
categories: ["SQL Server", "T-SQL"]
tags: ["DBCC", "LOOPBACK", "OPENQUERY", "SQL", "TABLERESULTS"]
---

Lots of blog posts and discussion threads suggest piping the output of DBCC commands to a table for further processing. That’s a great idea, but, unfortunately, an irritatingly high number of those posts contains an inaccurate table definition for the command output.

The reason behind this widespread inaccuracy is twofold.

On one hand the output of many DBCC commands changed over time and versions of SQL Server, and a table that was the perfect fit for the command in SQL Server 2000 is not  perfect any more. In this case, the blog/article/thread is simply old, but many people will keep referring to that source assuming that things did not change.

On the other hand, the output is not always documented in BOL, and people often have to guess the table definition based on the data returned by the command. I’ve been guilty of this myself and I’ve been corrected many times, until I decided that I needed a better way to discover the output definition.

<strong>You are a database professional and you don’t like to guess, because <em>guessing</em> is never as good as <em>knowing</em> it for sure.</strong>

In order to stop guessing, you will have to create a linked server named “loopback” that points back to the same instance where you are running the DBCC command.

I am sure you are asking yourself why you need such a strange thing as a loopback linked server. The idea behind is that you need a way to query the command as if it was a table or a view, so that it can be used as a valid source for a SELECT…INTO statement. The perfect tool for this kind of task is the OPENQUERY command, which allows sending pass-through queries, that don’t necessarily need to be SELECT statements. OPENQUERY requires a linked server, which can be any OLEDB data source, including a remote server or the same SQL Server instance where the linked server lies.

OK, let’s create it:



```sql
DECLARE @srv nvarchar(4000);
SET @srv = @@SERVERNAME; -- gather this server name

-- Create the linked server
EXEC master.dbo.sp_addlinkedserver
@server     = N'LOOPBACK',
@srvproduct = N'SQLServ', -- it’s not a typo: it can’t be “SQLServer”
@provider   = N'SQLNCLI', -- change to SQLOLEDB for SQLServer 2000
@datasrc    = @srv;


-- Set the authentication to "current security context"
EXEC master.dbo.sp_addlinkedsrvlogin
@rmtsrvname  = N'LOOPBACK',
@useself     = N'True',
@locallogin  = NULL,
@rmtuser     = NULL,
@rmtpassword = NULL;
```



In order to capture the output of DBCC commands, you have to wrap them inside a stored procedure, otherwise SQL Server could complain about missing column information. I don’t know the exact technical reason behind this error (I suppose it has to do with the way metadata is propagated), but this limitation can be overcome wrapping the command into a stored procedure and using “SET FMTONLY OFF” in the pass-through query.

This is also a nice way to overcome the single INSERT…EXEC limit (and implement many more interesting tricks that I hope to cover in future posts).

For instance, to capture the table definition of DBCC LOGINFO(), you will have to create a stored procedure similar to this:



```sql
USE tempdb;
GO

CREATE PROCEDURE loginfo
AS
BEGIN
    SET NOCOUNT ON;

    DBCC LOGINFO();

END
GO
```



With the stored procedure and the linked server in place, you can set up the call using OPENQUERY:



```sql
SELECT *
INTO tempdb.dbo.loginfo_output
FROM OPENQUERY(LOOPBACK, 'SET FMTONLY OFF; EXEC tempdb.dbo.loginfo');

DROP PROCEDURE loginfo;
GO
```



Running this script will create a table named “loginfo_output” in the tempdb database: you can find it in your object explorer and script it out to a new query editor window.

<a href="/wp-content/uploads/2011/11/script_table.png"><img src="/wp-content/uploads/2011/11/script_table.png" alt="" title="script_table" width="604" height="396" class="alignnone size-full wp-image-385" /></a>

Repeating these steps on instances running different versions on SQL Server reveals that the table definition changed in SQL2005 and then remained the same in 2008 and 2008R2.



```sql
-- SQL Server 2000
CREATE TABLE [dbo].[loginfo_output](
    [FileId]      [int] NULL,
    [FileSize]    [numeric](20, 0) NULL,
    [StartOffset] [numeric](20, 0) NULL,
    [FSeqNo]      [int] NULL,
    [Status]      [int] NULL,
    [Parity]      [tinyint] NULL,
    [CreateLSN]   [numeric](25, 0) NULL
)


-- SQL Server 2005, 2008 and 2008R2
CREATE TABLE [dbo].[loginfo_output](
    [FileId]      [int] NULL,
    [FileSize]    [bigint] NULL,
    [StartOffset] [bigint] NULL,
    [FSeqNo]      [int] NULL,
    [Status]      [int] NULL,
    [Parity]      [tinyint] NULL,
    [CreateLSN]   [numeric](25, 0) NULL
)
```



Now that you know how the output looks like, you can happily pipe the results of DBCC LOGINFO to an appropriate table:



```sql
-- Declare variable for dynamic sql
DECLARE @sql nvarchar(max)

-- Drop the table if already exists
IF OBJECT_ID('tempdb..loginfo_output') IS NOT NULL
    DROP TABLE tempdb..loginfo_output

-- Check SQL Server version
IF CAST(REPLACE(LEFT(CAST(SERVERPROPERTY('ProductVersion') AS nvarchar(128)),2),'.','') AS int) > 8
BEGIN
    -- SQL Server 2005+
    SET @sql = '
        CREATE TABLE tempdb..loginfo_output(
            [FileId]      [int] NULL,
            [FileSize]    [bigint] NULL,
            [StartOffset] [bigint] NULL,
            [FSeqNo]      [int] NULL,
            [Status]      [int] NULL,
            [Parity]      [tinyint] NULL,
            [CreateLSN]   [numeric](25, 0) NULL
        )
        '
END
ELSE
BEGIN
    -- SQL Server 2000
    SET @sql = '
        CREATE TABLE tempdb..loginfo_output(
            [FileId]      [int] NULL,
            [FileSize]    [numeric](20, 0) NULL,
            [StartOffset] [numeric](20, 0) NULL,
            [FSeqNo]      [int] NULL,
            [Status]      [int] NULL,
            [Parity]      [tinyint] NULL,
            [CreateLSN]   [numeric](25, 0) NULL
        )
        '
END

-- Create the output table
EXEC(@sql)

-- Execute DBCC command and
-- pipe results to the output table
INSERT tempdb..loginfo_output
EXEC('DBCC LOGINFO()')


-- Display results
SELECT *
FROM tempdb..loginfo_output
```



You could ask with good reason why you should use an output table when you could query the wrapper stored procedure directly with OPENQUERY. Based on observation, the trick does not always work and SQL Server can randomly complain about missing column information.



```text
Msg 7357, Level 16, State 2, Line 2
Cannot process the object "loginfo". The OLE DB provider "SQLNCLI10" for linked server "LOOPBACK" indicates that either the object has no columns or the current user does not have permissions on that object.
```



Again, I don’t have an in-depth technical answer: I can only report what I observed. It’s not a big deal indeed, because the output definition changes very slowly (typically between SQL Server versions) and you probably would review your code anyway when upgrading to a newer version. I guess you can live with a hardcoded table definition when the price to pay for having it dynamic is a random failure.

This post showed you how to capture the output of DBCC LOGINFO, but the same technique can be used for all DBCC commands that allow specifying WITH TABLERESULTS, extended stored procedures, remote stored procedures and all those programmable objects than cannot be inspected easily.

Now that you have the right tool in your hands, do yourself a favour: <em>stop guessing</em>!

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (5)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-968" class="archived-comment"><article><header><strong>Alfredo Giotti</strong> <time datetime="2011-11-18T13:53:00Z">November 18, 2011 at 14:53</time></header><section class="archived-comment-content">This could not have come at a better time. I am rewriting all of my maintenance scripts and I had difficulty determining the table structure for DBCC CHECKDB output. I am now able to cross-reference what I have built with the help of this post.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-969" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2011-11-18T13:54:30Z">November 18, 2011 at 14:54</time></header><section class="archived-comment-content">Great! Glad I could help.</section></article></li></ol></li><li id="wordpress-comment-970" class="archived-comment"><article><header><strong>Alfredo Giotti</strong> <time datetime="2011-11-18T14:21:56Z">November 18, 2011 at 15:21</time></header><section class="archived-comment-content">Thanks for posting, job well done!</section></article></li><li id="wordpress-comment-7874" class="archived-comment"><article><header><strong>Jeff Moden</strong> <time datetime="2015-05-26T22:49:51Z">May 26, 2015 at 23:49</time></header><section class="archived-comment-content">Unfortunately, the incredible "feature enhancements" of SQL Server 2012 blow this good method out of the water.<br><br>Msg 11528, Level 16, State 1, Procedure sp_describe_first_result_set, Line 1<br>The metadata could not be determined because statement 'DBCC LOGINFO();' in procedure 'loginfo' does not support metadata discovery.</section></article></li><li id="wordpress-comment-7875" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-05-26T22:52:42Z">May 26, 2015 at 23:52</time></header><section class="archived-comment-content">Yes, it's a well known issue. I have a workaround here /2013/02/26/discovering-resultset-definition-of-dbcc-commands-sql-server-2102/ but... surprise: it requires an older version of SQL Server :(</section></article></li></ol></details>
</div>
