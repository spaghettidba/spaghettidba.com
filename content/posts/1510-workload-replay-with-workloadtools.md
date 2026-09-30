---
title: "Workload replay with WorkloadTools"
date: "2019-06-20T16:01:28"
slug: "workload-replay-with-workloadtools"
source_url: "http://spaghettidba.com/2019/06/20/workload-replay-with-workloadtools/"
url: "/2019/06/20/workload-replay-with-workloadtools/"
categories: ["SQL Server"]
tags: ["Replay", "WorkloadTools"]
---

<!-- wp:paragraph -->
<p>In <a href="/2019/03/12/capturing-a-workload-with-workloadtools/">my
last post</a>, I described how to capture a workload to a file, in order to run
a replay against your target environment at a later time. Well, that later time
has come and you’re ready to roll.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Of course, WorkloadTools has got you covered.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Before I show you how SqlWorkload can run the replay,
reading all data from the workload file, I need to spend some time describing
how to set up your target environment. It may look superfluous, but getting
this part right is they key to a successful benchmarking activity and allows
you to make sure that you are comparing apples with apples.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Choosing a methodology</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>First of all, you need to decide what you want to discover
and make sure you understand entirely how performing the replay will help you
in your investigation. There are mainly two types of methodologies:</p>
<!-- /wp:paragraph -->

<!-- wp:list {"ordered":true} -->
<ol><li>Capture in production, analyze the workload,
replay in test, analyze and compare the results</li><li>Capture in production, replay and analyze in
test to establish a baseline, change something and replay again in test to
obtain a second benchmark, then compare the results</li></ol>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>The first method is useful when you are interested in
comparing two different scenarios that cannot be easily reproduced in a test
environment. As an example of this situation, imagine a production server that
sits on a SAN storage with no more space available to create a test
environment. Management wants to buy a new SAN and obtains a box to conduct a
POC. In this case you can set up a test environment on the new SAN and compare
the benchmarks on the two different storages.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This way of benchmarking is not always ideal, because it
tries to compare a workload captured in production with a workload captured as
the replay of the production one. The two are not the same: they depend on the
filters applied while capturing in production and can be affected by the
conditions under which the replay is being performed. For this reason, this
methodology should be used only when it is possible to accept the approximation
due to resource constraints.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The second method is more convoluted, but it is often able
to deliver more accurate results. With this method, both benchmarks are
obtained by measuring the replay of the original workload in a controlled test
environment, so that the way the replay itself is performed does not affect the
comparison.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This second method is easier to use in situations when the
test environment can be reused to obtain the two scenarios to measure. Imagine
that you want to observe the effect of changing compatibility level or some
other database level options: in this case you would need to replay the
original workload, change compatibility level, run a second replay and compare
the performance in the two scenarios.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>However, not even this method is perfect and you really need
to make sure that you understand what you want to measure. If you are looking
for plan regressions due to changing something at the instance, database or
object level, you probably don’t care much about the relative performance of
the hardware, because it is unlikely to affect query performance more than the
plan regression itself.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Setting up the environment</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Another thing that has to be taken into account is what data
the replay will be performed against. In order to obtain meaningful performance
information, the workload should ideally be performed against the same
database, with the data in the same exact state in both environments.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Working on data in different states can produce misleading
results. Imagine that the production workload contains thousands of commands
that operate changes to a particular order in a database for an e-commerce
website: if you tried to replay that workload against a copy of the database
taken one week before the order was created, you would not produce the same
amount of reads and writes found in the production workload. This means that
the two databases have to be synchronized, by performing a point int time
restore in the test environment up to the moment in which the capture of the
production workload has started.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If you have to replay the workload multiple times, it is
recommended to take a database snapshot before you start the replay, so that
you can revert to that snapshot before repeating the replay.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Replaying a Workload from production</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>In this case, the workload that you capture in production
will act as the baseline and will be compared to the workload captured in test
when performing the replay.

