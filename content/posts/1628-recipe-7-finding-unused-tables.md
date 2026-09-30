---
title: "Recipe 7: Finding Unused Tables"
date: "2022-03-01T14:00:00"
slug: "recipe-7-finding-unused-tables"
source_url: "http://spaghettidba.com/2022/03/01/recipe-7-finding-unused-tables/"
url: "/2022/03/01/recipe-7-finding-unused-tables/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Welcome toa new recipe of this Extended Events cookbook! You will find the first blog post of the series <a href="https://spaghettidba.com/10-dba-recipes-with-xesmarttarget/">here</a> and you can browse all recipes with the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>. </p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-problem">The problem</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The previous recipe showed you how to capture data from Extended Events sessions, summarize it in memory and then save it to a table in SQL Server, merging with any existing rows. This comes extremely handy when the events are not useful individually, but when the story is told by the aggregation of all the events.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Another possible problem that can be solved with the same technique is finding unused objects in the database. It looks like a trivial problem, but it’s not.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The easiest way to determine if a table is used or not is… deleting it and waiting for users to complain :) Of course, the easiest method is not always the most appropriate, and this makes no exception.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Audits would be extremely useful for this, because they capture the right events. Unfortunately they suffer from the same limitation discussed in the previous recipe: you don’t need the individual audit entries, all you need is a counter of accesses to the table. Again, <a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a> has got you covered.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The session for this recipe is going to be a bit weird. Instead of capturing the audit events, you’ll have to use a different type of event. The audit events are private and can only be used by the audit feature, so you need to track something else.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The lock_acquired events seem to have everything that you need: every time a table is accessed, a lock on the table is placed, so you can track them and determine whether the table is used or not. Let’s create a session:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS ( SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe07')

CREATE EVENT SESSION [Recipe07] ON SERVER
ADD EVENT sqlserver.lock_acquired (
    SET collect_database_name = (0)
        ,collect_resource_description = (1)
    ACTION(sqlserver.client_app_name, sqlserver.is_system, sqlserver.server_principal_name)
    WHERE (
        [package0].[equal_boolean]([sqlserver].[is_system], (0)) -- user SPID
        AND [package0].[equal_uint64]([resource_type], (5)) -- OBJECT
        AND [package0].[not_equal_uint64]([database_id], (32767))  -- resourcedb
        AND [package0].[greater_than_uint64]([database_id], (4)) -- user database
        AND [package0].[greater_than_equal_int64]([object_id], (245575913)) -- user object
        AND (
               [mode] = (1) -- SCH-S
            OR [mode] = (6) -- IS
            OR [mode] = (8) -- IX
            OR [mode] = (3) -- S
            OR [mode] = (5) -- X
        )
    )
);
GO


IF NOT EXISTS ( SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe07')
    ALTER EVENT SESSION Recipe07 ON SERVER STATE = START; </pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The configuration takes advantage of the capabilities of <a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a>: the events are processed by two separate Responses and merged into the same target table. The first Response only takes care of reads, while the second Response takes care of writes.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript","highlightLines":"22,39"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe07",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "GroupedTableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_07_TableAudit",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "client_app_name",
                    "database_id",
                    "object_id",
                    "MAX(collection_time) AS last_read"
                ],
                "Events": [
                    "lock_acquired"
                ],
                "Filter": "mode NOT IN ('X','IX')"
            },
            {
                "__type": "GroupedTableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_07_TableAudit",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "client_app_name",
                    "database_id",
                    "object_id",
                    "MAX(collection_time) AS last_write"
                ],
                "Events": [
                    "lock_acquired"
                ],
                "Filter": "mode IN ('X','IX')"
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Let’s save the JSON file as c:\temp\Recipe_07_Table_Audit.json.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Before you can run XESmartTarget, you need to create the target table with this script:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">USE [XERecipes]
GO

CREATE TABLE [dbo].[Recipe_07_TableAudit](
	[client_app_name] [nvarchar](255) NULL,
	[database_id] [int] NULL,
	[object_id] [int] NULL,
	[last_read] [datetime2](7) NULL,
	[last_write] [datetime2](7) NULL
) ON [PRIMARY]
GO</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>If you don't create the table upfront, XESmartTarget will try to create it, but the first Response that hits the database will do that and, in this case, you have different responses with different sets of output columns, so the resulting table would be missing one column in any case.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>OK, now that the target table is ready, it's time to run XESmartTarget:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File c:\temp\Recipe_07_Table_Audit.json --GlobalVariables ServerName=(local)\SQLEXPRESS</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>The console window shows that the two Responses are writing data independently:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1631,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-24.png"><img src="/wp-content/uploads/2022/02/image-24.png" alt="" class="wp-image-1631" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>If you query the target table, you will see that some tables appear there. Some will have a last_read date, some will have a last_write date and some will have both dates.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1632,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-25.png"><img src="/wp-content/uploads/2022/02/image-25.png" alt="" class="wp-image-1632" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>If you keep the application running for a meaningful amount of time, you will see all the tables appear in the target table, except for the ones that are not used. That’s pretty cool!</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In case you’re wondering, this works also if you have Read Committed Snapshot Isolation activated on your database.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a> can help you accomplish many tasks, including finding unused tables.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next recipe you will see use the <a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a> to analyze a workload and use the “collection_time” automatic column to create series of data based on the time of the event. Keep watching the <a href="https://spaghettidba.com/tag/xesmarttarget">XESmartTarget tag</a>!</p>
<!-- /wp:paragraph -->
