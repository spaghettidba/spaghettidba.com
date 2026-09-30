---
title: "Recipe 4: Sending Alerts via Email"
date: "2022-02-25T14:00:00"
slug: "recipe-4-sending-alerts-via-email"
source_url: "http://spaghettidba.com/2022/02/25/recipe-4-sending-alerts-via-email/"
url: "/2022/02/25/recipe-4-sending-alerts-via-email/"
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
<p>In the previous recipe, you learned how to combine multiple Responses together and how to control their output, using filters and Expression Columns. Armed with this knowledge, you can now tackle the most complex problems, using all the available Response types. In this post you learn how to notify when specific events occur, using the <a href="https://github.com/spaghettidba/XESmartTarget/wiki/EmailResponse">EmailResponse</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>One of the things that are missing from Extended Events is a mechanism for alerting. SQLTrace had Event Notifications (which is Service Broker on top of a trace), but Extended Events has nothing that comes close to it. No problem: XESmartTarget has your back again! You can use an <a href="https://github.com/spaghettidba/XESmartTarget/wiki/EmailResponse">EmailResponse</a> to send alerts whenever an interesting event is captured.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Of course, not all events need to be notified via email. Probably you shouldn’t be using email at all for notifications, but I digress…</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>One type of event that you may want to be notified of is the deadlock event. Deadlocks are bad and getting an email when one deadlock is captured is pretty reasonable. Let’s see how to do that with XESmartTarget.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Again, we need a session. This time the xml_deadlock_report event is the one that holds the information we are looking for. The script for the session is the following:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS ( SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe04')

CREATE EVENT SESSION [Recipe04] ON SERVER 
ADD EVENT sqlserver.xml_deadlock_report(
    ACTION(
        sqlserver.client_app_name,
        sqlserver.client_hostname,
        sqlserver.database_name,
        sqlserver.server_instance_name,
        sqlserver.server_principal_name,
        sqlserver.session_id
    )
)
GO


IF NOT EXISTS ( SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe04')
    ALTER EVENT SESSION Recipe04 ON SERVER STATE = START;</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The EmailResponse sends an email for each event it processes. In this example, the properties “Attachment” and “AttachmentFileName” can indicate which field or action from the event contains the data to attach and the name of the attached file. In this case, we are using the xml_report field and we are attaching it to the email message as “deadlock.xdl”, so that it can be associated with SSMS.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript","highlightLines":"14,15"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe04",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "EmailResponse",
                "SMTPServer": "localhost",
                "Sender": "demo@localhost",
                "To": "dba@localhost",
                "Subject": "Deadlock occurred",
                "Body": "Oh no! We got a deadlock!",
                "Attachment": "xml_report",
                "AttachmentFileName": "deadlock.xdl",
                "HTMLFormat": true,
                "Events": [
                    "xml_deadlock_report"
                ]
            },
            {
                "__type": "TableAppenderResponse",
                "ServerName": "$ServerName",
                "DatabaseName": "XERecipes",
                "TableName": "Recipe_04_Deadlocking",
                "AutoCreateTargetTable": false,
                "OutputColumns": [
                    "name", 
                    "collection_time", 
                    "client_app_name", 
                    "server_principal_name", 
                    "database_name",
                    "xml_report"
                ],
                "Events": [
                    "xml_deadlock_report"
                ]
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>At the same time, a Response of the type TableAppenderResponse takes care of saving the event to a table in the database, in order to obtain a log of the events and process them later.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Let’s save the file as c:\temp\Recipe_04_Alert_Email.json and run XESmartTarget:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>"%ProgramFiles%\XESmartTarget\xesmarttarget.exe" --File c:\temp\Recipe_04_Alert_Email.json --GlobalVariables ServerName=(local)\SQLEXPRESS</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>Again, XESmartTarget initializes two independent Response objects, this time of two different types: one TableAppenderResponse and one EmailResponse.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1608,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-16.png"><img src="/wp-content/uploads/2022/02/image-16.png" alt="" class="wp-image-1608" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The EmailResponse has been configured to use “localhost” as SMTP server, so I downloaded and installed a little nifty application that helps you test and troubleshoot email delivery: it’s called <a href="https://github.com/ChangemakerStudios/Papercut-SMTP">PaperCut SMTP</a> and it’s an absolute life saver! It incorporates the features of a SMTP server and an email client: it allows you to process email delivery as if it was a real SMTP server, but instead it saves the messages locally and displays them in a GUI similar to Outlook or a typical email client.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1609,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-17.png"><img src="/wp-content/uploads/2022/02/image-17.png" alt="" class="wp-image-1609" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>PaperCut displays all the emails generated by XESmartTarget, which also have an attachment named “deadlock.xdl”. If you download and open the file in SSMS, you will see a typical deadlock graph:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1610,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-18.png"><img src="/wp-content/uploads/2022/02/image-18.png" alt="" class="wp-image-1610" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>That’s pretty awesome if you ask me! The same can be done with other interesting events, like blocking or errors with high severity.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The EmailResponse object allows you to set up an alerting system based on Extended Events. All you have to do is set up a session that captures interesting events and then you can configure which events need to be notified and how.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next recipe you will learn how to execute T-SQL commands in response to specific events. Keep watching the <a href="https://spaghettidba.com/tag/xesmarttarget">XESmartTarget tag</a> for the next recipes!</p>
<!-- /wp:paragraph -->
