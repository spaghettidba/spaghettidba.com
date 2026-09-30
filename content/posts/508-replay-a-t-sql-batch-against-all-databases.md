---
title: "Replay a T-SQL batch against all databases"
date: "2012-06-27T21:25:32"
slug: "replay-a-t-sql-batch-against-all-databases"
source_url: "http://spaghettidba.com/2012/06/27/replay-a-t-sql-batch-against-all-databases/"
url: "/2012/06/27/replay-a-t-sql-batch-against-all-databases/"
categories: ["SQL Server", "T-SQL"]
tags: ["Replay", "Trace", "batch", "sp_MSForEachDb"]
---

It’s been quite a lot since I last posted on this blog and I apologize with my readers, both of them :-).

Today I would like to share with you a handy script I coded recently during a SQL Server health check. One of the tools I find immensely valuable for conducting a SQL Server assessment is <a href="http://sqlserverperformance.wordpress.com/2012/06/11/sql-server-2012-diagnostic-information-queries-june-2012/">Glenn Berry’s SQL Server Diagnostic Information Queries</a>. The script contains several queries that can help you collect and analyze a whole lot of information about a SQL Server instance and I use it quite a lot.

The script comes with a blank results spreadsheet, that can be used to save the information gathered by the individual queries. Basically, the spreadsheet is organized in tabs, one for each query and has no preformatted column names, so that you can run the query, select the whole results grid, copy with headers and paste everything to the appropriate tab.

When working with multiple instances, SSMS can help automating this task with multiserver queries. Depending on your SSMS settings, the results of a multiserver query can be merged into a single grid, with an additional column holding the server name.

<a href="/wp-content/uploads/2012/06/multiserver.png"><img class="alignnone size-full wp-image-509" title="MultiServer" src="/wp-content/uploads/2012/06/multiserver.png" alt="" width="604" height="354" /></a>

<a href="/wp-content/uploads/2012/06/multiserver2.png"><img class="alignnone size-full wp-image-510" title="MultiServer2" src="/wp-content/uploads/2012/06/multiserver2.png" alt="" width="604" height="202" /></a>

This feature is very handy, because it lets you run a statement against multiple servers without changing the statement itself.

This works very well for the queries in the first part of Glenn Berry’s script, which is dedicated to instance-level checks. The second part of the script is database-specific and you have to repeat the run+copy+paste process for each database in your instance.

It would be great if there was a feature in SSMS that allowed you to obtain the same results as the multiserver queries, scaled down to the database level. Unfortunately, SSMS has no such feature and  the only possible solution is to code it yourself... or borrow my script!

Before rushing to the code, let’s describe briefly the idea behind and the challenges involved.

It would be quite easy to take a single statement and use it with sp_MsForEachDB, but this solution has several shortcomings:
<ul>
	<li>The results would display as individual grids</li>
	<li>There would be no easy way to determine which results grid belongs to which database</li>
	<li>The statement would have to be surrounded with quotes and existing quotes would have to be doubled, with an increased and unwanted complexity</li>
</ul>
The ideal tool for this task should simply take a statement and run it against all [user] databases without modifying the statement at all, merge the results in a single result set and add an additional column to hold the database name. Apparently, sp_MSForEachDB, <a href="/2011/09/09/a-better-sp_msforeachdb/">besides being undocumented and potentially nasty</a>, is not the right tool for the job.

That said, the only option left is to capture the statement from its query window, combining a trace, a loopback linked server and various other tricks.

Here’s the code:



