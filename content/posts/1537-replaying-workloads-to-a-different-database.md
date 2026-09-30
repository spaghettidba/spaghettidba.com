---
title: "Replaying Workloads to a different Database"
date: "2020-03-31T09:27:04"
slug: "replaying-workloads-to-a-different-database"
source_url: "http://spaghettidba.com/2020/03/31/replaying-workloads-to-a-different-database/"
url: "/2020/03/31/replaying-workloads-to-a-different-database/"
categories: ["SQL Server"]
tags: ["Replay", "WorkloadTools"]
---

<!-- wp:paragraph -->
<p>One of the features I was asked to implement for WorkloadTools is the ability to replay commands to a database name different from the one recorded in the source workload.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This is something that I had been planning to implement for a while and it totally makes sense. Usually, you have two identical environments for the workload capture and replay, both with the same databases. Sometimes it makes sense to have two different databases as the source and target for the workload, for some particular reasons: resources constraints, ease of testing and so on.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><a href="https://github.com/spaghettidba/WorkloadTools">WorkloadTools </a>now supports replaying commands to a different database, using the <code>DatabaseMap </code>property of the <code>ReplayConsumer</code>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><code>DatabaseMap </code>is a <code>Dictionary </code>of strings, so it can be expressed in the .json file as a key/value pair, where the key is the original database and the value is the new target database for the command.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Here is an example:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript","highlightLines":"9-12"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "__type": "ReplayConsumer",
    "ConnectionInfo": {
        "ServerName": "somedatabase.database.windows.net",
        "DatabaseName": "mario",
        "UserName": "itsame",
        "Password": "itsamario"
    },
    "DatabaseMap": {
        "Mario": "Luigi",
        "Peach": "Bowser"
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>In this case, whenever a command from the database "Mario" is found, it is replayed against the database "Luigi". Similarly, when the database "Peach" is found, the command gets replayed on "Bowser".</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Please note that <code>DatabaseMap </code>only changes the database context and does not substitute any reference to the original database name in the code. For instance, if you had something like <code>EXEC Mario.sys.sp_executesql 'SELECT 1'</code> ,this would not be intercepted by <code>DatabaseMap</code> and would remain unchanged in your code.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Happy benchmarking with WorkladTools!</p>
<!-- /wp:paragraph -->

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (8)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-33386" class="archived-comment"><article><header><strong>Tom</strong> <time datetime="2020-07-07T13:04:39Z">July 7, 2020 at 14:04</time></header><section class="archived-comment-content">It is possible to compare the responses too?<br><br>In the sense: i have a the DB on an SQL 2008 - Server and the same DB on an SQL 2017 server and do an action in the enduser-application that sends the SQL-queries to SQLworkload and from there to the 2 DBs. The DBs returns their data to SQLworkload. SQLworkload builds a checksum of the returned data and writes an error in the logfile if the checksums are different...</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-33387" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2020-07-07T13:30:17Z">July 7, 2020 at 14:30</time></header><section class="archived-comment-content">Sorry, this is not one of the abilities of SQLWorkload, nor this is one of the intended features. You could easily fork WorkloadTools and add the feature, but I'm not really planning to add anything like this to the toolset right now.</section></article></li><li id="wordpress-comment-33760" class="archived-comment"><article><header><strong>John Sterrett</strong> <time datetime="2020-08-27T15:39:08Z">August 27, 2020 at 16:39</time></header><section class="archived-comment-content">Awesome job on adding the feature to replay to a different named database. It's something that was on my wish list for Distributed Replay.  I need  to dedicate some time to try out your toolset.</section></article></li></ol></li><li id="wordpress-comment-33388" class="archived-comment"><article><header><strong>Tom</strong> <time datetime="2020-07-07T14:48:36Z">July 7, 2020 at 15:48</time></header><section class="archived-comment-content">Thanks for your quick response!<br>Unfortunately i am not a good coder, so i cannot enhance your great tool.<br><br>One day i will try your tool for performance comparision, thanks for your work!</section></article></li><li id="wordpress-comment-36006" class="archived-comment"><article><header><strong>KnoedelDBA</strong> <time datetime="2021-05-28T09:33:27Z">May 28, 2021 at 10:33</time></header><section class="archived-comment-content">Really a cool toolset!<br>How much costs a developer certificate?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-36007" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2021-05-28T09:38:14Z">May 28, 2021 at 10:38</time></header><section class="archived-comment-content">It's open source software, help yourself :)</section></article></li></ol></li><li id="wordpress-comment-38160" class="archived-comment"><article><header><strong>Na</strong> <time datetime="2021-12-31T14:30:57Z">December 31, 2021 at 15:30</time></header><section class="archived-comment-content">Everything was working fine until I got the following error when I reply the workload. Is there something I can change on JSON file or target Server to avoid this error. <br><br>error message<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [296] - Sequence[5324610] - Error: Execution Timeout Expired.  The timeout period elapsed prior to completion of the operation or the server is not responding.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-38208" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2022-01-01T22:41:24Z">January 1, 2022 at 23:41</time></header><section class="archived-comment-content">Hey there! This error indicates a query timeout. The statement that generated the timeout is the one found in the source SQLite file in the events table with sequence_id = 5324610<br>Hope this helps!</section></article></li></ol></li></ol></details>
</div>
