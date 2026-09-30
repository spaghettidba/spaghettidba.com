---
title: "Recipe 8: Analyzing a Workload"
date: "2022-03-02T14:00:00"
slug: "recipe-8-analyzing-a-workload"
source_url: "http://spaghettidba.com/2022/03/02/recipe-8-analyzing-a-workload/"
url: "/2022/03/02/recipe-8-analyzing-a-workload/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Welcome to a new recipe of this Extended Events cookbook! You will find the first blog post of the series <a href="https://spaghettidba.com/10-dba-recipes-with-xesmarttarget/">here</a> and you can browse all recipes with the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-problem">The problem</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The idea comes from a blog post by Brent Ozar about "<a href="https://www.brentozar.com/archive/2020/08/how-to-find-out-whose-queries-are-using-the-most-cpu/">How to Find Out Whose Queries are Using The Most CPU</a>". Brent uses the Resource Governor to detect who's using the CPU. That's an interesting approach, but you can do the same more efficiently with XESmartTarget.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Analyzing a workload means capturing all the queries on a server, categorize them by application name, database name and login name, and creating samples at regular intervals, in order to describe the behavior of the workload over time, let’s say every one minute.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The events that you need this time are rpc_completed and sql_batch_completed. These two events are enough to describe the workload. Here is what the session script looks like:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS ( SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe08')

CREATE EVENT SESSION [Recipe08] ON SERVER 
ADD EVENT sqlserver.rpc_completed(
    ACTION(
        package0.event_sequence,
        sqlserver.client_app_name,
        sqlserver.client_pid,
        sqlserver.database_name,
        sqlserver.nt_username,
        sqlserver.server_principal_name,
        sqlserver.session_id
    )
    WHERE ([package0].[equal_boolean]([sqlserver].[is_system],(0)))
),
ADD EVENT sqlserver.sql_batch_completed(
    ACTION(
        package0.event_sequence,
        sqlserver.client_app_name,
        sqlserver.client_pid,
        sqlserver.database_name,
        sqlserver.nt_username,
        sqlserver.server_principal_name,
        sqlserver.session_id
    )
    WHERE ([package0].[equal_boolean]([sqlserver].[is_system],(0)))
)
GO

IF NOT EXISTS ( SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe08')
    ALTER EVENT SESSION Recipe08 ON SERVER STATE = START;</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This is what the configuration looks like:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript","highlightLines":"14"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe08",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "GroupedTableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_08_WorkloadAnalysis",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "snapshot_id AS CONVERT(SUBSTRING(CONVERT(collection_time,'System.String'),1,16),'System.DateTime')", 
                    "client_app_name", 
                    "server_principal_name", 
                    "database_name",
                    "SUM(cpu_time) AS tot_cpu",
                    "SUM(duration) AS tot_duration",
                    "SUM(logical_reads) AS tot_reads",
                    "SUM(writes) AS tot_writes",
                    "COUNT(collection_time) AS execution_count"
                ],
                "Events": [
                    "rpc_completed",
                    "sql_batch_completed"
                ]
            }
        ]
    }
} </pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>We used the GroupedTableAppender before, but this time we are grouping data using an Expression Column as part of the GROUP BY columns, in order to get a date column with precision up to the minute, to use as a snapshot_id. The expression converts the column “collection_time” (it’an automatic column, added by XESmartTarget to all the events captured) from DateTime to String, removing the last two digits (the seconds). The conversion depends on a weird combination of the short date and long time formats:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1681,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-36.png"><img src="/wp-content/uploads/2022/02/image-36.png" alt="" class="wp-image-1681" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>In this case, the snapshot_id will be in the format dd-MM-yyyy HH:mm:ss, so taking the first 16 characters, as the SUBSTRING function here does, returns dd-MM-yyyy HH:mm, for instance 18-02-2022 10:15. If you’re using a different format, make sure you’re changing the expression accordingly. Converting it back to System.DateTime ensures that you get a proper datetime2 column that you can sort on.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Before starting XESmartTarget, you’d better create the target table manually:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">CREATE TABLE [dbo].[Recipe_08_WorkloadAnalysis](
	[snapshot_id] [datetime2](7) NULL,
	[client_app_name] [nvarchar](255) NULL,
	[server_principal_name] [nvarchar](128) NULL,
	[database_name] [nvarchar](128) NULL,
	[tot_cpu] [bigint] NULL,
	[tot_duration] [bigint] NULL,
	[tot_reads] [bigint] NULL,
	[tot_writes] [bigint] NULL,
	[execution_count] [bigint] NULL,
	CONSTRAINT UQ_Recipe_08_WorkloadAnalysis 
		UNIQUE (snapshot_id, client_app_name, server_principal_name, database_name)
) </pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Now that the table is ready, you can save the configuration file and start XESmartTarget:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File c:\temp\Recipe_08_WorkloadAnalysis.json --GlobalVariables ServerName=(local)\SQLEXPRESS</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>Let’s leave this running for a while and have a look at the data in the target table:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1692,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/03/image.png"><img src="/wp-content/uploads/2022/03/image.png" alt="" class="wp-image-1692" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>To answer the question in Brent’s post, Whose Queries are Using The Most CPU? Let’s find out! Turns out it’s me (surprise!):</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1646,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-28.png"><img src="/wp-content/uploads/2022/02/image-28.png" alt="" class="wp-image-1646" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>Not only I can analyze the workload as a whole, but I can also plot cpu usage by database or login or application in a chart like this:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1648,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-29.png"><img src="/wp-content/uploads/2022/02/image-29.png" alt="" class="wp-image-1648" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>Well, maybe Azure Data Studio is probably not the best tool for the job, but you can use something like <a href="https://grafana.com/">Grafana</a> to plot the data.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a> is a super powerful tool! It can group on Expression Columns and can be incredibly helpful when you have to summarize event data over time.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next recipe we will see how to take <a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a> to the next level and simulate what Query Store does (especially useful if you’re not on 2016 or later). Keep an eye on the <a href="https://spaghettidba.com/tag/xesmarttarget">XESmartTarget tag</a>!</p>
<!-- /wp:paragraph -->
