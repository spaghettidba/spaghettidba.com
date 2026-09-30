---
title: "10 DBA recipes with XESmartTarget"
date: "2022-02-21T10:00:00"
slug: "10-dba-recipes-with-xesmarttarget"
source_url: "http://spaghettidba.com/2022/02/21/10-dba-recipes-with-xesmarttarget/"
url: "/2022/02/21/10-dba-recipes-with-xesmarttarget/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Some time ago, I started a project called <a href="https://github.com/spaghettidba/XESmartTarget">XESmartTarget</a>. I find it super useful and you should probably know about it. It’s totally my fault if you’re not using it and I apologize for all the pain that it could have saved you, but it didn’t because I did not promote it enough.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Now I want to remedy my mistake with a 10 days series of blog posts on XESmartTarget, which will show you how useful it can be and how it can be used to accomplish your daily DBA tasks using Extended Events.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In this first post of the series, I will introduce XESmartTarget, show how it works and how to configure it. For the next 10 days I will publish a post to show you how to solve a specific problem using XESmartTarget. Let’s go!</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="what-is-xesmarttarget">What is XESmartTarget?</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>XESmartTarget is a small command line utility that can connect to an Extended Events session using the <a href="https://docs.microsoft.com/en-us/dotnet/api/microsoft.sqlserver.xevent.linq.queryablexeventdata?view=sqlserver-2016">streaming API</a> and can perform actions in response to the events captured by the session. The actions can vary from saving to a table in a database, writing to a CSV file, sending alerts and many more.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>You can think of XESmartTarget as a <strong><em>processing engine for Extended Events</em></strong>, that you can run from the command line, without having to write a single line of code.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="where-does-it-run">Where does it run?</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>XESmartTarget does not need to run on the server, it can run on any Windows machine that can connect to the target SQL Server instance. You can certainly run it on the server, but you don’t need to. XESmartTarget depends on Microsoft Visual C++ 2013 Redistributable: if you have the client utilities (SSMS) on your computer then you’re good to go, otherwise you can always <a href="https://www.microsoft.com/en-us/download/details.aspx?id=40784">download from Microsoft</a>. It doesn’t run on Linux, I’m sorry.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="how-do-i-get-it">How do I get it?</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>It’s open-source software: you can <a href="https://github.com/spaghettidba/XESmartTarget/releases/latest">download it from GitHub</a> and install it. You have a x64 setup kit and a x86 setup kit: make sure to pick the correct version for your operating system. Your browser may complain about it being unsafe, despite being signed with a code signing cert (sigh…). Don’t worry, go ahead and download it. Windows may also complain when running the .msi, so you will have to bypass SmartScreen as well. By default, the software gets installed to c:\Program Files\XESmartTarget</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="why-do-i-need-it">Why do I need it?</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The built-in targets for Extended Events are great, but they don’t cover 100% of the spectrum. Some targets, like writing to a database table, would be extremely useful but are not there. There are multiple reasons, but mainly this is because of performance concerns: Extended Events have been designed to be fast and have a low performance impact on the server being monitored. Writing to a file or to a memory buffer is a fast operation, writing to a table or applying additional logic can end up slowing down the collection process and the SQL Server instance. However, Microsoft decided to give us the ability to post-process the events in the .xel files or process the events in near real-time using the streaming API for Extended Events. XESmartTarget uses the streaming API to receive the events from the server and the API itself has a built-in protection mechanism that prevents the server from being chocked by the client: if the client can’t keep up with the data rate from the server, it gets disconnected.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Having an API to process events means that we can write code to perform common actions on the events. I created 7 types of Response classes, that can receive data from the events and process them to let you perform actions that you can’t perform using the built-in targets:</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><li><a href="https://github.com/spaghettidba/XESmartTarget/wiki/CsvAppenderResponse">CsvAppenderReponse</a> – writes event data to a CSV file</li><li><a href="https://github.com/spaghettidba/XESmartTarget/wiki/EmailResponse">EmailResponse</a> – sends alerts via email based on event data</li><li><a href="https://github.com/spaghettidba/XESmartTarget/wiki/ExecuteTSQLResponse">ExecuteTSQLResponse</a> – runs T-SQL commands for each event captured</li><li><a href="https://github.com/spaghettidba/XESmartTarget/wiki/TableAppenderResponse">TableAppenderReponse</a> – writes event data to a table in a SQL Server database</li><li><a href="https://github.com/spaghettidba/XESmartTarget/wiki/GroupedTableAppenderResponse">GroupedTableAppenderReponse</a> – aggregates event data in memory and then merges with existing data in the target table</li><li><a href="https://github.com/spaghettidba/XESmartTarget/wiki/ReplayResponse">ReplayResponse</a> – replays sql_batch_completed and rpc_completed events</li><li><a href="https://github.com/spaghettidba/XESmartTarget/wiki/GelfTcpResponse">GelfTcpResponse</a> – writes events to a GrayLog server</li><li><a href="https://github.com/spaghettidba/XESmartTarget/wiki/TelegrafAppenderResponse">TelegrafAppenderReponse</a> – writes to an InfluxDB database using Telegraf</li></ul>
<!-- /wp:list -->

