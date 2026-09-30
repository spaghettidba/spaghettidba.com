---
title: "Recipe 5: Killing blocking SPIDs"
date: "2022-02-28T14:00:00"
slug: "recipe-5-killing-blocking-spids"
source_url: "http://spaghettidba.com/2022/02/28/recipe-5-killing-blocking-spids/"
url: "/2022/02/28/recipe-5-killing-blocking-spids/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Welcome to the latest recipe of this Extended Events cookbook! You will find the first blog post of the series <a href="https://spaghettidba.com/10-dba-recipes-with-xesmarttarget/">here</a> and you can browse all recipes with the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-problem">The problem</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>In the previous recipe, you learned how to notify when specific events occur, using the <a href="https://github.com/spaghettidba/XESmartTarget/wiki/EmailResponse">EmailResponse</a>. Notifications are appropriate when user intervention is required, but when the system can resolve the issue automatically it's better to avoid notifying users of the issue altogether. Resolving the issue often means performing some action in the database, using T-SQL.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Of course, XESmartTarget has got you covered, with the <a href="https://github.com/spaghettidba/XESmartTarget/wiki/ExecuteTSQLResponse">ExecuteTSQLResponse</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>For this post, the problem to solve is this: a session has an open transaction, is blocking other sessions, it’s been sleeping for a long time and it’s probably a good idea to kill it. This usually happens when there’s a problem in the application, that doesn’t handle transactions properly and leaves open transactions for a long time, maybe because it displays an error dialog, waiting for user input. There is very little that you can do in these cases: the blocked processes continue to pile up and the only thing left to do is kill the offending session.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Let’s see how to do that with XESmartTarget.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Of course, there’s a session for that. The event to capture is the blocked_process_report. This event is connected to a server wide setting that controls the number of seconds after which a blocked process event is raised. That configuration option is “blocked process threshold”. If it is set to zero (default), the event is never raised. When it is set to a positive number N, the blocked_process_report event is raised every N seconds. Before you can use this event, you need to set “blocked process threshold” to, let’s say, 10 seconds:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">EXEC sp_configure 'advanced', 1;
RECONFIGURE
EXEC sp_configure 'blocked process threshold', 10;
RECONFIGURE 
GO</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Then, you can set up the session to capture the blocked_process_report event. Since the event is fired every time a process is blocked for 10 seconds or multiples of 10 seconds, you probably want to capture only one instance of the event. You could filter the session, using the filters available for Extended Event sessions, but, in this case, I will show you how to filter events on XESmartTarget instead.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS (SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe05')

CREATE EVENT SESSION [Recipe05] ON SERVER 
ADD EVENT sqlserver.blocked_process_report(
    ACTION(
        sqlserver.client_app_name,
        sqlserver.client_hostname,
        sqlserver.database_name,
        sqlserver.server_instance_name,
        sqlserver.server_principal_name,
        sqlserver.session_id,
        sqlserver.sql_text
    )
)
GO


IF NOT EXISTS (SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe05')
    ALTER EVENT SESSION Recipe05 ON SERVER STATE = START;</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The configuration for XESmartTarget uses the ExecuteTSQLResponse object, which has to be set up to execute commands on a target server. ServerName, DatabaseName, UserName, Password are used to establish the connection to the target server. TSQL is the command to execute.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript","highlightLines":"11,16"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe05",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "ExecuteTSQLResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "master",
                "TSQL": "EXEC killBlocker {transaction_id}",  // the notation {propertyname} is used to 
                                                              // include fields and action from the events
                "Events": [
                    "blocked_process_report"
                ],
                "Filter": "duration &gt; 20000000 " // 20 seconds
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>The Filter property controls which events are processed by the Response and it is available for all Response types. In this case, we want to process only the events that have been blocked for more than 20 seconds. Ideally, XESmartTarget will kill their blocker, so that the event is not processed again.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The property TSQL can reference fields and actions from the source events using the notation {propertyname}. In this example, {transaction_id} is a parameter passed to the stored procedure killblocker and it is taken right from the blocked_process_report event.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The killblocker stored procedure has to be created in the master database and it looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">USE master;
GO

IF OBJECT_ID('killBlocker') IS NULL EXEC('CREATE PROCEDURE killBlocker AS BEGIN RETURN END');
GO

--
-- Kills the session that is blocking the specified
-- transaction, when the blocking session is sleeping
-- and has not issued any command in the last 30 seconds
-- 
ALTER PROCEDURE killBlocker @transaction_id int
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @spid int;

    SELECT @spid = blocking_session_id
    FROM sys.dm_exec_sessions AS blocked_session
    INNER JOIN sys.dm_exec_requests AS blocked_request
        ON blocked_session.session_id = blocked_request.session_id
    INNER JOIN sys.dm_exec_sessions AS blocking_session
        ON blocked_request.blocking_session_id = blocking_session.session_id
    WHERE blocked_session.session_id = (
            SELECT DISTINCT request_session_id
            FROM sys.dm_tran_locks
            WHERE request_owner_id = @transaction_id
        )
        AND blocking_session.status = 'sleeping'
        AND blocking_session.last_request_start_time &lt; DATEADD(second,-30,GETDATE());
    
    DECLARE @sql nvarchar(100) = 'KILL ' + CAST(@spid AS nvarchar(10));
    EXEC(@sql);
END</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Save this JSON as c:\temp\Recipe_05_Kill_Blocking.json and, now that everything is in place, let’s run XESmartTarget:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File c:\temp\Recipe_05_Kill_Blocking.json --GlobalVariables ServerName=(local)\SQLEXPRESS</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>There is not much to see on the console window. Let’s generate some blocking instead:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1617,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-19.png"><img src="/wp-content/uploads/2022/02/image-19.png" alt="" class="wp-image-1617" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The command on the left leaves an open transaction, while the command on the right tries to access a resource held by the open transaction, so it gets blocked. Since the session on the left is sleeping, I expect it to be killed by XESmartTarget.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1618,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-20.png"><img src="/wp-content/uploads/2022/02/image-20.png" alt="" class="wp-image-1618" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>After 20 seconds of blocking, the session on the left gets killed and the blocked processes are free to continue. Yay!</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The <a href="https://github.com/spaghettidba/XESmartTarget/wiki/ExecuteTSQLResponse">ExecuteTSQLResponse</a> object allows you to execute custom T-SQL commands in response to Extended Events. The possibilities are unlimited: executing stored procedures, running updates on the database… the sky is the limit.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next recipe you will learn how to use the <a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a> to group and summarize events before writing the to a target table. There are countless applications for this technique, so make sure to Keep watching the <a href="https://spaghettidba.com/tag/xesmarttarget">XESmartTarget tag</a> for the next recipes!</p>
<!-- /wp:paragraph -->
