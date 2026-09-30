---
title: "COPY_ONLY backups and Log Shipping"
date: "2014-01-22T19:44:27"
slug: "copy_only-backups-and-log-shipping"
source_url: "http://spaghettidba.com/2014/01/22/copy_only-backups-and-log-shipping/"
url: "/2014/01/22/copy_only-backups-and-log-shipping/"
categories: ["SQL Server", "T-SQL"]
tags: ["COPY_ONLY", "SQL", "SQLServer", "backup"]
---

Last week I was in the process of migrating a couple of SQL Server instances from 2008 R2 to 2012.

In order to let the migration complete quickly, I set up log shipping from the old instance to the new instance. Obviously, the existing backup jobs had to be disabled, otherwise they would have broken the log chain.

That got me thinking: was there a way to keep both “regular” transaction log backups (taken by the backup tool) and the transaction log backups taken by log shipping?

<span style="line-height:1.5em;"> <a href="/wp-content/uploads/2014/01/ls_architecture.png"><img class="alignnone size-full wp-image-760" alt="ls_architecture" src="/wp-content/uploads/2014/01/ls_architecture.png" width="600" height="355" /></a></span>

The first thing that came to my mind was the <a href="http://technet.microsoft.com/en-us/library/ms191495.aspx">COPY_ONLY</a> option available since SQL Server 2005.

You probably know that COPY_ONLY backups are useful when you have to take a backup for a special purpose, for instance when you have to restore from production to test. With the COPY_ONLY option, database backups don’t break the differential base and transaction log backups don’t break the log chain.

My initial thought was that I could ship COPY_ONLY backups to the secondary and keep taking scheduled transaction log backups with the existing backup tools.

I was dead wrong.

Let’s see it with an example on a TEST database.

I took 5 backups:
<ol>
	<li>FULL database backup, to initialize the log chain. Please note that COPY_ONLY backups cannot be used to initialize the log chain.</li>
	<li>LOG backup</li>
	<li>LOG backup with the COPY_ONLY option</li>
	<li>LOG backup</li>
	<li>LOG backup with the COPY_ONLY option</li>
</ol>
The backup information can be queried from backupset in msdb:



```sql
SELECT
     ROW_NUMBER() OVER(ORDER BY bs.backup_start_date) AS [backup #]
    ,first_lsn
    ,last_lsn
    ,backup_start_date
    ,type
    ,is_copy_only
    ,DENSE_RANK() OVER(ORDER BY type, bs.first_lsn) AS sequence
FROM msdb.dbo.backupset bs
WHERE bs.database_name = 'TEST'
```



<span style="line-height:1.5em;"> <a href="/wp-content/uploads/2014/01/backupsets.png"><img class="alignnone size-full wp-image-758" alt="backupsets" src="/wp-content/uploads/2014/01/backupsets.png" width="604" height="99" /></a></span>

As you can see, the COPY_ONLY backups don’t truncate the transaction log and losing one of those backups wouldn't break the log chain.

However, all backups always start from the first available LSN, which means that scheduled log backups taken without the COPY_ONLY option truncate the transaction log and make significant portions of the transaction log unavailable in the next COPY_ONLY backup.

You can see it clearly in the following picture: the LSNs highlighted in red should contain no gaps in order to be restored successfully to the secondary, but the regular TLOG backups break the log chain in the COPY_ONLY backups.

<a href="/wp-content/uploads/2014/01/backupsets2.png"><img class="alignnone size-full wp-image-759" alt="backupsets2" src="/wp-content/uploads/2014/01/backupsets2.png" width="604" height="99" /></a>

That means that there’s little or no point in taking COPY_ONLY transaction log backups, as “regular” backups will always determine gaps in the log chain.

When log shipping is used, the secondary server is the only backup you can have, unless you keep the TLOG backups or use your backup tool directly to ship the logs.

Why on earth should one take a COPY_ONLY TLOG backup (more than one at least) is beyond my comprehension, but that's a whole different story.