```sql
-- =============================================
-- Author:      Gianluca Sartori - @spaghettidba
-- Create date: 2012-06-26
-- Description: Records statements to replay
--              against all databases.
-- =============================================
CREATE PROCEDURE replay_statements_on_each_db
    @action varchar(10) = 'RECORD',
    @start_statement_id int = NULL,
    @end_statement_id   int = NULL
AS
BEGIN

    SET NOCOUNT ON;

    DECLARE @TraceFile nvarchar(256);
    DECLARE @TraceFileNoExt nvarchar(256);
    DECLARE @LastPathSeparator int;
    DECLARE @TracePath nvarchar(256);
    DECLARE @TraceID int;
    DECLARE @fs bigint = 5;
    DECLARE @r int;
    DECLARE @spiid int = @@SPID;
    DECLARE @srv nvarchar(4000);
    DECLARE @ErrorMessage nvarchar(4000);
    DECLARE @ErrorSeverity int;
    DECLARE @ErrorState int;
    DECLARE @sql nvarchar(max);
    DECLARE @statement nvarchar(max);
    DECLARE @column_list nvarchar(max);

    IF @action NOT IN ('RECORD','STOPRECORD','SHOWQUERY','REPLAY')
        RAISERROR('A valid @action (RECORD,STOPRECORD,SHOWQUERY,REPLAY) must be specified.',16,1)

    -- *********************************************** --
    -- *                 RECORD                      * --
    -- *********************************************** --
    IF @action = 'RECORD'
    BEGIN

        BEGIN TRY

            -- Identify the path of the default trace
            SELECT @TraceFile = path
            FROM master.sys.traces
            WHERE id = 1

            -- Split the directory / filename parts of the path
            SELECT @LastPathSeparator = MAX(number)
            FROM master.dbo.spt_values
            WHERE type = 'P'
                  AND number BETWEEN 1 AND LEN(@tracefile)
                  AND CHARINDEX('\', @TraceFile, number) = number
            --' fix WordPress's sql parser quirks'

            SELECT @TraceFile =
                  SUBSTRING(
                         @TraceFile
                        ,1
                        ,@LastPathSeparator
                  )
                  + 'REPLAY_'
                  + CONVERT(char(8),GETDATE(),112)
                  + REPLACE(CONVERT(varchar(8),GETDATE(),108),':','')
                  + '.trc'

            SET @TraceFileNoExt = REPLACE(@TraceFile,N'.trc',N'')

            -- create trace
            EXEC sp_trace_create @TraceID OUTPUT, 0, @TraceFileNoExt, @fs, NULL;

            --add filters and events
            EXEC sp_trace_setevent @TraceID, 41, 1, 1;
            EXEC sp_trace_setevent @TraceID, 41, 12, 1;
            EXEC sp_trace_setevent @TraceID, 41, 13, 1;

            EXEC sp_trace_setfilter @TraceID, 1, 0, 7, N'%fn_trace_gettable%'
            EXEC sp_trace_setfilter @TraceID, 1, 0, 7, N'%replay_statements_on_each_db%'
            EXEC sp_trace_setfilter @TraceID, 12, 0, 0, @spiid

            --start the trace
            EXEC sp_trace_setstatus @TraceID, 1

            --create a global temporary table to store the statements
            IF OBJECT_ID('tempdb..##replay_info') IS NOT NULL
                DROP TABLE ##replay_info;

            CREATE TABLE ##replay_info (
                trace_id int,
                statement_id int,
                statement_text nvarchar(max)
            );

            --save the trace id in the global temp table
            INSERT INTO ##replay_info (trace_id) VALUES(@TraceID);

        END TRY
        BEGIN CATCH

            --cleanup the trace
            IF EXISTS( SELECT 1 FROM sys.traces WHERE id = @TraceId AND status = 1 ) EXEC sp_trace_setstatus @TraceID, 0;
            IF EXISTS( SELECT 1 FROM sys.traces WHERE id = @TraceId AND status = 0 ) EXEC sp_trace_setstatus @TraceID, 2;

            IF OBJECT_ID('tempdb..##replay_info') IS NOT NULL
                DROP TABLE ##replay_info;

            SELECT @ErrorMessage  = ERROR_MESSAGE(),
                   @ErrorSeverity = ERROR_SEVERITY(),
                   @ErrorState    = ERROR_STATE();

            RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);

        END CATCH

    END

    -- *********************************************** --
    -- *              STOP RECORDING                 * --
    -- *********************************************** --
    IF @action = 'STOPRECORD'
    BEGIN

        BEGIN TRY

            -- gather the trace id
            SELECT @TraceID = trace_id
            FROM ##replay_info;

            IF @TraceId IS NULL
                RAISERROR('No data has been recorded!',16,1)

            DELETE FROM ##replay_info;

            -- identify the trace file
            SELECT TOP(1) @TraceFile = path
            FROM sys.traces
            WHERE path like '%REPLAY[_]______________.trc'
            ORDER BY id DESC

            -- populate the global temporary table with
            -- the statements recorded in the
            INSERT INTO ##replay_info
            SELECT @TraceID,
                ROW_NUMBER() OVER(ORDER BY (SELECT NULL)),
                TextData
            FROM fn_trace_gettable(@traceFile, DEFAULT)
            WHERE TextData IS NOT NULL;

            --stop and deltete the trace
            IF EXISTS( SELECT 1 FROM sys.traces WHERE id = @TraceId AND status = 1 ) EXEC sp_trace_setstatus @TraceID, 0;
            IF EXISTS( SELECT 1 FROM sys.traces WHERE id = @TraceId AND status = 0 ) EXEC sp_trace_setstatus @TraceID, 2;

        END TRY
        BEGIN CATCH

            --stop and deltete the trace
            IF EXISTS( SELECT 1 FROM sys.traces WHERE id = @TraceId AND status = 1 ) EXEC sp_trace_setstatus @TraceID, 0;
            IF EXISTS( SELECT 1 FROM sys.traces WHERE id = @TraceId AND status = 0 ) EXEC sp_trace_setstatus @TraceID, 2;

            SELECT @ErrorMessage  = ERROR_MESSAGE(),
                   @ErrorSeverity = ERROR_SEVERITY(),
                   @ErrorState    = ERROR_STATE();

            RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);

        END CATCH

    END

    -- *********************************************** --
    -- *           SHOW COLLECTED QUERIES            * --
    -- *********************************************** --
    IF @action = 'SHOWQUERY'
    BEGIN
        BEGIN TRY

            IF OBJECT_ID('tempdb..##replay_info') IS NULL
                RAISERROR('No data has been recorded yet',16,1);

            SET @sql = 'SELECT statement_id, statement_text FROM ##replay_info ';

            IF @start_statement_id IS NOT NULL AND @end_statement_id IS NULL
                SET @sql = @sql + ' WHERE statement_id = @start_statement_id ';

            IF @start_statement_id IS NOT NULL AND @end_statement_id IS NOT NULL
                SET @sql = @sql + ' WHERE statement_id
                                    BETWEEN @start_statement_id AND @end_statement_id';

            EXEC sp_executesql
                 @sql
                ,N'@start_statement_id int, @end_statement_id int'
                ,@start_statement_id
                ,@end_statement_id;

        END TRY
        BEGIN CATCH
            SELECT @ErrorMessage  = ERROR_MESSAGE(),
                   @ErrorSeverity = ERROR_SEVERITY(),
                   @ErrorState    = ERROR_STATE();

            RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
        END CATCH
    END

    -- *********************************************** --
    -- *                 REPLAY                      * --
    -- *********************************************** --
    IF @action = 'REPLAY'
    BEGIN

        BEGIN TRY

            --load the selected statement(s)
            SET @statement = '
                SET @sql = ''''
                SELECT @sql += statement_text + '' ''
                FROM ##replay_info
            ';

            IF @start_statement_id IS NOT NULL AND @end_statement_id IS NULL
                SET @statement =
                    @statement
                    + ' WHERE statement_id = @start_statement_id ';

            IF @start_statement_id IS NOT NULL AND @end_statement_id IS NOT NULL
                SET @statement =
                    @statement
                    + ' WHERE statement_id
                        BETWEEN @start_statement_id AND @end_statement_id';

            EXEC sp_executesql
                 @statement
                ,N'@start_statement_id int, @end_statement_id int, @sql nvarchar(max) OUTPUT'
                ,@start_statement_id
                ,@end_statement_id
                ,@sql OUTPUT;

            IF NULLIF(LTRIM(@sql),'') IS NULL
                RAISERROR('Unable to locate the statement(s) specified.',16,1)

            SET @srv = @@SERVERNAME; -- gather this server name

            IF EXISTS (SELECT * FROM sys.servers WHERE name = 'TMPLOOPBACK')
                EXEC sp_dropserver 'TMPLOOPBACK';

            -- Create a loopback linked server
            EXEC master.dbo.sp_addlinkedserver
                @server     = N'TMPLOOPBACK',
                @srvproduct = N'SQLServ', -- it’s not a typo: it can’t be “SQLServer”
                @provider   = N'SQLNCLI', -- change to SQLOLEDB for SQLServer 2000
                @datasrc    = @srv;

            -- Set the authentication to "current security context"
            EXEC master.dbo.sp_addlinkedsrvlogin
                @rmtsrvname  = N'TMPLOOPBACK',
                @useself     = N'True',
                @locallogin  = NULL,
                @rmtuser     = NULL,
                @rmtpassword = NULL;

            -- Use a permanent table in Tempdb to store the output
            IF OBJECT_ID('tempdb..___outputTable') IS NOT NULL
                DROP TABLE tempdb..___outputTable;

            -- Execute the statement in Tempdb to discover the column definition
            SET @statement = '
                SELECT TOP(0) *
                INTO tempdb..___outputTable
                FROM OPENQUERY(TMPLOOPBACK,''
                    SET FMTONLY OFF; EXEC tempdb.sys.sp_executesql N''''' + REPLACE(@sql,'''','''''''''') + '''''
                '')
            ';

            EXEC(@statement);

            SET @statement = @sql;

            -- Build the column list of the output table
            SET @column_list = STUFF((
                SELECT ',' + QUOTENAME(C.name)
                FROM tempdb.sys.columns AS C
                INNER JOIN tempdb.sys.tables AS T
                    ON C.object_id = T.object_id
                WHERE T.name = '___outputTable'
                FOR XML PATH('')
            ),1,1,SPACE(0));

            -- Add a "Database Name" column
            ALTER TABLE tempdb..___outputTable ADD Database__Name sysname;

            -- Build a sql statement to execute
            -- the recorded statement against all databases
            SET @sql =
                'N''INSERT tempdb..___outputTable(' + @column_list + ') EXEC(@statement); UPDATE tempdb..___outputTable SET Database__Name = DB_NAME() WHERE Database__Name IS NULL;''';

            -- Build a statement to execute on each database context
            ;WITH dbs AS (
                SELECT *,
                    system_db = CASE WHEN name IN ('master','model','msdb','tempdb') THEN 1 ELSE 0 END
                FROM sys.databases
                WHERE   DATABASEPROPERTY(name, 'IsSingleUser') = 0
                    AND HAS_DBACCESS(name) = 1
                    AND state_desc = 'ONLINE'
            )
            SELECT @sql = (
                SELECT
                    'EXEC ' + QUOTENAME(name) + '.sys.sp_executesql ' +
                        @sql + ',' +
                        'N''@statement nvarchar(max)'',' +
                        '@statement;' + char(10) AS [text()]
                FROM dbs
                ORDER BY name
                FOR XML PATH('')
            );

            -- Execute multi-db sql and pass in the actual statement
            EXEC sp_executeSQL @sql, N'@statement nvarchar(max)', @statement

            --
            SET @sql = '
                SELECT Database__Name AS [Database  Name], ' + @column_list + '
                FROM tempdb..___outputTable
                ORDER BY 1;
            '

            EXEC sp_executesql @sql;

            EXEC tempdb.sys.sp_executesql N'DROP TABLE ___outputTable';

        END TRY
        BEGIN CATCH
            SELECT @ErrorMessage  = ERROR_MESSAGE(),
                   @ErrorSeverity = ERROR_SEVERITY(),
                   @ErrorState    = ERROR_STATE();

            RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
        END CATCH

    END

END
```



