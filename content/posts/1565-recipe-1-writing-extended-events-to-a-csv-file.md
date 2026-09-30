---
title: "Recipe 1: Writing Extended Events to a CSV file"
date: "2022-02-22T14:00:00"
slug: "recipe-1-writing-extended-events-to-a-csv-file"
source_url: "http://spaghettidba.com/2022/02/22/recipe-1-writing-extended-events-to-a-csv-file/"
url: "/2022/02/22/recipe-1-writing-extended-events-to-a-csv-file/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Welcome to the first recipe of this Extended Events cookbook! You will find the first blog post of the series <a href="https://spaghettidba.com/10-dba-recipes-with-xesmarttarget/">here</a> and you can browse all recipes with the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recipes-what-are-the-ingredients">Recipes: what are the ingredients?</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Every recipe starts with a problem to solve and has three ingredients:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><li>A session to capture the events</li><li>A JSON configuration file for XESmartTarget to process the events</li><li>A client application to read the data produced by XESmartTarget</li></ul>
<!-- /wp:list -->

<!-- wp:heading {"level":1} -->
<h1 id="the-problem">The problem</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>In this case, imagine that you wanted to observe the commands executed on a SQL Server instance and save them to a file to process them later. Of course, Extended Events can do that with the built-in targets. However, when you write to a file target, the file has to reside on the disks of the SQL Server machine (well, actually, the file could be sitting on a file share writable by SQL Server or even on BLOB storage on Azure, but let’s keep it simple). How do you use the storage of the client machine instead of using the precious filesystem of the server machine?</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Here is where XESmartTarget can help you with a <a href="https://github.com/spaghettidba/XESmartTarget/wiki/CsvAppenderResponse">CsvAppenderResponse</a>. This Response type writes all the events it receives to a CSV file, that can be saved on the client machine, without wasting disk space on the server. You can decide which events to process and which columns to include in the CSV file, but more on that later.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>First of all, you need a session: how do you create it? I know what you’re thinking: “if this was a trace, I would know how to get it”. Right. Many DBAs are still using Traces, because Extended Events have not been very friendly to them. Profiler was super easy to use: start the program, connect, select a template, choose events and columns, start the trace and you see the data right away in the GUI. Extended Events can be a bit overwhelming because there are multiple concepts to get hold of: sessions, events, targets, fields, actions… Yeah, it’s the same old story: more power, more responsibility.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>It was not just you: everyone was confused by Extended Events when it first shipped with SQL Server 2012 (well, we had something in 2008, but it wasn’t really a replacement for traces until 2012).</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><a href="https://twitter.com/cl">Chrissy LeMaire</a> was just as confused as you, so she did what the giants do: she studied the topic in depth and not only she made it easier for herself, but she made it easier for everyone using <a href="https://dbatools.io/">dbatools</a>. If you don’t know what dbatools is, you really need to check it out: it’s a Powershell module that allows DBAs to perform all their day-to-day tasks on SQL Servers using powershell. Everything you can do with SSMS (and much more!) can be done with dbatools. Chrissy created a lot of <a href="https://dbatools.io/commands/#XE">dbatools commands to work with Extended Events</a> and now everything is much easier!</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>But is it really as easy as working with traces? With Profiler, you would have the Standard template and you would only need to click start. Can it be that simple with dbatools? Let’s find out.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>One of the great features that Chrissy added to dbatools is the ability to create a session from a template. She gathered a lot of useful session definitions from community blog posts, scripts, and templates from Microsoft tools, then she included those definitions in dbatools. It’s the same as in Profiler: all you have to do is select the appropriate template:</p>
<!-- /wp:paragraph -->

<!-- wp:preformatted -->
<pre class="wp-block-preformatted">Get-DbaXESessionTemplate | Out-GridView</pre>
<!-- /wp:preformatted -->

