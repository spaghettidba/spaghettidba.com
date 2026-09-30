---
title: "Recipe 3: Merging and manipulating events"
date: "2022-02-24T14:00:00"
slug: "recipe-3-merging-and-manipulating-events"
source_url: "http://spaghettidba.com/2022/02/24/recipe-3-merging-and-manipulating-events/"
url: "/2022/02/24/recipe-3-merging-and-manipulating-events/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Welcome to the third recipe of this Extended Events cookbook! You will find the first blog post of the series <a href="https://spaghettidba.com/10-dba-recipes-with-xesmarttarget/">here</a> and you can browse all recipes with the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-problem">The problem</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>In the previous recipe, we wrote event data to a table in the database and each event used field and action names to map to the column names in the table. The same information (the text of the command) was stored in two separate columns, depending on the event type:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><li>batch_text for sql_batch_completed events</li><li>statement for rpc_completed events</li></ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>SSMS has a nice feature that allows you to create a merged column using data from several columns. Here is how you do it:</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>As you can see, the two even types are returning NULL for the columns that they don’t have:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1586,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-9.png"><img src="/wp-content/uploads/2022/02/image-9.png" alt="" class="wp-image-1586" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>You can create a merged column by right clicking the table header and clicking “Choose Columns”:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1588,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-10.png"><img src="/wp-content/uploads/2022/02/image-10.png" alt="" class="wp-image-1588" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>In the dialog you can click on “New” in the section for merged columns:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1589,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-11.png"><img src="/wp-content/uploads/2022/02/image-11.png" alt="" class="wp-image-1589" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>In the next dialog you can select which columns to merge. In this case you want to merge batch_text and statement:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1590,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-12.png"><img src="/wp-content/uploads/2022/02/image-12.png" alt="" class="wp-image-1590" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The result looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1591,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-13.png"><img src="/wp-content/uploads/2022/02/image-13.png" alt="" class="wp-image-1591" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>When the data is missing from one column, it is taken from the other column and the merged column always contain some data to show.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>It would be nice if I could do that with XESmartTarget as well, merging multiple columns before writing them to the target table. Turns out it is possible, with some work on the configuration file.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>First, we need a session. Since it is the same session as the one used for the second recipe, I will show you how you can recreate the same session with a different name (Recipe03) using the previous session as a template. Of course, I will use <a href="https://dbatools.io/">dbatools</a> for that.</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>Get-DbaXESession -SqlInstance "localhost\SQLEXPRESS" -Session Recipe02 |
    Export-DbaXESessionTemplate -Path C:\temp\xe |
    Import-DbaXESessionTemplate  -SqlInstance "localhost\SQLEXPRESS" -Name "Recipe03"