As you can see, the code creates a stored procedure that accepts a parameter named @action, which is used to determine what the procedure should do. Specialized sections of the procedure handle every possible value for the parameter, with the following logic:

<a href="/wp-content/uploads/2012/06/flow.png"><img class="alignnone size-full wp-image-511" title="flow" src="/wp-content/uploads/2012/06/flow.png" alt="" width="311" height="381" /></a>

First of all you start recording, then you execute the statements to repeat on each database, then you stop recording. From that moment on, you can enumerate the statements captured and execute them, passing a specific statement id or a range of ids.

The typical use of the procedure could look like this:



```sql
-- start recording
EXECUTE replay_statements_on_each_db
    @action = 'RECORD'

-- run the statements you want to replay
SELECT DATABASEPROPERTYEX(DB_NAME(),'Recovery') AS RecoveryModel

-- stop recording
EXECUTE replay_statements_on_each_db
    @action = 'STOPRECORD'

-- display captured statements
EXECUTE replay_statements_on_each_db
    @action = 'SHOWQUERY'

-- execute the first statement
EXECUTE replay_statements_on_each_db
    @action             = 'REPLAY',
    @start_statement_id = 1,
    @end_statement_id   = 1
```



You can see the results of the script execution here:

<a href="/wp-content/uploads/2012/06/results.png"><img class="alignnone size-full wp-image-513" title="results" src="/wp-content/uploads/2012/06/results.png" alt="" width="358" height="273" /></a>