WorkloadTools lets you choose when to analyze
the source workload: you can do that during the workload capture, you can do
that while performing the replay or you can do that at a later moment. In the
first case, you just need to add a second consumer to the listener and let it
write the performance data to a schema in the analysis database. 



</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"java"} -->
<pre class="wp-block-syntaxhighlighter-code brush: java; notranslate">{
    "Controller": {

        // This listener connects to the source instance
        // using Extended Events
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
            // This consumer analyzes the workload and saves
            // the analysis to a database, in the schema “baseline”
            {
                "__type": "AnalysisConsumer",
                "ConnectionInfo": 
                {
                    "ServerName": "AnalysisInstance",
                    "DatabaseName": "SqlWorkload",
                    "SchemaName": "baseline"
                },
                "UploadIntervalSeconds": 60
            },
            // This consumer writes the workload to a file
            {
                "__type": "WorkloadFileWriterConsumer",
                "OutputFile": "C:\\temp\\SqlWorkload.sqlite"
            }
        ]
    }
}
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>If you decide to analyze the workload later, you can start a
file listener and feed the events to an analysis consumer. This setup can come
handy when the analysis database is not reachable from the machine where the
capture is being performed. This is an example of how to perform the analysis
using a workload file as the source:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"java"} -->
<pre class="wp-block-syntaxhighlighter-code brush: java; notranslate">{
    "Controller": {

        "Listener":
        {
            "__type": "FileWorkloadListener",
            "Source": "C:\\temp\\SqlWorkload.sqlite",
            "SynchronizationMode": "false"
        },

        "Consumers":
        [
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
<p>Another option is to analyze the source workload while performing the replay. Here is a sample json file for that:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"java"} -->
<pre class="wp-block-syntaxhighlighter-code brush: java; notranslate">{
    "Controller": {

        "Listener":
        {
            "__type": "FileWorkloadListener",
            "Source": "C:\\temp\\SqlWorkload.sqlite",
            // in this case you want to simulate the original query rate
            "SynchronizationMode": "true" 
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
}
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>The replay workload has to be captured and analyzed as well,
but you don’t need to record the queries to a workload file, because you are
only after the performance data and you don’t need to replay the queries captured
in this environment. All you need in this case is an instance of SqlWorkload
with a listener connected to the test environment and a consumer to perform the
analysis.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"java"} -->
<pre class="wp-block-syntaxhighlighter-code brush: java; notranslate">{
    "Controller": {

        // This listener points to the target instance
        // where the replay is being performed
        "Listener":
        {
            "__type": "ExtendedEventsWorkloadListener",
            "ConnectionInfo":
            {
                "ServerName": "TargetInstance",
                "DatabaseName": "DS3"
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
                    "SchemaName": "replay"
                },
                "UploadIntervalSeconds": 60
            }
        ]
    }
}
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>The analysis data can be saved to the same target database
used for the production workload, but it is not a requirement. In case you
decide to use the same database, the target schema needs to be different.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Recording multiple benchmarks for the same workload</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>In this case, the workload captured in production will not
be used as the baseline, but the baseline will be obtained by replaying it.
This means that you don’t need to analyze the source workload and all you need
to do is record it to a file. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Pointing to the target environment, you will need an
instance of SqlWorkload with a listener configured to read the workload file
and replay the events using a replay consumer. </p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"java"} -->
<pre class="wp-block-syntaxhighlighter-code brush: java; notranslate">{
    "Controller": {

        "Listener":
        {
            "__type": "FileWorkloadListener",
            "Source": "C:\\temp\\SqlWorkload.sqlite",
            // in this case you want to simulate the original query rate
            "SynchronizationMode": "true" 
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
            }
        ]
    }
}
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>In the same environment, you will have another instance of
SqlWorkload with a listener capturing the events being replayed and an analysis
consumer to write the performance data to an analysis database. </p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"java"} -->
<pre class="wp-block-syntaxhighlighter-code brush: java; notranslate">{
    "Controller": {

        // This listener points to the target instance
        // where the replay is being performed
        "Listener":
        {
            "__type": "ExtendedEventsWorkloadListener",
            "ConnectionInfo":
            {
                "ServerName": "TargetInstance",
                "DatabaseName": "DS3"
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
                    "SchemaName": "benchmark01"
                },
                "UploadIntervalSeconds": 60
            }
        ]
    }
}
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>

















