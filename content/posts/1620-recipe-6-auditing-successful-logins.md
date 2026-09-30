---
title: "Recipe 6: Auditing Successful Logins"
date: "2022-02-28T14:05:07"
slug: "recipe-6-auditing-successful-logins"
source_url: "http://spaghettidba.com/2022/02/28/recipe-6-auditing-successful-logins/"
url: "/2022/02/28/recipe-6-auditing-successful-logins/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Welcome to a new recipe of this Extended Events cookbook! You will find the first blog post of the series <a href="https://spaghettidba.com/10-dba-recipes-with-xesmarttarget/">here</a> and you can browse all recipes with the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>. </p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-problem">The problem</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Sometimes you are not interested in the individual events captured by a session, but you want to extract some information from a series of events, by grouping and aggregating them. This is the case of events that happen very often, like, logon events, that can help you validate your story.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Imagine that you inherited a big, busy and chaotic SQL Server instance, with lots of databases and logins. One of the things that you probably want to do is track which logins are active and which ones are not and can be safely disabled.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>One of the possible ways of doing this is to enable successful and failed login auditing in ERRORLOG, but this creates a lot of noise. No thanks, I don't want a messy ERRORLOG.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Another possibility is to capture login events with an Extended Events session and write them to a file target. However, with this approach you capture the individual events, which you don’t need. What you really want is a very simple information: when has each login accessed the server the last time? Writing session data to a file target does not answer that question directly, but forces you to read and aggregate all the data in the file at a later time.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>XESmartTarget can help with this, using the <a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a>. This Response type aggregates the data in memory before writing it to a target table, where it is merged with the existing data.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Let’s set up a session for this. You need to capture the “login” event, which contains all the data that you need.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS ( SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe06')

CREATE EVENT SESSION [Recipe06] ON SERVER 
ADD EVENT sqlserver.login(
    SET collect_database_name=(1)
    ACTION(
        sqlserver.client_app_name,
        sqlserver.server_principal_name
    )
)
GO


IF NOT EXISTS ( SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe06')
    ALTER EVENT SESSION Recipe06 ON SERVER STATE = START;</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This is what the configuration looks like:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript","highlightLines":"17,18,19"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe06",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "GroupedTableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_06_LoginAudit",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "server_principal_name",
                    "database_name",
                    "client_app_name",
                    "MIN(collection_time) AS first_seen", 
                    "MAX(collection_time) AS last_seen", 
                    "COUNT(collection_time) AS logon_count" 
                ],
                "Events": [
                    "login"
                ]
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>It’s very similar to the TableAppenderResponse, with one main difference: you can have aggregated columns, using the usual aggregation functions and aliases to assign a name to the columns. All the columns included in the output and not aggregated are used to create the groups. The data is aggregated first in memory and then it is merged with the data already in the table, using the group by columns as the join key.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>There is one important rule to respect though: the name of the aggregated column cannot be the same as any other column from the events, so make sure to assign a new name.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Let’s save the file as c:\temp\Recipe_06_Login_Audit.json and run XESmartTarget:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File c:\temp\Recipe_06_Login_Audit.json --GlobalVariables ServerName=(local)\SQLEXPRESS</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>The console window informs us that the rows are not being written directly to the target table, but they are grouped and aggregated according to the configuration.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1623,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-21.png"><img src="/wp-content/uploads/2022/02/image-21.png" alt="" class="wp-image-1623" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>Inspecting the data in the target table confirms that we have indeed 7 rows:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1624,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-22.png"><img src="/wp-content/uploads/2022/02/image-22.png" alt="" class="wp-image-1624" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>If you let XESmartTarget run for a while, it will keep writing more data to the target tables and it will update the counts, merging the data from memory with the data already in the table:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1626,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-23.png"><img src="/wp-content/uploads/2022/02/image-23.png" alt="" class="wp-image-1626" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>If you want to identify unused logins, all you have to do is run XESmartTarget for a meaningful amount of time (let’s say one month) and it will fill the data in the target table. Easy peasy.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a> is a powerful tool to perform aggregations on the events captured by Extended Events sessions. It can be used to accomplish a lot of tasks.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next recipe you will learn how to use the <a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderResponse</a> to identify unused tabled in the database. Keep watching the <a href="https://spaghettidba.com/tag/xesmarttarget">XESmartTarget tag</a>!</p>
<!-- /wp:paragraph -->
