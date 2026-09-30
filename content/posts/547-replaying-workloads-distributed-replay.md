---
title: "Replaying Workloads with Distributed Replay"
date: "2012-11-22T20:00:40"
slug: "replaying-workloads-distributed-replay"
source_url: "http://spaghettidba.com/2012/11/22/replaying-workloads-distributed-replay/"
url: "/2012/11/22/replaying-workloads-distributed-replay/"
categories: ["SQL Server", "T-SQL"]
tags: ["Distributed Replay", "Ostress", "Profiler", "RML Utilities", "ReadTrace", "Replay", "Trace"]
---

A couple of weeks ago I posted a <a title="More on converting trace files" href="/2012/11/08/more-on-converting-trace-files/">method to convert trace files</a> from the SQL Server 2012 format to the SQL Server 2008 format.

The trick works quite well and the trace file can be opened with Profiler or with ReadTrace from <a title="RML Utilities for SQL Server (x64)" href="http://www.microsoft.com/en-us/download/details.aspx?id=4511">RML Utilities</a>. What doesn't seem to work just as well is the trace replay with Ostress (another great tool bundled in the RML Utilities).

For some reason, OStress refuses to replay the whole trace file and starts throwing lots of errors.

Some errors are due to the workload I was replaying (it contains CREATE TABLE statements and that can obviuosly work just the first time it is issued), but some others seem to be due to parsing errors, probably because of differences in the trace format between version 11 and 10.



```text
11/20/12 12:30:39.008 [0x00001040] File C:\RML\SQL00063.rml: Parser Error: [Error: 60500][State: 1][Abs Char: 1068][Seq: 0] Syntax error [parse error, expecting `tok_RML_END_RPC'] encountered near
0x0000042C: 6C000D00 0A005700 48004500 52004500 l.....W.H.E.R.E.
0x0000043C: 20005500 6E006900 74005000 72006900  .U.n.i.t.P.r.i.
0x0000044C: 63006500 20002600 6C007400 3B002000 c.e. .&.l.t.;. .
0x0000045C: 24003500 2E003000 30000D00 0A004F00 $.5...0.0.....O.
0x0000046C: 52004400 45005200 20004200 59002000 R.D.E.R. .B.Y. .
0x0000047C: 50007200 6F006400 75006300 74004900 P.r.o.d.u.c.t.I.
0x0000048C: 44002C00 20004C00 69006E00 65005400 D.,. .L.i.n.e.T.
0x0000049C: 6F007400 61006C00 3B000D00 0A003C00 o.t.a.l.;.....<. 0x000004AC: 2F004300 4D004400 3E000D00 0A003C00 /.C.M.D.>.....<. 0x000004BC: 2F004C00 41004E00 47003E00 0D000A00 /.L.A.N.G.>.....
0x000004CC:

11/20/12 12:30:39.010 [0x00001040] File C:\RML\SQL00063.rml: Parser Error: [Error: 110010][State: 100][Abs Char: 1068][Seq: 0] SYNTAX ERROR: Parser is unable to safely recover. Correct the errors and try again.
```



The error suggests that the two formats are indeed more different than I supposed, thus making the replay with Ostress a bit unrealiable.

<strong>Are there other options?</strong>

Sure there are! Profiler is another tool that allows replaying the workload, even if some limitations apply. For instance, Profiler cannot be scripted, which is a huge limitation if you are using Ostress in benchmarking script and want to replace it with something else.

That "something else" could actually be the <a title="SQL Server Distributed Replay" href="http://msdn.microsoft.com/en-us/library/ff878183.aspx">Distributed Replay</a> feature introduced in SQL Server 2012.

Basically, Distributed Replay does the same things that Ostress does and even more, with the nice addition of the possibility to start the replay on multiple machines, thus simulating a workload that resembles more the one found in production.

An introduction to Distributed Replay can be found on <a title="Installing and Configuring SQL Server 2012 Distributed Replay" href="http://sqlskills.com/blogs/jonathan/post/Installing-and-Configuring-SQL-Server-2012-Distributed-Replay.aspx">Jonathan Kehayias' blog</a> and I will refrain from going into deep details here: those posts are outstanding and there's very little I could add to that.

<strong>Installing the Distributed Replay feature</strong>

The first step for the installation is adding a new user for the distributed replay services. You could actually use separate accounts for the Controller and Client services, but for a quick demo a single user is enough.

<a href="/wp-content/uploads/2012/11/user_setup.png"><img class="alignnone size-full wp-image-553" title="User_Setup" alt="" src="/wp-content/uploads/2012/11/user_setup.png" height="362" width="604" /></a>

The Distributed Replay Controller and Client features must be selected from the Feature Selection dialog of SQLServer setup:

<a href="/wp-content/uploads/2012/11/install_select.png"><img class="alignnone size-full wp-image-554" title="Install_Select" alt="" src="/wp-content/uploads/2012/11/install_select.png" height="454" width="604" /></a>

In the next steps of the setup you will also be asked the service accounts to use for the services and on the Replay Client page you will have to enter the controller name and the working directories.

Once the setup is over, you will find two new services in the Server Manager:

<a href="/wp-content/uploads/2012/11/services.png"><img class="alignnone size-full wp-image-555" title="Services" alt="" src="/wp-content/uploads/2012/11/services.png" height="269" width="604" /></a>

After starting the services (first the Controller, then the Client), you can go to the log directories and check in the log files if everything is working.

The two files to check are in the following folders:
<ul>
	<li>C:\Program Files (x86)\Microsoft SQL Server\110\Tools\DReplayController\Log</li>
	<li>C:\Program Files (x86)\Microsoft SQL Server\110\Tools\DReplayClient\Log</li>
</ul>
Just to prove one more time that "if something can wrong, it will", the client log will probably contain an obnoxious error message.

<strong>DCOM gotchas</strong>

Setting up the distributed replay services can get tricky because of some permissions needed to let the client connect to the controller. Unsurprisingly, the client/controller communication is provided by DCOM, which must be configured correctly.

Without granting the appropriate permissions, in the distributed replay client log file you may find the following message:



```text
2012-11-03 00:43:04:062 CRITICAL     [Client Service]      [0xC8100005 (6)] Failed to connect controller with error code 0x80070005.
```



In practical terms, the service account that executes the distributed replay controller service must be granted permissions to use the DCOM class locally and through the network:
<ol>
	<li>Run dcomcnfg.exe</li>
	<li>Navigate the tree to Console Root, Component Services, Computers, My Computer, DCOM Config, DReplayController</li>
	<li>Right click DReplayController and choose "properties" from the context menu.</li>
	<li>Click the Security tab</li>
	<li>Click the “Launch and Activation Permissions” edit button and grant  “Local Activation” and “Remote Activation” permissions to the service account</li>
	<li>Click the “Access Permissions” edit button and grant “Local Access” and “Remote Access” permissions to the service account</li>
	<li>Add the service user account to the “Distributed COM Users” group</li>
	<li>Restart the distributed replay controller and client services</li>
</ol>
After restarting the services, you will find that the message in the log file has changed:



```text
2012-11-20 14:01:10:783 OPERATIONAL  [Client Service]      Registered with controller "WIN2012_SQL2012".
```



<strong>Using the Replay feature</strong>

Once the services are successfully started, we can now start using the Distributed Replay feature.

The trace file has to meet the same requirements for replay found in Profiler, thus making the "Replay" trace template suitable for the job.

But there's one more step needed before we can replay the trace file, which cannot be replayed directly. In fact, distributed replay needs to work on a trace stub, obtained preprocessing the original trace file.

The syntax to obtain the stub is the following:



```text
"C:\Program Files (x86)\Microsoft SQL Server\110\Tools\Binn\dreplay.exe" preprocess -i "C:\SomePath\replay_trace.trc" -d "C:\SomePath\preprocessDir"
```



Now that the trace stub is ready, we can start the replay admin tool from the command line, using the following syntax:



```text
"C:\Program Files (x86)\Microsoft SQL Server\110\Tools\Binn\dreplay.exe" replay -s "targetServerName" -d "C:\SomePath\preprocessDir" -w "list,of,allowed,client,names"
```



<strong>A final word</strong>

A comparison of the features found in the different replay tools can be found in the following table:
<table width="100%" border="0" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td></td>
<td style="text-align:center;"><b>Profiler</b></td>
<td style="text-align:center;"><b>Ostress</b></td>
<td style="text-align:center;"><b>Distributed Replay</b></td>
</tr>
<tr>
<td><b>Multithreading</b></td>
<td style="text-align:center;"><b>YES</b></td>
<td style="text-align:center;"><b>YES</b></td>
<td style="text-align:center;"><b>YES</b></td>
</tr>
<tr>
<td><b>Debugging</b></td>
<td style="text-align:center;"><b>YES</b></td>
<td style="text-align:center;"><b>NO</b></td>
<td style="text-align:center;"><b>NO</b></td>
</tr>
<tr>
<td><b>Synchronization</b><b> mode</b></td>
<td style="text-align:center;"><b>NO</b></td>
<td style="text-align:center;"><b>YES</b></td>
<td style="text-align:center;"><b>YES</b></td>
</tr>
<tr>
<td><b>Stress mode</b></td>
<td style="text-align:center;"><b>YES</b></td>
<td style="text-align:center;"><b>YES</b></td>
<td style="text-align:center;"><b>YES</b></td>
</tr>
<tr>
<td><b>Distributed mode</b></td>
<td style="text-align:center;"><b>NO</b></td>
<td style="text-align:center;"><b>NO</b></td>
<td style="text-align:center;"><b>YES</b></td>
</tr>
<tr>
<td><b>Scriptable</b></td>
<td style="text-align:center;"><b>NO</b></td>
<td style="text-align:center;"><b>YES</b></td>
<td style="text-align:center;"><b>YES</b></td>
</tr>
<tr>
<td><b>Input format</b></td>
<td style="text-align:center;"><strong>Trace</strong></td>
<td style="text-align:center;"><strong>Trace/RML/SQL</strong></td>
<td style="text-align:center;"><strong>Trace</strong></td>
</tr>
</tbody>
</table>
The Distributed Replay Controller can act as  a replacement for Ostress, except for the ability to replay SQL and RML files.

Will we be using RML Utilities again in the future? Maybe: it  depends on what Microsoft decides to do with this tool. It's not unlikely that the Distributed Replay feature will replace the RML Utilities entirely. The tracing feature itself  has an unceartain future ahead, with the deprecation in SQL Server 2012. Probably this new feature will disappear in the next versions of SQLServer, or it will be ported to the Extended Events instrastructure, who knows?

One thing is sure: today we have three tools that support replaying trace files and seeing this possibilty disappear in the future would be very disappointing. I'm sure SQL Server will never disappoint us. :-)