In
order to obtain the second benchmark, you will now need to rewind the database
to its initial state by performing a restore (using backups or a snapshot) and
then you are ready to perform replay and capture once again. The .json files to
use are almost identical to the ones that you used to obtain the first
benchmark, except that you will need to specify a different schema to save the
workload analysis.



</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"java"} -->
<pre class="wp-block-syntaxhighlighter-code brush: java; notranslate">{
    "Controller": {

        // This listener points to the target instance
        // where the replay is being performed
        "Listener":
        {
            "__type": "ExtendedEventsWorkloadListener",
            "ConnectionInfo":
            {
                "ServerName": "TargetInstance",
                "DatabaseName": "DS3"
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
                    "SchemaName": "benchmark02"
                },
                "UploadIntervalSeconds": 60
            }
        ]
    }
}
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:heading -->
<h2>Comparing benchmarks using WorkloadViewer</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Regardless of the method that you decided to use, at the end
of the replays, you will have two distinct sets of tables containing the
workload analysis data, sitting in different schemas in the same database or in
completely different databases.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>WorkloadViewer will let you visualize performance over time,
as we have seen for a single workload analysis, but this time it will be able
to show you data from both workloads, so that you can compare them.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The first tab will still contain the charts for total
duration, cpu and number of batches per second, with two different series:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1511} -->
<figure class="wp-block-image"><img src="/wp-content/uploads/2019/06/compare.png" alt="" class="wp-image-1511" /></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The grid in the second tab will now show performance data by
query for both benchmarks, so that you can easily spot regressions sorting by
the difference:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1512} -->
<figure class="wp-block-image"><img src="/wp-content/uploads/2019/06/queries.png" alt="" class="wp-image-1512" /></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>The third tab will show you the details for a single query,
with the detail broken down by application, hostname, username and
databasename. It will also contain a chart to show you the behavior of the
query over time.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1513} -->
<figure class="wp-block-image"><img src="/wp-content/uploads/2019/06/details.png" alt="" class="wp-image-1513" /></figure>
<!-- /wp:image -->

