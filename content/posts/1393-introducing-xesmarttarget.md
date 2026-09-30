---
title: "Introducing XESmartTarget"
date: "2017-10-19T11:56:04"
slug: "introducing-xesmarttarget"
source_url: "http://spaghettidba.com/2017/10/19/introducing-xesmarttarget/"
url: "/2017/10/19/introducing-xesmarttarget/"
categories: ["SQL Server"]
tags: ["Administration", "Extended Events", "GitHub", "Open Source"]
---

Three years ago, I started to work on a project called <a href="https://github.com/spaghettidba/ExtendedTSQLCollector">ExtendedTsqlCollector</a>. I <a href="https://spaghettidba.com/?s=extendedtsqlcollector">blogged about it multiple times here on spaghettidba.com</a>.

Even if I received positive feedback, I knew that one aspect was slowing down the adoption of the project: the Data Collector. That particular feature of SQL Server has a very bad reputation for being difficult to set up, customize and monitor. ExtendedTSQLCollector tried to address some of those issues, but the damage was already done and I knew that the Data Collector was already on the verge of extinction.

So, how could I preserve the work done for that project and, at the same time, offer DBAs the ability to set up complex actions in response to events? What I aimed to release was a tool capable of streaming events from a session and perform configurable actions in response to those events, mainly writing to a database table and sending alerts. The tool I had in mind should have to be configured in a simple and straightforward way, possibly with a single configuration file.

So, back to the drawing board. The tool I came up with had ditched the data collector, but it kept as much as possible from the previous project.
<h2>Introducing XESmartTarget</h2>
I am proud to introduce <a href="https://github.com/spaghettidba/XESmartTarget">XESmartTarget</a>: the easiest way to interact with extended events sessions without writing a single line of code.

XESmartTarget uses the Extended Events streaming API to connect to a session and execute some actions in response to each event. The actions you perform can be configured in a simple .json file, which controls the Response types and all their properties.

For instance, if you have a session to capture deadlocks, you may want to be notified whenever such an event is captured. All you need to do is configure XESmartTarget to send an email using the EmailResponse class. You can do that by creating a simple .json file with all the parameters needed:

<script src="https://gist.github.com/425552250b3287b8c2073964712c73d7.js"></script>

XESmartTarget will connect to your session and will execute an EmailResponse for every event you capture. What will you see? Not much, because XESmartTarget is a console application that you are supposed to run in the background:

<img class="alignnone size-full wp-image-1398" src="/wp-content/uploads/2017/10/xesmarttarget.png" alt="xesmarttarget" width="1053" height="492" />

What you will actually see is email messages flowing to your inbox:

<img class="alignnone size-full wp-image-1402" src="/wp-content/uploads/2017/10/deadlockemail.png" alt="deadlockemail" width="682" height="530" />

This is just an example of what XESmartTarget can do: you already have Response types to write events to a database table or replay execution-related events to a target instance. More Response types are in the works as well, but the good news is that XESmartTarget is open source, so you can code your own ad contribute it to the <a href="https://github.com/spaghettidba/XESmartTarget">project on GitHub</a>.

What are you waiting for? <a href="https://github.com/spaghettidba/XESmartTarget">Download and try XESmartTarget now</a>!