Obviuosly this approach is totally overkill for just selecting the database recovery model, but it can become very handy when the statement’s complexity raises.

This seems a perfect fit for Glen Berry’s diagnostic queries, which is where we started from. You can go back to that script and add the record instructions just before the database specific queries start:

<a href="/wp-content/uploads/2012/06/record1.png"><img class="alignnone size-full wp-image-514" title="Record" src="/wp-content/uploads/2012/06/record1.png" alt="" width="604" height="380" /></a>

At the end of the script you can add the instructions to stop recording and show the queries captured by the procedure.

<a href="/wp-content/uploads/2012/06/record2.png"><img class="alignnone size-full wp-image-515" title="Record2" src="/wp-content/uploads/2012/06/record2.png" alt="" width="604" height="442" /></a>

Once the statements are recorded, you can run any of the statements against all databases. For instance, I decided to run the top active writes index query (query 51).

<a href="/wp-content/uploads/2012/06/query18.png"><img class="alignnone size-full wp-image-516" title="query18" src="/wp-content/uploads/2012/06/query18.png" alt="" width="604" height="326" /></a>

As expected, the procedure adds the database name column to the result set and then displays the merged results.

You may have noticed that I skipped the first statement in the database-specific section of the script, which is a DBCC command. Unfortunately, not all kind of statement can be captured with this procedure, because some limitations apply. Besides the inability to capture some DBCC commands, please note that the column names must be explicitly set.

I think that a CLR procedure could overcome these limitations, or at least some of them. I hope I will find the time to try the CLR method soon and I promise I will blog the results.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (4)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-1225" class="archived-comment"><article><header><strong>isalom</strong> <time datetime="2012-06-27T20:45:21Z">June 27, 2012 at 21:45</time></header><section class="archived-comment-content">Great post! I'll give it a try for sure.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1226" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2012-06-27T20:47:19Z">June 27, 2012 at 21:47</time></header><section class="archived-comment-content">Thanks! Let me know if you find some quirks (I'm sure there are some).</section></article></li></ol></li><li id="wordpress-comment-1309" class="archived-comment"><article><header><strong>Dukagjin Maloku</strong> <time datetime="2012-09-29T20:29:00Z">September 29, 2012 at 21:29</time></header><section class="archived-comment-content">Brilliant work my friend ... Thanks for sharing!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1310" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2012-10-01T07:54:14Z">October 1, 2012 at 08:54</time></header><section class="archived-comment-content">Thanks Dugi!</section></article></li></ol></li></ol></details>
</div>
