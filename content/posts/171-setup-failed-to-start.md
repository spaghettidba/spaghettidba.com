---
title: "Setup failed to start"
date: "2011-05-27T15:30:22"
slug: "setup-failed-to-start"
source_url: "http://spaghettidba.com/2011/05/27/setup-failed-to-start/"
url: "/2011/05/27/setup-failed-to-start/"
categories: ["SQL Server"]
tags: ["cluster", "error", "setup"]
---

<h1><span class="Apple-style-span" style="font-size:13px;font-weight:normal;">Yesterday I ran into this error message while installing a new SQL Server 2005 instance on a Windows 2003 cluster:</span></h1>


```text
Setup failed to start on the remote machine. Check the Task scheduler event log on the remote machine.
```



<a href="/wp-content/uploads/2011/05/setupfailedtostart.gif"><img class="alignnone size-full wp-image-172" title="SetupFailedToStart" src="/wp-content/uploads/2011/05/setupfailedtostart.gif" alt="" width="604" height="129" /></a>

SQL Server 2005 setup, in a clustered environment, relies on a remote setup process started on the passive nodes through a scheduled task:

<a href="/wp-content/uploads/2011/05/remotesetup.png"><img class="alignnone size-full wp-image-173" title="remoteSetup" src="/wp-content/uploads/2011/05/remotesetup.png" alt="" width="542" height="565" /></a>

For some weird reason, the remote scheduled task refuses to start if there is an active RDP session on the passive nodes. This KB article describes symptoms and resolution in detail: <a href="http://support.microsoft.com/kb/910851/en-us">http://support.microsoft.com/kb/910851/en-us</a>

If you look into the Scheduled Tasks log you will find something similar to this:



```text
sql server Task did not appear to start on machine <machine_name> 267015
```



Needless to say that one of my co-workers was logged on the desktop of one of the passive nodes.  So, if you need another good reason to lock everyone out of your servers’ desktop, here it is.

After resetting the offending session, remember to log on to all the passive nodes and kill the zombie setup processes you may have left. Also, delete the scheduled tasks from each node.