<!-- wp:heading {"level":1} -->
<h1 id="will-i-have-to-write-code">Will I have to write code?</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>If you really, <em>really</em> want to write code, you can do it: XESmartTarget is a .dll library that you can incorporate in your project. That’s what we did with <a href="https://docs.dbatools.io/New-DbaXESmartTableWriter">dbatools</a>. The license is super permissive, so go ahead and do it!</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>However, one of the strengths of XESmartTarget is that it requires <strong>absolutely no coding</strong>: all you have to do is configure XESmartTarget to do what you want. It is a command line tool and it accepts some parameters:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>-F|--File &lt;path to the .JSON configuration file&gt;
        Uses the supplied .json file to configure the source of the events and the list of responses
-N|--NoLogo 
        Hides copyright banner at startup
-Q|--Quiet
        Suppresses output to console
-G|--GlobalVariables &lt;variable1=value1 variableN=valueN&gt;
        Replaces $variableN with valueN in configuration files
-L|--LogFile &lt;path to log file&gt;
        Writes the log to the file specified
</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>As you can see, you can use a .json file to provide the configuration. Not everyone likes JSON for configuration files, but I find it easy to use and good enough for the purpose. A nice addition to the standard JSON format is the ability to add comments using the javascript notation.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>A typical .json configuration file looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "server to monitor, where the session is running",
        "SessionName": "name of the session",
        "Responses": [
            {
                // Properties for Response1
            },
            {
                // Properties for ResponseN
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Each Response subclass has a set of public properties that can be set in the configuration file. You can visit the <a href="https://github.com/spaghettidba/XESmartTarget/wiki">documentation page</a> for each Response type to discover what are the properties available to you and see an example json file.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>For instance, <a href="https://github.com/spaghettidba/XESmartTarget/wiki/TableAppenderResponse">TableAppenderResponse</a> has some properties to set the target server/database/table for the events and you can set them like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "(local)\\SQLEXPRESS",
        "SessionName": "commands",
        "Responses": [
            {
                "__type": "TableAppenderResponse",
                "ServerName": "(local)\\SQLEXPRESS",
                "DatabaseName": "DBAStuff",
                "TableName": "queries",
                "AutoCreateTargetTable": true,
                "UploadIntervalSeconds": 10,
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
<p>Once you have your .json configuration file ready and your Extended Events session running, you can start XESmartTarget. It’s a command like tool, so it won’t show any GUI, but it will print messages to the console or to the log file to indicate that it’s doing some work.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>As an example, you can save the above as c:\temp\capture_commands.json and run it with this command line:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>“C:\program files\xesmarttarget\xesmarttarget.exe” --File c:\temp\capture_commands.json</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>You will see something similar to this:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1560,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image.png"><img src="/wp-content/uploads/2022/02/image.png" alt="" class="wp-image-1560" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>If you look in your database, you will see some rows in the target table:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1561,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-1.png"><img src="/wp-content/uploads/2022/02/image-1.png" alt="" class="wp-image-1561" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>If you want to stop XESmartTarget, you can press CTRL+C.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="what-else-can-it-do">What else can it do?</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The sky is the limit. In the next posts of this series, I will demonstrate how to accomplish typical DBA tasks using XESmartTarget and you will learn how to use the appropriate Response type for every need. You will also see how to unleash the most advanced features of the configuration files, to filter events, group and summarize data, use fields and actions as parameters and more.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Keep an eye on the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>!</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1>Where are my recipes?</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>There you go:</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><a href="/2022/02/22/recipe-1-writing-extended-events-to-a-csv-file/">/2022/02/22/recipe-1-writing-extended-events-to-a-csv-file/</a><br><a href="/2022/02/23/recipe-2-writing-extended-events-to-a-table/">/2022/02/23/recipe-2-writing-extended-events-to-a-table/</a><br><a href="/2022/02/24/recipe-3-merging-and-manipulating-events/">/2022/02/24/recipe-3-merging-and-manipulating-events/</a><br><a href="/2022/02/25/recipe-4-sending-alerts-via-email/">/2022/02/25/recipe-4-sending-alerts-via-email/</a><br><a href="/2022/02/28/recipe-5-killing-blocking-spids/">/2022/02/28/recipe-5-killing-blocking-spids/</a><br><a href="/2022/02/28/recipe-6-auditing-successful-logins/">/2022/02/28/recipe-6-auditing-successful-logins/</a><br><a href="/2022/03/01/recipe-7-finding-unused-tables/">/2022/03/01/recipe-7-finding-unused-tables/</a><br><a href="/2022/03/02/recipe-8-analyzing-a-workload/">/2022/03/02/recipe-8-analyzing-a-workload/</a><br><a href="/2022/03/03/recipe-9-capturing-queries-and-plans/">/2022/03/03/recipe-9-capturing-queries-and-plans/</a><br><a href="/2022/03/04/recipe-10-writing-events-to-influxdb/">/2022/03/04/recipe-10-writing-events-to-influxdb/</a></p>
<!-- /wp:paragraph -->