Start-DbaXESession -SqlInstance "localhost\SQLEXPRESS" -Session Recipe03
</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>It could not be easier! dbatools is the best! </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If you insist doing things the hard way, you can reuse the script from the first recipe and change the name of the session.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The configuration needs to be a bit more complex this time. The column “text” on the target table will have to receive data from different events, which have attributes with different names. To accomplish this, the configuration file will have to leverage two features: event filters and expression columns.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The first one is easy: you can decide which events gets processed by the Response using the “Events” attribute. I introduced this possibility in Recipe 1.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Expression columns use the same syntax as <a href="https://docs.microsoft.com/en-us/sql/relational-databases/tables/specify-computed-columns-in-a-table?view=sql-server-ver15">calculated columns in SQL Server</a>. To use an expression column in XESmartTarget, you can declare in the configuration file in the form column name = expression. This will allow you to calculate expressions, using fields and actions from the events as operands and all the functions and operators available in <a href="https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/dataset-datatable-dataview/creating-expression-columns">.NET DataTable objects</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In this case, the rpc_completed event will have to rename its “statement” column to “sql” and the sql_batch_completed event will have to rename its “batch_text” column to “sql”. While we’re at it, let’s also create a column “total_io” that contains logical_reads + writes. Let’s see how you can do it:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript","highlightLines":"19,20,23,38,39,42"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe03",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "TableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_03_Queries",
                "AutoCreateTargetTable": true,
                "OutputColumns": [
                    "name", 
                    "collection_time", 
                    "client_app_name", 
                    "server_principal_name", 
                    "database_name",
                    "sql AS statement",
                    "total_io AS logical_reads + writes"
                ],
                "Events": [
                    "rpc_completed"
                ]
            },
            {
                "__type": "TableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_03_Queries",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "name", 
                    "collection_time", 
                    "client_app_name", 
                    "server_principal_name", 
                    "database_name",
                    "sql AS batch_text",
                    "total_io AS logical_reads + writes"
                ],
                "Events": [
                    "sql_batch_completed"
                ]
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Besides filters and expressions, this JSON file also introduces the ability to process the events using multiple response objects, even of different types.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Let’s save this file as c:\temp\Recipe_03_Output_Table_Expressions.json and run XESmartTarget:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File c:\temp\Recipe_03_Output_Table_Expressions.json --GlobalVariables ServerName=(local)\SQLEXPRESS</code></pre>
<!-- /wp:code -->

<!-- wp:image {"id":1596,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-14.png"><img src="/wp-content/uploads/2022/02/image-14.png" alt="" class="wp-image-1596" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>As you can see from the output, XESmartTarget initializes two independent TableAppenderResponse objects and each one works on the events defined in the filter and outputs the columns defined in the OutputColumns property, including the expressions described above.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Querying the target table, you can see that the “sql” column contains data from both events, achieving the same result as the merged column in SSMS:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1597,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-15.png"><img src="/wp-content/uploads/2022/02/image-15.png" alt="" class="wp-image-1597" /></a></figure>
<!-- /wp:image -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Filters and Expression Columns allow you to achieve more complex results, like combining data from different fields or actions into a single column, or calculating expressions.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next recipe you will learn how to combine Responses of different types and use XESmartTarget to send email notifications when a particular event is captured. Keep an eye on the <a href="https://spaghettidba.com/tag/xesmarttarget">XESmartTarget tag</a> for the next recipes!</p>
<!-- /wp:paragraph -->

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (2)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-42569" class="archived-comment"><article><header><strong>Aditya Sawant</strong> <time datetime="2022-07-27T12:07:37Z">July 27, 2022 at 13:07</time></header><section class="archived-comment-content">Hi,<br><br>Than you the post it was really very helpful.<br><br>I am using <br><br>First Task: XESmartTarget to capture queries using high DOP on server and dumping them into table using TableAppenderResponse.<br><br>Also, <br>Second Task: I am using XESmartTarget to kill blocking on server.<br><br>The setup is working file the only problem I am facing is:<br><br>The first XESmartTarget  task which is used to capture high DOP queries executed for only 4 hr and then STOPs the XESmartTarget  <br><br>The Second XESmartTarget  task which is used to KILL blocking needs to run full time, but when the First task stops it also stops the second task.<br><br> PS: I use TASKKILL /F /IM "xesmarttarget.exe" /T to Stop the XESmartTarget  via .bat file<br><br>Unfortunately I am not able to  kill just First task and not both.<br><br>I can identify individual PID of  XESmartTarget.exe  but the First task is scheduled to execute 4hrs everyday and each time XESmartTarget.exe have different PID.<br><br>Can you help me to find out a way to kill XESmartTarget.exe of only first task and not the second task.</section></article></li><li id="wordpress-comment-42570" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2022-07-27T12:36:18Z">July 27, 2022 at 13:36</time></header><section class="archived-comment-content">I just published a possible solution for your problem: download the latest version (1.4.9) and use the --Timeout command line option to let XESmartTarget shut down after the timeout (in seconds) has expired.<br>Hope this helps!</section></article></li></ol></details>
</div>
