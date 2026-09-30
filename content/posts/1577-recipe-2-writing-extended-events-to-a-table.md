---
title: "Recipe 2: Writing Extended Events to a table"
date: "2022-02-23T14:00:00"
slug: "recipe-2-writing-extended-events-to-a-table"
source_url: "http://spaghettidba.com/2022/02/23/recipe-2-writing-extended-events-to-a-table/"
url: "/2022/02/23/recipe-2-writing-extended-events-to-a-table/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Welcome to the second recipe of this Extended Events cookbook! You will find the first blog post of the series <a href="https://spaghettidba.com/10-dba-recipes-with-xesmarttarget/">here</a> and you can browse all recipes with the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-problem">The problem</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This time, you want capture all the queries executing on your server and save the Extended Events data to a table in SQL Server. One of the things you cannot achieve easily with the standard targets in Extended Events is writing to a database table. If you check the documentation and all the blogs that you find on the Internet, all of them recommend using two possible methods to extract the information from the session:</p>
<!-- /wp:paragraph -->

<!-- wp:list {"ordered":true,"type":"1"} -->
<ol type="1"><li>Shredding the XML of the session data from the ring buffer target</li><li>Using&nbsp;<code>master.sys.fn_xe_file_target_read_file</code>&nbsp;to read the session data from a file target</li></ol>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>The first approach is extremely painful (XML shredding - enough said).</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The second approach requires a file target, which is not always available. It also requires to stop the session to read all the data, or write extremely complicated code to read the data incrementally while the session is running (believe me, I did it and my brain still hurts).</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This is where XESmartTarget jumps in to help you! All you have to do is write some configuration in a json file and let XESmartTarget do its magic.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>For this task you can use a&nbsp;<a href="https://github.com/spaghettidba/XESmartTarget/wiki/TableAppenderResponse">TableAppenderResponse</a>, that takes care of reading all the events from the session using the streaming API and write them to a target table, that can also be created automatically by XESmartTarget itself.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This time you can use a plain SQL script to create the session. It is going to capture rpc_completed and sql_batch_completed events, the same in a Profiler Standard trace.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Remember that you don’t need to set up any targets, it’s enough to add the events and start the session, like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS ( SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe02')

CREATE EVENT SESSION [Recipe02] ON SERVER 
ADD EVENT sqlserver.rpc_completed(
    ACTION(
        package0.event_sequence,
        sqlserver.client_app_name,
        sqlserver.client_pid,
        sqlserver.database_name,
        sqlserver.nt_username,
        sqlserver.query_hash,
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
        sqlserver.query_hash,
        sqlserver.server_principal_name,
        sqlserver.session_id
    )
    WHERE ([package0].[equal_boolean]([sqlserver].[is_system],(0)))
)
GO

IF NOT EXISTS ( SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe02')
    ALTER EVENT SESSION Recipe02 ON SERVER STATE = START;</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Now that the session is set up, you can use XESmartTarget to process the data. As you learned in the previous recipe, all you have to do is create a JSON file with configuration data, according to what <a href="https://github.com/spaghettidba/XESmartTarget/wiki/TableAppenderResponse">the documentation</a> says. This time, the JSON file looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript","highlightLines":"3,9,12"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe02",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "TableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_02_Queries",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "name", 
                    "collection_time", 
                    "client_app_name", 
                    "server_principal_name", 
                    "database_name",
                    "batch_text",
                    "statement"
                ],
                "Events": [
                    "rpc_completed",
                    "sql_batch_completed"
                ]
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>It is very similar to the one we had for CsvAppenderResponse, but there are some interesting things to note.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>First, you will notice that we have some placeholders that start with the dollar sign, like $ServerName. Those are <a href="https://github.com/spaghettidba/XESmartTarget/wiki#global-variables">Global Variables</a>, that allow you to reuse the same JSON file in multiple situations. You can provide the values for the Global variables from the command line of XESmartTarget, in the form --GlobalVariables key1=value1 key2=value2 … keyN=valueN</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In this example, you don’t have to create a new JSON file for every server that you connect to, but you can reuse the same file, by specifying the name of the server in the Global Variables.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Another thing worth noting is the AutoCreateTable property: it controls whether XESmartTarget will attempt to create the target table based on the columns specified in the OutputColumns property. XESmartTarget will try to guess the correct data types, but it will have no way to determine the maximum length for string columns, so they will be created as nvarchar(max). If you want a more precise data type definition, I suggest that you create the table manually and set this property to false.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>There is another property that controls the behaviour of the TableAppenderResponse, even if it does not appear in the configuration file above. UploadIntervalSeconds controls how often XESmartTarget uploads the data to the target table. The default is 10 seconds: if you're ok with that, you can omit it in the configuration file, otherwise you're free to set it to a different value. Between uploads, the data is held in memory, so make sure to reduce this interval when you have a lot of events captured by your session.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Save the JSON file as c:\temp\Recipe_02_Output_Table.json and you’re ready to invoke XESmartTarget. This time, the command line will need the server’s name specified as a Global Variable:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File c:\temp\Recipe_02_Output_Table.json --GlobalVariables ServerName=(local)\SQLEXPRESS</code></pre>
<!-- /wp:code -->

<!-- wp:image {"id":1580,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-7.png"><img src="/wp-content/uploads/2022/02/image-7.png" alt="" class="wp-image-1580" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The output will tell you when the target table has been created and will count the rows written by each upload. Let’s check the data in the database with a quick query:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1582,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-8.png"><img src="/wp-content/uploads/2022/02/image-8.png" alt="" class="wp-image-1582" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>How cool! The table has been created and the data is being written to it every 10 seconds. That's one thing that is not easy to achieve with the built-in targets!</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>You wanted to save all the commands executed on your SQL Server to a table in your database, so you configured XESmartTarget using the TableAppenderResponse. That was super easy, wasn’t it?</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next recipe you will learn how to manipulate the output further, using expression columns and event filters. Stay tuned!</p>
<!-- /wp:paragraph -->