<!-- wp:heading -->
<h2>Conclusions</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Even when replaying a workload, WorkloadTools keep the
promise of low complexity and allow you to perform all the activities involved
in your benchmarking scenarios.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In the next post I will show you how to leverage the most
interesting feature of WorkloadTools: the real-time replay. Stay tuned!</p>
<!-- /wp:paragraph -->

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (22)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-28956" class="archived-comment"><article><header><strong>Terje Dahle</strong> <time datetime="2019-06-24T11:35:16Z">June 24, 2019 at 12:35</time></header><section class="archived-comment-content">Hi, I tryed following your example in "Recording multiple benchmarks for the same workload",<br>but the instance of SqlWorkLoad recording the Replay consumer stops with the following error after it is succsefully started:<br><br>Info - SqlWorkload.Program : SqlWorkload, Version=1.2.14.0, Culture=neutral, PublicKeyToken=null 1.2.14<br>Info - SqlWorkload.Program : Reading configuration from 'c:\DBA\WorkloadTools\RecordReplay_Kasper_Bechmark01.json'<br>Info - WorkloadTools.Listener.ExtendedEvents.ExtendedEventsWorkloadListener : Reading Extended Events session definition from C:\Program Files\WorkloadTools\Listener\ExtendedEvents\sqlworkload.sql<br>Info - WorkloadTools.WorkloadController : Listener of type ExtendedEventsWorkloadListener initialized correctly. Waiting for events.<br>Error - WorkloadTools.Listener.ExtendedEvents.StreamXEventDataReader : Error converting XE data from the stream: Unable to cast object of type 'System.Int32' to type 'System.String'.<br>Error - WorkloadTools.Listener.ExtendedEvents.StreamXEventDataReader :     event type            : Error<br>Error - WorkloadTools.Listener.ExtendedEvents.StreamXEventDataReader :     client_app_name       : WorkloadTools-ReplayWorker<br>Error - WorkloadTools.Listener.ExtendedEvents.StreamXEventDataReader :     database_name         : KASPER_CLONE_ted<br>Error - WorkloadTools.Listener.ExtendedEvents.StreamXEventDataReader :     client_hostname       : SQL77<br>Error - WorkloadTools.Listener.ExtendedEvents.StreamXEventDataReader :     server_principal_name : SPK\teda<br>Error - WorkloadTools.Listener.ExtendedEvents.StreamXEventDataReader :     session_id            : 278<br>Error - WorkloadTools.Listener.ExtendedEvents.ExtendedEventsWorkloadListener : Unable to cast object of type 'System.Int32' to type 'System.String'.<br>Error - WorkloadTools.Listener.ExtendedEvents.ExtendedEventsWorkloadListener :    at WorkloadTools.Listener.ExtendedEvents.StreamXEventDataReader.ReadEvents() in C:\GitHub\WorkloadTools\WorkloadTools\Listener\ExtendedEvents\StreamXEventDataReader.cs:line 198<br>   at WorkloadTools.Listener.ExtendedEvents.ExtendedEventsWorkloadListener.ReadEvents() in C:\GitHub\WorkloadTools\WorkloadTools\Listener\ExtendedEvents\ExtendedEventsWorkloadListener.cs:line 251<br>Info - WorkloadTools.Listener.ExtendedEvents.ExtendedEventsWorkloadListener : Extended Events session [sqlworkload] stopped successfully.<br><br><br>What shall i do, i have the same json files as you, just different values.?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-29084" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-07-01T22:42:31Z">July 1, 2019 at 23:42</time></header><section class="archived-comment-content">Hi, sorry for the delay. Would you mind sharing your sqlite file? Do you think it is possible?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-29415" class="archived-comment"><article><header><strong>Terje Dahle</strong> <time datetime="2019-07-29T11:02:48Z">July 29, 2019 at 12:02</time></header><section class="archived-comment-content">Hi, the sqllite file is 274 MB big, how do you want to receive it?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-29425" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-07-30T06:17:48Z">July 30, 2019 at 07:17</time></header><section class="archived-comment-content">Put it somewhere on a cloud drive and send the link to spaghettidba at sqlconsulting dot it. If you compress the file it will shrink significantly</section></article></li></ol></li></ol></li></ol></li><li id="wordpress-comment-29485" class="archived-comment"><article><header><strong>John McCormack</strong> <time datetime="2019-08-07T13:28:29Z">August 7, 2019 at 14:28</time></header><section class="archived-comment-content">Hi Gianluca - How did you get on with this? <br><br>I am also getting the same error. I am using your latest version 1.3.1 using ExtendedEventsWorkloadListener to replay and capture the baseline and benchmark to the same DB but different schemas.<br><br>Error - WorkloadTools.Listener.ExtendedEvents.ExtendedEventsWorkloadListener : Unable to cast object of type 'System.Int32' to type 'System.String</section></article></li><li id="wordpress-comment-29486" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-08-07T14:25:20Z">August 7, 2019 at 15:25</time></header><section class="archived-comment-content">Hi John, please try version 1.3.3, freshly released :) Hope this works for you!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-29487" class="archived-comment"><article><header><strong>John McCormack</strong> <time datetime="2019-08-07T14:48:15Z">August 7, 2019 at 15:48</time></header><section class="archived-comment-content">Thanks for such a quick reply. I will report back tomorrow. <br>In the meantime, I worked around by using SqlTraceWorkloadListener for analysing the benchmark.</section></article></li></ol></li><li id="wordpress-comment-29526" class="archived-comment"><article><header><strong>Sami Kukkonen</strong> <time datetime="2019-08-14T18:08:37Z">August 14, 2019 at 19:08</time></header><section class="archived-comment-content">I have a 50 MB .trc file that I captured earlier.<br><br>When I use ConvertWorkLoad to convert it, nothing happens. I can see it reading disk and consuming some CPU and then nothing happens, there is no output. The file log only has this:<br><br>Info - ConvertWorkload.Program : ConvertWorkload, Version=1.3.3.0, Culture=neutral, PublicKeyToken=null 1.3.3<br>Info - WorkloadTools.Listener.Trace.TraceFileWrapper : SMO Version: Microsoft.SqlServer.ConnectionInfoExtended, Version=14.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-29527" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-08-14T18:12:23Z">August 14, 2019 at 19:12</time></header><section class="archived-comment-content">What's the command line you used? Can you share the input file?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-29536" class="archived-comment"><article><header><strong>Sami Kukkonen</strong> <time datetime="2019-08-15T17:01:00Z">August 15, 2019 at 18:01</time></header><section class="archived-comment-content">Alas, the trace contains sensitive information. I made another trace and the same thing happens, it does read the input data but writes nothing.<br><br>"C:\Program Files\WorkloadTools\ConvertWorkload.exe"  -I Z:\tracefiles\prod-tracing\2019-08-12\2019-08-12-production.trc -O Z:\tracefiles\prod-tracing\2019-08-12-production.sqlite -L convert_log.txt</section></article></li></ol></li><li id="wordpress-comment-32142" class="archived-comment"><article><header><strong>MarianC</strong> <time datetime="2020-01-15T12:33:42Z">January 15, 2020 at 13:33</time></header><section class="archived-comment-content">The same problem with version 1.3.4, nothing happen with conversion of a .trc file.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-32144" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2020-01-15T13:34:35Z">January 15, 2020 at 14:34</time></header><section class="archived-comment-content">You're right. Microsoft killed this feature when it started shipping trace DLLs with SMO and now the new versions of SMO do not support reading / writing trace files. I'm working on a fix, but it is going to take time, I'm sorry.</section></article></li></ol></li></ol></li><li id="wordpress-comment-30346" class="archived-comment"><article><header><strong>Frank Willshire</strong> <time datetime="2019-09-18T19:24:12Z">September 18, 2019 at 20:24</time></header><section class="archived-comment-content">Can you advise how to correctly replay a saved workload (sqlite file) and replay it against a target environment?  <br><br>When I follow the examples on how to set the json files for setting up a ReplayConsumer and AnalysisConsumer, the final WorkloadViewer always shows the exact same CPU and duration information?  <br><br>Here are my 2 json file settings for recording a baseline and replaying on a target server.<br><br>{<br>  "Controller": {<br><br>    "Listener": {<br>      "__type": "ExtendedEventsWorkloadListener",<br>      "ConnectionInfo": {<br>        "ServerName": "BaseLineServer",<br>        "UserName": "BaseLineAdmin",<br>        "Password": "BaseLinePassword"<br>      },<br>      "DatabaseFilter": "DATABASENAME"<br>    },<br><br>    "Consumers": [<br>      // This consumer analyzes the workload and saves<br>      // the analysis to a database, in the schema “baseline”<br>      {<br>        "__type": "AnalysisConsumer",<br>        "ConnectionInfo": {<br>          "ServerName": "ANALYSISSERVER",<br>          "DatabaseName": "DATABASENAME",<br>          "SchemaName": "baseline",<br>          "UserName": "AnalysisServerAdmin",<br>          "Password": "AnalysisServerPassword"<br>        },<br>        "UploadIntervalSeconds": 60<br>      },<br>      // This consumer writes the workload to a file<br>      {<br>        "__type": "WorkloadFileWriterConsumer",<br>        "OutputFile": "C:\\temp\\SqlWorkload.sqlite"<br>      }<br>    ]<br>  }<br>}<br><br><br>Replay json<br><br>{<br>    "Controller": {<br><br>      "Listener":<br>      {<br>        "__type": "FileWorkloadListener",<br>        "Source": "C:\\temp\\SqlWorkload.sqlite",<br>        "SynchronizationMode": "true"<br>      },<br><br>      "Consumers": [<br>        {<br>            "__type": "ReplayConsumer",<br>            "ConnectionInfo":<br>            {<br>                "ServerName": "TARGETSERVER",<br>                "DatabaseName": "DATABASENAME",<br>                "UserName": "TargetServerAdmin",<br>                "Password": "TargetServerPassword"<br>            }<br>        },<br>        {<br>            "__type": "AnalysisConsumer",<br>          "ConnectionInfo": {<br>            "ServerName": "ANALYSISSERVER",<br>          "DatabaseName": "DATABASENAME",<br>          "SchemaName": "replay",<br>          "UserName": "AnalysisServerAdmin",<br>          "Password": "AnalysisServerPassword"<br>          },<br>            "UploadIntervalSeconds": 60<br>        }<br>        <br>      ]<br>    }<br>}</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-30347" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-09-18T19:34:00Z">September 18, 2019 at 20:34</time></header><section class="archived-comment-content">The issue is how you set up the replay. You need to have two json files for the replay: one takes care of the replay itself and one takes care of analyzing the replayed events in the target server. Follow the examples and you should be fine. In case you get in trouble shoot me an email</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-30348" class="archived-comment"><article><header><strong>Frank Willshire</strong> <time datetime="2019-09-18T20:19:19Z">September 18, 2019 at 21:19</time></header><section class="archived-comment-content">OK, I think I understand.  But for a replay, am I running those 2 json files as command line parameters for 1 instance of the SqlWorkload project like this the following? <br><br>--File appsettingsReplayOne.json appsettingsReplayTwo.json<br><br>Or am trying to run 2 different instances of the the SqlWorkLoad project at the same time each with it's own --File command line json parameters?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-30349" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-09-18T20:53:44Z">September 18, 2019 at 21:53</time></header><section class="archived-comment-content">You need to run to separate instances of sqlworkload, each with its own json file</section></article></li></ol></li><li id="wordpress-comment-30353" class="archived-comment"><article><header><strong>Frank Willshire</strong> <time datetime="2019-09-19T15:14:48Z">September 19, 2019 at 16:14</time></header><section class="archived-comment-content">Great!  Thank you. I have it working now.</section></article></li></ol></li></ol></li><li id="wordpress-comment-36632" class="archived-comment"><article><header><strong>Dave</strong> <time datetime="2021-09-07T14:17:27Z">September 7, 2021 at 15:17</time></header><section class="archived-comment-content">When I run the replay JSON file, how I am going to determine the all events are applied on the target server. It shows starting but didn't say complete. I have attached my JSON file for your reference. <br>{<br>    "Controller": {<br> <br>        "Listener":<br>        {<br>            "__type": "FileWorkloadListener",<br>            "Source": "C:\\temp\\SqlWorkload.sqlite",<br>            "SynchronizationMode": "true"<br>        },<br> <br>        "Consumers":<br>        [<br>            {<br>                "__type": "ReplayConsumer",<br>                "ConnectionInfo": <br>                {<br>                    "ServerName": "targetserver",<br>                    "DatabaseName": "targetDB",<br>                    "UserName": "user",<br>                    "Password": "password"<br>                }<br>            }<br>        ]<br>    }<br>}<br><br>CMD output:<br><br>C:\Program Files\WorkloadTools&gt; "SqlWorkload.exe" --File "Replay.json"<br>Info - SqlWorkload.Program : SqlWorkload, Version=1.5.14.0, Culture=neutral, PublicKeyToken=null 1.5.14<br>Info - SqlWorkload.Program : Reading configuration from 'C:\Program Files\WorkloadTools\Replay.json'<br>Info - WorkloadTools.Listener.File.FileWorkloadListener : The source file contains 44 events.<br>Info - WorkloadTools.WorkloadController : Listener of type FileWorkloadListener initialized correctly. Waiting for events.<br>Info - WorkloadTools.Consumer.Replay.ReplayConsumer : Worker [502] - Starting<br>Info - WorkloadTools.Consumer.Replay.ReplayConsumer : Worker [246] - Starting</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-36633" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2021-09-07T14:22:58Z">September 7, 2021 at 15:22</time></header><section class="archived-comment-content">I am sorry it didn't work as expected. I would need to have more info in order to answer your question. Probably I would also need to have a look at what you have in your .sqlite file.</section></article></li></ol></li><li id="wordpress-comment-39350" class="archived-comment"><article><header><strong>Jose Navarro</strong> <time datetime="2022-03-03T01:22:47Z">March 3, 2022 at 02:22</time></header><section class="archived-comment-content">Hi! I am trying to do a replay from a sql lite file that I captured. My application is very cursor-based.<br><br><br>{<br>    "Controller": {<br> <br>        "Listener":<br>        {<br>            "__type": "FileWorkloadListener",<br>            "Source": "E:\\Workload_Tool\\Trace3\\SqlWorkload_01.sqlite",<br>            "SynchronizationMode": "true"<br>        },<br> <br>        "Consumers":<br>        [<br>            {<br>                "__type": "ReplayConsumer",<br>                "ConnectionInfo": <br>                {<br>                    "ServerName": "TEST1",<br>                    "DatabaseName": "test3"<br>                }<br>            },<br>            {<br>                "__type": "AnalysisConsumer",<br>                "ConnectionInfo": <br>                {<br>                    "ServerName": "LOADTESTER",<br>                    "DatabaseName": "DEMO",<br>                    "SchemaName": "baseline"<br>                },<br>                "UploadIntervalSeconds": 60<br>            }<br>        ]<br>    }<br>}<br><br><br>I am having these errors:<br><br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529452] - Error: sp_cursoroption: The cursor identifier value provided (b4dff33) is not valid.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529454] - Error: sp_cursoroption: The cursor identifier value provided (b4dff33) is not valid.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529456] - Error: sp_cursor: The cursor identifier value provided (b4dff33) is not valid.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529460] - Error: Could not find prepared statement with handle 1073858554.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529462] - Error: Could not find prepared statement with handle 1073858555.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529464] - Error: sp_cursoroption: The cursor identifier value provided (b4dff37) is not valid.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529466] - Error: sp_cursoroption: The cursor identifier value provided (b4dff37) is not valid.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529467] - Error: sp_cursor: The cursor identifier value provided (b4dff37) is not valid.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529472] - Error: Could not find prepared statement with handle 1073858554.<br>Warn - WorkloadTools.Consumer.Replay.ReplayWorker : Worker [110] - Sequence[3529473] - Error: Could not find prepared statement with handle 1073858555.<br><br><br><br>These errors are repeated throughout the replay. Is there any way to correct it?<br><br>Thanks!<br>JN</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-39361" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2022-03-03T14:11:45Z">March 3, 2022 at 15:11</time></header><section class="archived-comment-content">Hi Jose, WorkloadTools has issues with cursors. I ran into this problem multiple times and I have some work to do in this area. I'm afraid I don't have much to offer right now. Sorry.</section></article></li></ol></li><li id="wordpress-comment-45966" class="archived-comment"><article><header><strong>Lee Markum</strong> <time datetime="2025-04-08T15:28:10Z">April 8, 2025 at 16:28</time></header><section class="archived-comment-content"><br><p>Is the second json set meant to be a way to analyze a captured workload from the source without replaying it against another database? It seems like it is meant to be a way to generate a baseline to later compare to a workload that is replayed against a different server. Despite using my AD creds that I know work, when I try this in the WorkloadViewer, for some reason I'm getting a login failed message when trying to connect to the instance and database that will hold the analysis data. </p><br></section></article></li></ol></details>
</div>
