---
title: "Error upgrading MDW from 2008R2 to 2012"
date: "2013-10-24T21:48:49"
slug: "error-upgrading-mdw-from-2008r2-to-2012"
source_url: "http://spaghettidba.com/2013/10/24/error-upgrading-mdw-from-2008r2-to-2012/"
url: "/2013/10/24/error-upgrading-mdw-from-2008r2-to-2012/"
categories: ["SQL Server"]
tags: ["SQLServer", "cluster", "setup", "system databases", "test environment", "trace flags"]
---

Some months ago I posted a <a href="/2013/03/19/data-collector-clustering-woes/">method to overcome some quirks in the MDW database</a> in a clustered environment.

Today I tried to upgrade that clustered instance (in a test environment, fortunately) and I got some really annoying errors.

Actually, I got what I deserved for messing with the system databases and I wouldn't even dare posting my experience if  it wasn't cause by something I suggested on this blog.

However, every cloud has a silver lining: many things can go wrong when upgrading a cluster and the resolution I will describe here can fit many failed upgrade situations.

So, what's wrong with the <a href="/2013/03/19/data-collector-clustering-woes/">solution I proposed</a> back in march?

The offending line in that code is the following:



```sql
EXEC sp_rename 'core.source_info_internal', 'source_info_internal_ms'
```



What happened here? Basically, I renamed a table in the MDW and I created a view in its place.

One of the steps of the setup process tries to upgrade the MDW database with a script, that is executed at the first startup on an upgraded cluster node.

The script fails and the following message is found in the ERRORLOG:



```text
Creating table [core].[source_info_internal]...
2013-10-24 09:21:02.99 spid8s Error: 2714, Severity: 16, State: 6.
2013-10-24 09:21:02.99 spid8s There is already an object named 'source_info_internal' in the database.
2013-10-24 09:21:02.99 spid8s Error: 912, Severity: 21, State: 2.
2013-10-24 09:21:02.99 spid8s Script level upgrade for database 'master' failed because upgrade step 'upgrade_ucp_cmdw.sql' encountered error 3602, state 51, severity 25. This is a serious error condition which might interfere with regular operation and the database will be taken offline. If the error happened during upgrade of the 'master' database, it will prevent the entire SQL Server instance from starting. Examine the previous errorlog entries for errors, take the appropriate corrective actions and re-start the database so that the script upgrade steps run to completion.
2013-10-24 09:21:02.99 spid8s Error: 3417, Severity: 21, State: 3.
2013-10-24 09:21:02.99 spid8s Cannot recover the master database. SQL Server is unable to run. Restore master from a full backup, repair it, or rebuild it. For more information about how to rebuild the master database, see SQL Server Books Online.
```



Every attempt to bring the SQL Server resource online results in a similar error message.

The only way to fix the error is to restore the initial state of the MDW database, renaming the table core.source_info_internal_ms to its original name.

But how can it be done, since the instance refuses to start?

Microsoft added and documented <a href="http://support.microsoft.com/kb/2163980/en">trace flag 902</a>, that can be used to bypass the upgrade scripts at instance startup.

Remember that the startup parameters of a clustered instance cannot be modified while the resource is offline, because the registry checkpointing mechanism will restore the registry values stored in the quorum disk while bringing the resource online.

There are three ways to start the instance in this situation:
<ol>
	<li><a href="http://support.microsoft.com/kb/953504/en-us">modify the startup parameters by disabling checkpointing</a></li>
	<li><a href="http://support.microsoft.com/kb/953504/en-us">modify the startup parameters in the quorum registry hives</a></li>
	<li>start the instance manually at the command prompt</li>
</ol>
Method N.3 is the simplest one in this situation and is what I ended up doing.

Once the instance started, I renamed the view core.source_info_internal and renamed core.source_info_internal_ms to its original name.

The instance could then be stopped (CTRL+C at the command prompt or SHUTDOWN WITH NOWAIT in sqlcmd) and restarted removing the trace flag.

With the MDW in its correct state, the upgrade scripts completed without errors and the clustered instance could be upgraded to SQL Server 2012 without issues.

<strong>Lessons learned:</strong>
<ol>
	<li>Never, ever mess with the system databases. The MDW is not technically a system database, but it's shipped by Microsoft and should be kept untouched. If you decide you absolutely need to modify something there, remember to undo your changes before upgrading and applying service packs.</li>
	<li>Always test your environment before upgrading. It took me 1 hour to fix the issue and not every upgrade scenario tolerates 1 hour of downtime. Think about it.</li>
	<li>Test your upgrade.</li>
	<li>Did I mention you need to test?</li>
</ol>
Jokes aside, I caught my error in a test environment and I'm happy it was not in production.

As the saying goes, better safe than sorry.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (1)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-10150" class="archived-comment"><article><header><strong>Johnson</strong> <time datetime="2016-12-28T06:03:10Z">December 28, 2016 at 07:03</time></header><section class="archived-comment-content">Great, This is so chock full of users information and the resources you provided was helpful to me. ThereI found an informative article explaining rebuilding of master database in steps.<br>http://www.sqlmvp.org/rebuild-master-database-without-backup/</section></article></li></ol></details>
</div>
