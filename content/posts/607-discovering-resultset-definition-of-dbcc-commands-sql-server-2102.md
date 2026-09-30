---
title: "Discovering resultset definition of DBCC commands in SQL Server 2012"
date: "2013-02-26T00:56:49"
slug: "discovering-resultset-definition-of-dbcc-commands-sql-server-2102"
source_url: "http://spaghettidba.com/2013/02/26/discovering-resultset-definition-of-dbcc-commands-sql-server-2102/"
url: "/2013/02/26/discovering-resultset-definition-of-dbcc-commands-sql-server-2102/"
categories: ["SQL Server", "T-SQL"]
tags: ["CHECKDB", "DBCC", "Linked Servers", "SQLServer", "undocumented"]
---

Back in 2011 I showed a method to <a href="/2011/11/16/discovering-the-output-of-dbcc-commands/">discover the resultset definition of DBCC undocumented commands</a>.

At the time, SQL Server 2012 had not been released yet and nothing suggested that the linked server trick could stop working on the new major version. Surprisingly enough it did.

If you try to run the same code showed in that old post on a 2012 instance, you will get a quite explicit error message:



```sql
DECLARE @srv nvarchar(4000);
SET @srv = @@SERVERNAME; -- gather this server name

-- Create the linked server
EXEC master.dbo.sp_addlinkedserver
    @server     = N'LOOPBACK',
    @srvproduct = N'SQLServ', -- it’s not a typo: it can’t be “SQLServer”
    @provider   = N'SQLNCLI', -- change to SQLOLEDB for SQLServer 2000
    @datasrc    = @srv;

-- Set the authentication to "current security context"
EXEC master.dbo.sp_addlinkedsrvlogin
    @rmtsrvname  = N'LOOPBACK',
    @useself     = N'True',
    @locallogin  = NULL,
    @rmtuser     = NULL,
    @rmtpassword = NULL;

USE tempdb;
GO

CREATE PROCEDURE loginfo
AS
BEGIN
    SET NOCOUNT ON;

    DBCC LOGINFO();
END
GO

SELECT *
INTO tempdb.dbo.loginfo_output
FROM OPENQUERY(LOOPBACK, 'SET FMTONLY OFF; EXEC tempdb.dbo.loginfo');

DROP PROCEDURE loginfo;
GO
```




```text
Msg 11528, Level 16, State 1, Procedure sp_describe_first_result_set, Line 1
The metadata could not be determined because statement 'DBCC LOGINFO();' in procedure 'loginfo' does not support metadata discovery.
```



This behaviour has to do with the way SQL Server 2012 tries to discover metadata at parse/bind time, when the resultset is not available yet for DBCC commands.

Fortunately, there is still a way to discover metadata when you have a SQL Server instance of a previous version available.

On my laptop I have a 2008R2 instance I can use to query the 2012 instance with a linked server:



```sql
-- run this on the 2008R2 instance
USE [master]
GO

EXEC master.dbo.sp_addlinkedserver
     @server = N'LOCALHOST\SQL2012'
    ,@srvproduct = N'SQL Server'

EXEC master.dbo.sp_addlinkedsrvlogin
     @rmtsrvname = N'LOCALHOST\SQL2012'
    ,@useself = N'True'
    ,@locallogin = NULL
    ,@rmtuser = NULL
    ,@rmtpassword = NULL
GO

SELECT *
INTO tempdb.dbo.loginfo_output
FROM OPENQUERY([LOCALHOST\SQL2012], 'SET FMTONLY OFF; EXEC tempdb.dbo.loginfo');
GO
```



This code pipes the results of the DBCC command into a table in the tempdb database in my 2008R2 instance. The table can now be scripted using SSMS:

<img class="alignnone" alt="" src="/wp-content/uploads/2011/11/script_table.png" width="605" height="397" />

Using the 2008R2 instance as a "Trojan Horse" for the metadata discovery, you can see that the resultset definition of DBCC LOGINFO() has changed again in SQL Server 2012:



```sql
CREATE TABLE [dbo].[loginfo_output](
	[RecoveryUnitId] [int] NULL,  -- new in SQL2012
	[FileId] [int] NULL,
	[FileSize] [bigint] NULL,
	[StartOffset] [bigint] NULL,
	[FSeqNo] [int] NULL,
	[Status] [int] NULL,
	[Parity] [tinyint] NULL,
	[CreateLSN] [numeric](25, 0) NULL
)
```



This trick will be particularly useful for an upcoming (and long overdue) post, so... stay tuned!
