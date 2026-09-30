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
