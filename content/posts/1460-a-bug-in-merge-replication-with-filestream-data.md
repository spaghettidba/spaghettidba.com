---
title: "A bug in merge replication with FILESTREAM data"
date: "2018-07-03T12:05:55"
slug: "a-bug-in-merge-replication-with-filestream-data"
source_url: "http://spaghettidba.com/2018/07/03/a-bug-in-merge-replication-with-filestream-data/"
url: "/2018/07/03/a-bug-in-merge-replication-with-filestream-data/"
categories: ["SQL Server"]
tags: ["BUG", "Merge Replication", "Replication"]
---

I wish I could say that every DBA has a love/hate relationship with Replication, but, let's face it, it's only hate. But it could get worse: it could be Merge Replication. Or even worse: Merge Replication with FILESTREAM.

What could possibly top all this hatred and despair if not a bug? Well, I happened to find one, that I will describe here.
<h2>The scenario</h2>
I published tables with FILESTREAM data before, but it seems like there is a particular planetary alignment that triggers an error during the execution of the snapshot agent.

This unlikely combination consists in a merge article with a FILESTREAM column and two UNIQUE indexes on the ROWGUIDCOL column. Yes, I know that generally it does not make sense to have two indexes on the same column, but this happened to be one of the cases where it did, so we had a CLUSTERED PRIMARY KEY on the uniqueidentifier column decorated with the ROWGUIDCOL attribute and, on top, one more NONCLUSTERED UNIQUE index on the same column, backed by a UNIQUE constraint.

Setting up the publication does not throw any error, but generating the initial snapshot for the publication does:



```text
Cannot create, drop, enable, or disable more than one constraint,
column, index, or trigger named 'ncMSmerge_conflict_TestMergeRep_DataStream'
in this context. Duplicate names are not allowed.
```



Basically, the snapshot agent is complaining about the uniqueness of the name of one of the indexes it is trying to create on the conflict table. The interesting fact about this bug is that it doesn't appear when the table has no FILESTREAM column and it doesn't appear when the table doesn't have the redundant UNIQUE constraint on the ROWGUID column: both conditions need to be met.
<h2>The script</h2>
Here is the full script to reproduce the bug.

Before you run it, make sure that:
<ol>
	<li>FILESTREAM is enabled</li>
	<li>Distribution is configured</li>
</ol>
https://gist.github.com/spaghettidba/37cd6cd75a08890b79599b551f7db454

After running the script, start the snapshot agent and you'll see the error appearing:

<img class="alignnone size-full wp-image-1462" src="/wp-content/uploads/2018/07/snapshot1.png" alt="snapshot" width="596" height="285">
<h2>Workaround</h2>
One way to get rid of the bug is to enforce the uniqueness of the data by using a UNIQUE index instead of a UNIQUE constraint:



```sql
CREATE UNIQUE NONCLUSTERED INDEX UQ_MESL_DataStreamPK
ON [DataStream] ([DataStreamGUID]);
```



With this index, the snapshot agent completes correctly. Please note that the index would have been UNIQUE anyway, because its key is a superset of the primary key.

Hope this helps!
<h2>Please Vote!</h2>
This bug has been filed on UserVoice and can be found here: <a href="https://feedback.azure.com/forums/908035-sql-server/suggestions/34735489-bug-in-merge-replication-snapshot-agent-with-files">https://feedback.azure.com/forums/908035-sql-server/suggestions/34735489-bug-in-merge-replication-snapshot-agent-with-files </a>

Please upvote it!
