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

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (3)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-12979" class="archived-comment"><article><header><strong>patchy_drizzle</strong> <time datetime="2018-07-11T12:09:59Z">July 11, 2018 at 13:09</time></header><section class="archived-comment-content">From the name, it looks like the error occurs creating an index twice on the conflicts table with same name.<br><br>So there must be two triggers within your ddl that cause that to be.<br><br>The conflict table index includes ROWGUID; I suppose the act of publishing <br>the table creates this conflict table and index. <br><br>It looks as if this bit<br>'ALTER TABLE [DataStream] ADD CONSTRAINT UQ_MESL_DataStreamPK UNIQUE ([DataStreamGUID'<br><br>must also be picked up by the publication process and cause it to try and add the same unique index on the conflict table with the same system generated name.<br><br>Why add another unique index to that GUID column anyway ? Perhaps you don't need...<br><br>Also You might want to check the guid is defined with 'newsequentialid' to avoid lots of page <br>splitting. Especially as it's your clustered index ...</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12980" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-07-11T12:15:13Z">July 11, 2018 at 13:15</time></header><section class="archived-comment-content">Thanks, I appreciate the tips, but they have nothing to do with the bug itself. It's the constraint combined with the filestream column that causes the unwanted behavior</section></article></li></ol></li><li id="wordpress-comment-12982" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-07-12T08:18:21Z">July 12, 2018 at 09:18</time></header><section class="archived-comment-content">The error message appears to be similar, but it's a default constraint in that case. However, there seems to be a bond between the FILESTREAM attribute on the column and the bug: if you remove it from the script, everything works just fine. I have absolutely no idea why FILESTREAM could cause a problem like that, but turns out it does.</section></article></li></ol></details>
</div>