<!-- wp:image {"id":1567,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-2.png"><img src="/wp-content/uploads/2022/02/image-2.png" alt="" class="wp-image-1567" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>In this case you can use the "Profiler Standard" template and of course it’s there and you can do it with just a couple of lines of PowerShell:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>Import-DbaXESessionTemplate -SqlInstance "localhost\SQLEXPRESS" -Name "Recipe01" -Template "Profiler Standard"</code></pre>
<!-- /wp:code -->

<!-- wp:code -->
<pre class="wp-block-code"><code>Start-DbaXESession -Session "Recipe01" -SqlInstance " localhost\SQLEXPRESS"</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>That couldn’t be easier! Notice that the commands above did not add any targets to the session: the streaming API will take care of processing the data. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If you don't like dbatools or don't want to use powershell, the script for the session is this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS ( SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe01')

CREATE EVENT SESSION [Recipe01] ON SERVER 
ADD EVENT sqlserver.attention(
    ACTION(
		 package0.event_sequence
		,sqlserver.client_app_name
		,sqlserver.client_pid
		,sqlserver.database_id
		,sqlserver.nt_username
		,sqlserver.query_hash
		,sqlserver.server_principal_name
		,sqlserver.session_id
	)
    WHERE ([package0].[equal_boolean]([sqlserver].[is_system],(0)))
),
ADD EVENT sqlserver.existing_connection(
	SET collect_options_text=(1)
    ACTION(
		 package0.event_sequence
		,sqlserver.client_app_name
		,sqlserver.client_pid
		,sqlserver.nt_username
		,sqlserver.server_principal_name
		,sqlserver.session_id
	)
),
ADD EVENT sqlserver.login(
	SET collect_options_text=(1)
    ACTION(
		 package0.event_sequence
		,sqlserver.client_app_name
		,sqlserver.client_pid
		,sqlserver.nt_username
		,sqlserver.server_principal_name
		,sqlserver.session_id
	)
),
ADD EVENT sqlserver.logout(
    ACTION(
		 package0.event_sequence
		,sqlserver.client_app_name
		,sqlserver.client_pid
		,sqlserver.nt_username
		,sqlserver.server_principal_name
		,sqlserver.session_id
	)
),
ADD EVENT sqlserver.rpc_completed(
    ACTION(
		 package0.event_sequence
		,sqlserver.client_app_name
		,sqlserver.client_pid
		,sqlserver.database_id
		,sqlserver.nt_username
		,sqlserver.query_hash
		,sqlserver.server_principal_name
		,sqlserver.session_id
	)
    WHERE ([package0].[equal_boolean]([sqlserver].[is_system],(0)))
),
ADD EVENT sqlserver.sql_batch_completed(
    ACTION(
		 package0.event_sequence
		,sqlserver.client_app_name
		,sqlserver.client_pid
		,sqlserver.database_id
		,sqlserver.nt_username
		,sqlserver.query_hash
		,sqlserver.server_principal_name
		,sqlserver.session_id
	)
    WHERE ([package0].[equal_boolean]([sqlserver].[is_system],(0)))
),
ADD EVENT sqlserver.sql_batch_starting(
    ACTION(
		 package0.event_sequence
		,sqlserver.client_app_name
		,sqlserver.client_pid
		,sqlserver.database_id
		,sqlserver.nt_username
		,sqlserver.query_hash
		,sqlserver.server_principal_name
		,sqlserver.session_id
	)
    WHERE ([package0].[equal_boolean]([sqlserver].[is_system],(0)))
);

IF NOT EXISTS ( SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe01')
    ALTER EVENT SESSION Recipe01 ON SERVER STATE = START;
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Now that you have a session running you can work with the events it captures, using XESmartTarget.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The tool already ships with multiple Response types: all you have to do is prepare a configuration file. In this case you will use a <a href="https://github.com/spaghettidba/XESmartTarget/wiki/CsvAppenderResponse">CsvAppenderResponse</a>. If you go to the documentation page, you will see what properties are exposed by this Response type, which can be set in a JSON configuration file.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1568,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-3.png"><img src="/wp-content/uploads/2022/02/image-3.png" alt="" class="wp-image-1568" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>OK, let’s do it! Following the example on the documentation, you can craft your own JSON file to configure XESmartTarget:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "(local)\\SQLEXPRESS",
        "SessionName": "Recipe01",
        "Responses": [
            {
                "__type": "CsvAppenderResponse",
                "OutputFile": "c:\\temp\\output.csv",
                "OverWrite": "true",
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
<p>There are a couple of things to note on this file. First, it’s a JSON file, so it has to comply with the syntax of Javascript: backslash in strings has to be escaped with "\", so it becomes "\\". For each object in the "Responses" array, the property “__type” controls which Response type is used, then you can use its properties inside that block. For CsvAppenderResponse, the property “OutputColumns” controls which columns will be written to the CSV file. These columns are fields or actions from the events.<br>The property “Events” controls which events are processed by the current Response. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If your session captures multiple event types, you can choose which ones are processed by each Response, using the "Events" property. In this case, the profiler default template capture events that you don’t want to process, like existing connections, so you can filter for "rpc_completed" and "sql_batch_completed" events only.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Now, save the file as c:\temp\Recipe_01_Output_CSV.json and you can use it with XESmartTarget, by running this:</p>
<!-- /wp:paragraph -->

<!-- wp:preformatted -->
<pre class="wp-block-preformatted">"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File c:\temp\Recipe_01_Output_CSV.json</pre>
<!-- /wp:preformatted -->

<!-- wp:image {"id":1571,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-4.png"><img src="/wp-content/uploads/2022/02/image-4.png" alt="" class="wp-image-1571" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The output on the cmd window won’t tell you much, except that XESmartTarget is running, it’s connected to the appropriate session and the it’s writing to the CSV file.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Let’s check what happens if you run some commands from Azure Data Studio:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1572,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-5.png"><img src="/wp-content/uploads/2022/02/image-5.png" alt="" class="wp-image-1572" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The cmd window doesn’t say anything new, but if you open the CSV file with VSCode you will see that some data has been saved:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1573,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-6.png"><img src="/wp-content/uploads/2022/02/image-6.png" alt="" class="wp-image-1573" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>Code is great for inspecting CSV files, because it has the ability to reload the file when new rows are added and also has nice plugins like <a href="https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv">Rainbow CSV</a> to help you interpret the contents correctly. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>When you are finished with your capture, you can press CTRL+C on the cmd window where XESmartTarget is running and it will shut down.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>You wanted to save all the commands executed on your SQL Server to a CSV file on your computer. You had to set up a session for that, which was super easy, thanks to dbatools. Then you configured XESmartTarget to process all the events and save them to the CSV file of your choice. You could also watch the events flowing to the file in real-time, thanks to Code and its plugins.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In this recipe you familiarized with XESmartTarget and had a glimpse of its capabilities. The next recipe will introduce more capabilities and showcase more features of the JSON configuration format. Stay tuned!</p>
<!-- /wp:paragraph -->

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (2)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-45950" class="archived-comment"><article><header><strong>anon fremdly</strong> <time datetime="2024-07-09T13:50:10Z">July 9, 2024 at 14:50</time></header><section class="archived-comment-content"><br><p>Off topic -  thanks for your sqlbits presentation on SQL Server 2022 Time Series. Imo high on usability (lucid &amp; useful). It is getting me into this from older SQL Server.  </p><br></section></article><ol class="archived-comment-replies"><li id="wordpress-comment-45951" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2024-07-09T13:51:12Z">July 9, 2024 at 14:51</time></header><section class="archived-comment-content"><br><p>Always happy to help!</p><br></section></article></li></ol></li></ol></details>
</div>
