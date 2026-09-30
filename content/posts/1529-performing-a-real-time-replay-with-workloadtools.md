---
title: "Performing a real-time replay with WorkloadTools"
date: "2020-03-03T18:50:00"
slug: "performing-a-real-time-replay-with-workloadtools"
source_url: "http://spaghettidba.com/2020/03/03/performing-a-real-time-replay-with-workloadtools/"
url: "/2020/03/03/performing-a-real-time-replay-with-workloadtools/"
categories: ["SQL Server"]
tags: ["Replay", "SQLServer", "WorkloadTools"]
---

<!-- wp:paragraph -->
<p>In a <a href="/2019/06/20/workload-replay-with-workloadtools/">previous blog post</a>, I showed you how to use <a href="https://github.com/spaghettidba/WorkloadTools/">WorkloadTools</a> to replay a workload in two different scenarios. However, there is a third scenario that is worth exploring: the real-time replay.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Before we jump to <em>how</em>, I’d better spend some words on <em>why</em> a real-time replay is needed.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The main reason is the complexity involved in capturing and analyzing a workload for extended periods of time. Especially when performing migrations and upgrades, it is crucial to capture the entire business cycle, in order to cover all possible queries issued by the applications. All existing benchmarking tools require to capture the workload to a file <strong>before</strong> it can be analyzed and/or replayed, but this becomes increasingly complicated when the length of the business cycle grows.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The first complication has to do with the size of the trace files, that will have to be accommodated to a disk location, either local or remote. It is not reasonable to expect to capture a workload on a busy server for, let’s say two weeks, because the size of the trace files can easily get to a few hundred GBs in less than one hour.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The second complication has to do with the ability of the benchmarking tools to process the trace files: bigger and more numerous files increase enormously the chances of breaking the tools. If you ever captured a big workload to a set of trace files to feed it to ReadTrace, you probably know what I’m talking about and chances are that you witnessed a crash or two. If you tried it with DReplay, you now probably have an ample collection of exotic and unhelpful error messages.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In this context, being able to process the events as soon as they occur is a plus, so that storing them to a file of any type is not needed. This is exactly what WorkloadTools does with the real-time replay feature.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Performing a real-time replay</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>All the considerations made for replaying a saved workload also apply to this scenario. First of all, you will need to set up a target environment that contains an up to date copy of the production database. Log shipping is a great tool for this: you can restore a full backup from production and restore all logs until the two databases are in sync. Immediately after restoring the last log backup with recovery, you can start the capture and replay on the production server.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The .json file for this activity will probably look like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Controller": {

        "Listener":
        {
            "__type": "ExtendedEventsWorkloadListener",
            "ConnectionInfo":
            {
                "ServerName": "SourceInstance"
            },
            "DatabaseFilter": "YourDatabase"
        },

        "Consumers":
        [
            {
                "__type": "ReplayConsumer",
                "ConnectionInfo": 
                {
                    "ServerName": "TargetInstance",
                    "DatabaseName": "YourDatabase"
               }
            },
            {
                "__type": "AnalysisConsumer",
                "ConnectionInfo": 
                {
                    "ServerName": "AnalysisInstance",
                    "DatabaseName": "SqlWorkload",
                    "SchemaName": "baseline"
                },
                "UploadIntervalSeconds": 60
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>On the target server, you can use SqlWorkload again to capture the performance data produced by the replay, using a .json file similar to the one used when analyzing the replay of a saved workload:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Controller": {
        "Listener":
        {
            "__type": "ExtendedEventsWorkloadListener",
            "ConnectionInfo":
            {
                "ServerName": "TargetInstance",
                "DatabaseName": "YourDatabase"
            }
        },

        "Consumers":
        [
            {
                "__type": "AnalysisConsumer",
                "ConnectionInfo": 
                {
                    "ServerName": "AnalysisInstance",
                    "DatabaseName": "SqlWorkload",
                    // different schema from SqlWorkload 1
                    "SchemaName": "replay"                 
                },
                "UploadIntervalSeconds": 60
            }
        ]
    }
}</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>The overall architecture of the real-time replay looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1533,"sizeSlug":"large"} -->
<figure class="wp-block-image size-large"><img src="/wp-content/uploads/2020/03/replay.png" alt="" class="wp-image-1533" /></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>It is crucial to start both instances of SqlWorkload at the same time, as the time dimension is always measured as the offset from the start of the analysis: starting both instances at the same time ensures that the same queries get executed around the same offset, so that you can compare apples to apples.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>It is also extremely important to make sure that the target environment can keep up with the workload being replayed, otherwise the number of queries found in the same interval will never match between the two environments and the two workloads will start to diverge more and more. You can observe the data in WorkloadViewer while is gets written by the two analysis consumers and you can compare the number of batches per seconds to make sure that the target environment does not get overwhelmed by the workload. To refresh the data in WorkloadViewer, simply press F5.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The analysis and comparison of a real-time replay is not different from a deferred replay and you can use the same tools and apply the same considerations to both situations.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The interesting part of a real-time replay is the ability to perform the replay for extended periods of time, without the need to store the workload data to any type of intermediate format and without the need to analyze the workload data as a whole before you can proceed with the replay. The possibilities that this approach opens are really interesting and can be outside the usual scope of benchmarking tools.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>As an example, you could decide to have a <em>staging environment</em> where you want to test the performance impact of new implementations directly against a <em>production workload</em>, gaining immediate insights regarding performance and catching runaway queries before they hit production. The traditional approach to this problem has always been based on test harnesses that simulate the critical parts of the workload, but building and maintaining these tools can be time consuming. With WorkloadTools you can measure the performance impact of your changes without having to build new tools and you can focus on what matters to you the most: <strong>your business.</strong></p>
<!-- /wp:paragraph -->

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (10)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-32938" class="archived-comment"><article><header><strong>martinpguth</strong> <time datetime="2020-04-28T13:17:32Z">April 28, 2020 at 14:17</time></header><section class="archived-comment-content">Interesting one! I am having a hard time on thinking how to get the starting point in an OLTP environment where data is constantly changing...here the production will always be ahead in terms of time and data volume.<br>For an OLAP scenario (data warehousing) with nightly batches however that seems to make more sense. I would be very interested in your experience on that or scenarios where you use it.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-32939" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2020-04-28T14:36:02Z">April 28, 2020 at 15:36</time></header><section class="archived-comment-content">Well, you don't want to use WorkloadTools to keep the databases in sync, but you can use log shipping and then start the replay when the two databases are in sync.</section></article></li></ol></li><li id="wordpress-comment-35140" class="archived-comment"><article><header><strong>Vlada</strong> <time datetime="2021-02-12T18:54:27Z">February 12, 2021 at 19:54</time></header><section class="archived-comment-content">Hi Gianluca,<br><br>I'm trying to replay workload (either recorded or a live one) and I'm having troubles with QueryTimeoutSeconds parameter. I've tried couple different options but I'm still getting query timeouts when executing a replay. <br>Can you please help me understand what am I missing here (I'm on a latest version)?<br><br>This is JSON I'm using for a live replay (I'm running a second one to capture stats for analysis on replay instance)<br><br>{<br>    "Controller": {<br> <br>        "Listener":<br>        {<br>            "__type": "ExtendedEventsWorkloadListener",<br>            "ConnectionInfo":<br>            {<br>                "ServerName": "PRD-TST-SQL11\\SQL2012"<br>            },<br>            "DatabaseFilter": "StackOverflow2013",<br>			"TimeoutMinutes": 10<br>        },<br> <br>        "Consumers":<br>        [<br>            {<br>                "__type": "ReplayConsumer",<br>                "ConnectionInfo": <br>                {<br>                    "ServerName": "PRD-TST-SQL12",<br>                    "DatabaseName": "StackOverflow2013"<br>               },<br>			   "QueryTimeoutSeconds": 300<br>            },<br>            {<br>                "__type": "AnalysisConsumer",<br>                "ConnectionInfo": <br>                {<br>                    "ServerName": "PRD-TST-SQL12",<br>                    "DatabaseName": "SqlWorkload",<br>                    "SchemaName": "baseline"<br>                },<br>                "UploadIntervalSeconds": 60,<br>				"DisplayWorkerStats": "true"<br>				<br>            }<br>        ]<br>    }<br>}<br><br>Thanks,<br>Vlada</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-35152" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2021-02-15T09:43:34Z">February 15, 2021 at 10:43</time></header><section class="archived-comment-content">Hi Vlada, what is the desired outcome and what is happening instead? Are the queries actually hitting a timeout or not? How can I help you?</section></article></li></ol></li><li id="wordpress-comment-44111" class="archived-comment"><article><header><strong>guyrodge</strong> <time datetime="2022-12-27T15:57:45Z">December 27, 2022 at 16:57</time></header><section class="archived-comment-content">Hello,<br>Many thanks for this work!<br>i am trying to view the workload with workloadviewer but nothing is displayed. Queries are there in the schema however No values about CPU or time have been recorded alongside. ( table [dbAdmin].[replayCompatLvl].[WorkloadDetails])<br>here is my json replay and the workloadviewer command :<br><br>{<br>    "Controller": {<br> <br>        "Listener":<br>        {<br>            "__type": "FileWorkloadListener",<br>            "Source": "E:\\data\\replayNotProcessOrdralfa.sqlite",<br>            // in this case you want to simulate the original query rate<br>            "SynchronizationMode": "true"<br>        },<br> <br>        "Consumers":<br>        [<br>            {<br>                "__type": "ReplayConsumer",<br>                "ConnectionInfo": <br>                {<br>                    "ServerName": "nas374"<br>                }<br>            },<br>            {<br>                "__type": "AnalysisConsumer",<br>                "ConnectionInfo": <br>                {<br>                    "ServerName": "nas374",<br>                    "DatabaseName": "dbAdmin",<br>                    "SchemaName": "replayCompatLvl02"<br>                },<br>                "UploadIntervalSeconds": 60<br>            }<br>        ]<br>    }<br>}<br><br>.\WorkloadViewer.exe --baseLineServer nas374 --baselineDatabase dbAdmin --BaselineSchema baseline --BaseLineUsername sa --BaselinePassword xxx</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-44130" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2022-12-28T18:42:58Z">December 28, 2022 at 19:42</time></header><section class="archived-comment-content">Hi, I don't understand what you mean with "No values about CPU or time have been recorded alongside". No rows in the table? No values in the columns?<br>However, if you perform replay and analysis on the same instance of sqlworkload you will get the analysis of the source workload that you feed to the replay consumer, not the analysis of the replayed workload.<br>Hope this helps<br>Gianluca</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-44137" class="archived-comment"><article><header><strong>guyrodge</strong> <time datetime="2022-12-29T07:41:10Z">December 29, 2022 at 08:41</time></header><section class="archived-comment-content">Hello, <br>thanks for your response that's probably the thing I would like to have :<br>Replaying a file workload and get an analysis of that replayed workload.<br>Is that something that can be done ?<br>GuyR</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-44142" class="archived-comment"><article><header><strong>Gianluca Sartori</strong> <time datetime="2022-12-29T17:33:05Z">December 29, 2022 at 18:33</time></header><section class="archived-comment-content">Sure! You can do that by having two separate instances of  sqlworkload.exe running at the same time, each with its own  configuration. The first one will take care of the replay, the second one will take  care of analyzing the queries performed on the target of the replay.  Follow the instructions you will find at this address:  /2019/06/20/workload-replay-with-workloadtools/<br><br>Hope this helps Gianluca</section></article></li></ol></li></ol></li></ol></li><li id="wordpress-comment-44207" class="archived-comment"><article><header><strong>guyrodge</strong> <time datetime="2023-01-05T17:54:18Z">January 5, 2023 at 18:54</time></header><section class="archived-comment-content">many thanks! great tools! I am impressed<br>indeed my error was to use the same listenner for the capture and the replay!<br>keep testing...</section></article></li><li id="wordpress-comment-44686" class="archived-comment"><article><header><strong>Fergus O'Neill</strong> <time datetime="2023-02-23T15:45:33Z">February 23, 2023 at 16:45</time></header><section class="archived-comment-content">I love the look of this, but I've run into a little difficulty.<br>I have a slightly different use-case, in that I'm using SQL Azure, and I have my workload from SQL Auditing, i.e. not captured directly with SqlWorkload.<br>Is it possible to convert SQL Audit logs to the SQLLite format expected?<br>I won't need to capture performance data when running the workload, I only need to run the commands.  (Performance analysis will come from Azure logs...)</section></article></li></ol></details>
</div>
