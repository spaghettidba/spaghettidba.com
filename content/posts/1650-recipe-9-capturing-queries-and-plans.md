---
title: "Recipe 9: Capturing Queries and Plans"
date: "2022-03-03T14:00:00"
slug: "recipe-9-capturing-queries-and-plans"
source_url: "http://spaghettidba.com/2022/03/03/recipe-9-capturing-queries-and-plans/"
url: "/2022/03/03/recipe-9-capturing-queries-and-plans/"
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
<p>In the previous recipe we used XESmartTarget to analyze a workload and we could characterize it by application/login/database. Now let’s take one more step: let’s capture all the queries and their plans and add query_hash and query_plan_hash to the analysis table. We will also capture plans and query text on separate tables.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The session looks a bit like the one that we had for the previous recipe, but the events are different.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS ( SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe09')

CREATE EVENT SESSION [Recipe09] ON SERVER 
ADD EVENT sqlserver.sp_statement_completed(
	SET collect_statement=(1)
    ACTION(
		sqlserver.client_app_name,
		sqlserver.client_hostname,
		sqlserver.database_name,
		sqlserver.plan_handle,
		sqlserver.query_hash,
		sqlserver.query_plan_hash,
		sqlserver.server_principal_name
	)
    WHERE ([sqlserver].[query_hash] &lt;&gt; 0)
),
ADD EVENT sqlserver.sql_statement_completed(
	SET collect_statement=(1)
    ACTION(
		sqlserver.client_app_name,
		sqlserver.client_hostname,
		sqlserver.database_name,
		sqlserver.plan_handle,
		sqlserver.query_hash,
		sqlserver.query_plan_hash,
		sqlserver.server_principal_name
	)
    WHERE ([sqlserver].[query_hash] &lt;&gt; 0)
)
GO

IF NOT EXISTS ( SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe09')
    ALTER EVENT SESSION Recipe09 ON SERVER STATE = START;</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>This time, instead of capturing sql_batch_completed and rpc_completed, we have to capture sql_statement_completed and sp_statement_completed. This is because we have to capture events that carry the plan_handle, query_hahs and query_plan_hash columns, that are available on the individual statements rather than the whole batches or stored procedures.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>First, we need to create some tables to store the data captured by the session:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">CREATE TABLE [dbo].[Recipe_09_WorkloadAnalysis](
	[snapshot_id] [datetime2](7) NULL,
	[client_app_name] [nvarchar](255) NULL,
	[server_principal_name] [nvarchar](128) NULL,
	[database_name] [nvarchar](128) NULL,
	[query_hash] [decimal](20, 0) NULL,
	[query_plan_hash] [decimal](20, 0) NULL,
	[tot_cpu] [bigint] NULL,
	[tot_duration] [bigint] NULL,
	[tot_reads] [bigint] NULL,
	[tot_writes] [bigint] NULL,
	[execution_count] [bigint] NULL,
	CONSTRAINT UQ_Recipe_09_WorkloadAnalysis 
		UNIQUE (snapshot_id, client_app_name, server_principal_name, database_name, query_hash, query_plan_hash)

) 

CREATE TABLE [dbo].[Recipe_09_WorkloadAnalysis_Queries](
	[query_hash] [numeric](20, 0) PRIMARY KEY,
	[sql_text] [nvarchar](max) NULL
)

CREATE TABLE [dbo].[Recipe_09_WorkloadAnalysis_Plans](
	[query_plan_hash] [numeric](20, 0) PRIMARY KEY,
	[query_plan] [xml] NULL
)
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>The target configuration is rather complex: we have three tables to populate, so we need three separate Responses.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe09",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "GroupedTableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_09_WorkloadAnalysis",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "snapshot_id AS CONVERT(SUBSTRING(CONVERT(collection_time,'System.String'),1,16),'System.DateTime')", 
                    "client_app_name", 
                    "server_principal_name", 
                    "database_name",
                    "query_hash",
                    "query_plan_hash",
                    "SUM(cpu_time) AS tot_cpu",
                    "SUM(duration) AS tot_duration",
                    "SUM(logical_reads) AS tot_reads",
                    "SUM(writes) AS tot_writes",
                    "COUNT(collection_time) AS execution_count"
                ]
            },
            {
                "__type": "GroupedTableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_09_WorkloadAnalysis_Queries",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "query_hash",
                    "MIN(statement) AS sql_text"
                ]
            },
            {
                "__type": "ExecuteTSQLResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TSQL": "INSERT INTO Recipe_09_WorkloadAnalysis_Plans SELECT TOP(1) {query_plan_hash} AS query_plan_hash, query_plan FROM sys.dm_exec_query_plan({plan_handle}) AS qp WHERE NOT EXISTS(SELECT * FROM Recipe_09_WorkloadAnalysis_Plans WITH (READCOMMITTEDLOCK) WHERE query_plan_hash = {query_plan_hash})"
            }
        ]
    }
}
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>The first Response takes care of aggregating the data, as we did for the previous recipe. This time we have some more columns to group on (query_hash and query_plan_hash), but it’s rather similar to what we did last time.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The second Response saves the text of the queries by query hash. We can safely use MIN(statement) to make sure that we capture one instance of the query text for each plan_hash.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The third Response captures the query plans. Instead of capturing the plan from the session, we’re extracting it from sys.dm_exec_query_plan. I’m not really sure this is a great idea from a performance standpoint, but I’m just demonstrating a concept here: I strongly suggest that you measure the impact before running this against a production server.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>OK, let’s save the configuration and start XESmartTarget:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File C:\temp\Recipe_09_Workload_Analysis.json --GlobalVariables ServerName=(local)\SQLEXPRESS</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>After a while, we can inspect the data in the target tables. As expected, the first one contains the workload data:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1653,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-30.png"><img src="/wp-content/uploads/2022/02/image-30.png" alt="" class="wp-image-1653" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The second table contains all the queries:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1655,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-31.png"><img src="/wp-content/uploads/2022/02/image-31.png" alt="" class="wp-image-1655" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>And the last one contains all the query plans:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1656,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-32.png"><img src="/wp-content/uploads/2022/02/image-32.png" alt="" class="wp-image-1656" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>Using this data, we can easily identify the most cpu intensive queries, using this statement:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">SELECT TOP(10) wa.query_hash, MIN(sql_text) AS sql_text, SUM(tot_cpu) AS sum_tot_cpu
FROM [dbo].[Recipe_09_WorkloadAnalysis] AS wa
INNER JOIN [dbo].[Recipe_09_WorkloadAnalysis_Queries] AS q
	ON wa.query_hash = q.query_hash
GROUP BY wa.query_hash
ORDER BY sum_tot_cpu DESC
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:image {"id":1657,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-33.png"><img src="/wp-content/uploads/2022/02/image-33.png" alt="" class="wp-image-1657" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>There is not much going on on this instance, but still the query to extract plans tops the chart. Hmmm… it looks like extracting query plans this way is probably not a great idea after all :)</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Combining multiple Response types, you can achieve very complex results. XESmartTarget can be a life saver when you have to pull event data from many events and manipulate the data in many ways.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next recipe we will see how to write events to a time-series database like InfluxDB, using XESmartTarget and the TelegrafAppenderResponse. Keep an eye on the <a href="https://spaghettidba.com/tag/xesmarttarget">XESmartTarget tag</a>!</p>
<!-- /wp:paragraph -->
