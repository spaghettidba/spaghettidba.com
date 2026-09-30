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
