---
title: "Capturing a Workload with WorkloadTools"
date: "2019-03-12T16:03:41"
slug: "capturing-a-workload-with-workloadtools"
source_url: "http://spaghettidba.com/2019/03/12/capturing-a-workload-with-workloadtools/"
url: "/2019/03/12/capturing-a-workload-with-workloadtools/"
categories: ["SQL Server"]
tags: ["Performance Tuning", "WorkloadTools"]
---

Last week I showed you how to use WorkloadTools to analyze a workload. As you have seen, using SqlWorkload to extract performance data from your workload is extremely easy and it just takes a few keystrokes in your favorite text editor to craft the perfect .json configuration file.

Today I’m going to show you how to capture a workload and save it to a file. If you’ve ever tried to perform this task with any other traditional benchmarking tool, like RML Utilities or Distributed Replay, your palms are probably sweaty already, but fear not: no complicated traces to set up, no hypertrophic scripts to create extended events captures. <strong>WorkloadTools makes it as easy as it can get</strong>.

Saving a workload to a file might look superfluous when you think that WorkloadTools has the ability to perform replays in real-time (I’ll discuss this feature in a future post), but there are situations when you want to replay the same exact workload multiple times, maybe changing something in the target database between each benchmark to see precisely what performance looks like under different conditions.

Another scenario where saving the workload to a file comes handy is when the source and destination servers are on different isolated networks and cannot communicate directly: in this case, you will save the workload to a file, copy it to the network where the target server resides and perform the replay there.
<h2>Choosing a file format</h2>
Before I show you how to do it, please allow me to explain what type of file we are going to write to and why I decided to use this format. If you’re not interested in this kind of geeky stuff, you can skip to the next section, no offense taken.

As already mentioned in my previous blog post, SqlWorkload uses a Listener object that relies on the underlying technology to capture the execution events that form the workload, so we have specialized Listeners for SqlTrace and for Extended Events. However, the Listener reads the events from the underlying source and then discards the source immediately.

When the workload is captured with an Extended Events session and the events are processed with the streaming API for Extended Events, it is pretty obvious how this works and why there is no .xel file at the end of the capture: the events are never written to a file and they are processed on the fly. In the same way, when the workload is captured with SqlTrace, SqlWorkload makes sure to keep the trace files on the server’s file system as shortly as possible, so it reads the events from the tail of the active rollover file and forwards them to the Consumers immediately: again, at the end of the capture, there will be no trace file available.

Long story short: using one of the traditional capture formats would require to instruct SQL Server to leave the files on the file system, which is not what we want and often something we cannot do.

Moreover, choosing one of the traditional formats (SqlTrace or Extended Events) would be problematic: Extended Events only works with SQLServer 2012 and newer and SqlTrace can only be read and written with an old 32 bit COM API.

What I decided to use as the<strong> intermediate format for SqlWorkload is a SqLite database</strong>, that contains a handful of tables that persist all the queries captured by the Listener. Yeah, sure: when you’re a database professional it feels very natural to use a database to store information (if  all you have is a hammer, everything looks like a nail), but I can assure you that it is far from an unreasonable decision. Using a SqLite database allows you to inspect, modify and filter the workload data with extreme ease, using industry standard tools.

But enough talking about my decisional process: let’s go straight to the meat of this post.
<h2>Capturing a Workload</h2>
As you probably have guessed, capturing a workload is a matter of preparing a .json file with all the parameters and feeding it to SqlWorkload.

All you need is a Listener that captures the workload using SqlTrace or Extended Events and then a Consumer that takes care of writing to a SqLite file.

The .json file will be similar to this:



```javascript
{
    "Controller": {

        "Listener":
        {
            // I'm using Extended Events here, but it could
            // be any type of listener
            "__type": "ExtendedEventsWorkloadListener",
            "ConnectionInfo":
            {
                "ServerName": "(local)"
            },
            "DatabaseFilter": "MyDatabase"
        },

        "Consumers":
        [
            {
                // The File Writer consumer takes care
                // of saving the workload to a file
                "__type": "WorkloadFileWriterConsumer",
                "OutputFile": "C:\\temp\\SqlWorkload.sqlite"
            }
        ]
    }
}
```



Once the configuration file is ready, you just need to pass its path as a command line argument to SqlWorkload and the Listener will start to forward all the events to the File Writer Consumer. You will see an output similar to this:

<img class="alignnone size-full wp-image-1488" src="/wp-content/uploads/2019/03/capture.png" alt="Capture" width="979" height="512" />

When you are done capturing the workload, you can stop SqlWorkload by pressing CTRL+C and you will be left with a SqLite file containing all your workload. You can actually open that file with a SqLite client of your choice and see what it contains. <a href="https://sqlitebrowser.org/">SqLite Browser</a> is one of the possibilities, but there are countless options in Windows, Linux and Mac.

<img class="alignnone size-full wp-image-1489" src="/wp-content/uploads/2019/03/sqlitebrowser.png" alt="SqliteBrowser" width="1039" height="662" />
<h2>Converting an existing SqlTrace or Extended Events file</h2>
You are probably wondering what to do if you already have a set of SqlTrace or Extended Events files that describe your workload perfectly: you probably don’t want to capture the workload again just for the sake of using it with SqlWorkload. Don’t worry: WorkloadTools also contains a <strong>command line tool to convert .trc and .xel files to the SqLite format</strong> understood by SqlWorkload.

All you have to do is run <strong>ConvertWorkload</strong> and pass the path to the source file and the path to the output file.
<h2>Conclusions</h2>
Again, it couldn’t get easier than that: SqlWorkload provides a Consumer to capture your workload to a file for later use, be it a replay or analysis. All you have to do is fill some info in a .json file and SqlWorkload takes care of the rest for you.

In the next post we will see how to replay a workload using WorkloadTools and we will see how one of the possible sources for the replay can be in fact one of these SqLite files produced by the File Writer Consumer.

Stay tuned!
