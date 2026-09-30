---
title: "Mirrored Backups: a useful feature?"
date: "2011-12-29T16:56:28"
slug: "mirrored-backups-a-usefu-feature"
source_url: "http://spaghettidba.com/2011/12/29/mirrored-backups-a-usefu-feature/"
url: "/2011/12/29/mirrored-backups-a-usefu-feature/"
categories: ["SQL Server"]
tags: ["SQL", "backup", "backup database", "backup set", "mirror copies"]
---

One of the features found in the Enterprise Edition of SQL Server is the ability to take <a href="http://msdn.microsoft.com/en-us/library/ms175053.aspx">mirrored backups</a>. Basically, taking a mirrored backup means creating additional copies of the backup media (up to three) using a single BACKUP command, eliminating the need to perform the copies with <em>copy</em> or <em>robocopy</em>.

The idea behind is that you can backup to multiple locations and increase the protection level by having additional copies of the backup set. In case one of the copies gets lost or corrupted, you can use the mirrored copy to perform a restore.



```sql
BACKUP DATABASE [AdventureWorks2008R2]
TO DISK = 'C:\backup\AdventureWorks2008R2.bak'
MIRROR
TO DISK = 'H:\backup\AdventureWorks2008R2.bak'
WITH FORMAT;
GO
```



Another possible scenario for a mirrored backup is deferred tape migration: you can backup to a local disk and mirror to a shared folder on a file server. That way you could have a local copy of the backup set and restore it in case of need and let the mirrored copy migrate to tape when the disk backup software processes the file server’s disks.

<a href="/wp-content/uploads/2011/12/mirroredbackup.png"><img class="alignnone size-full wp-image-420" title="MirroredBackup" src="/wp-content/uploads/2011/12/mirroredbackup.png" alt="" width="604" height="210" /></a>

Mirrored backup sets can be combined with striped backups, given that all the mirror copies contain the same number of stripes:



```sql
BACKUP DATABASE [AdventureWorks2008R2]
TO DISK = 'C:\backup\AdventureWorks2008R2_1.bak',
   DISK = 'C:\backup\AdventureWorks2008R2_2.bak',
   DISK = 'C:\backup\AdventureWorks2008R2_3.bak'
MIRROR
TO DISK = 'H:\AdventureWorks2008R2_1.bak',
   DISK = 'H:\AdventureWorks2008R2_2.bak',
   DISK = 'H:\AdventureWorks2008R2_3.bak'
WITH FORMAT;
GO
```



When restoring from a striped + mirrored backup set, you can mix the files from one media with the files from another media, as each mirrored copy is an exact copy of the main backup set.



```sql
RESTORE DATABASE [AW_Restore]
FROM
	DISK = N'C:\backup\AdventureWorks2008R2_1.bak',  -- main   media
	DISK = N'H:\AdventureWorks2008R2_2.bak',         -- mirror media
	DISK = N'H:\AdventureWorks2008R2_3.bak'          -- mirror media
WITH
	FILE = 1,
	MOVE N'AdventureWorks2008R2_Data'
		TO N'C:\DATA\AW_Restore.mdf',
	MOVE N'AdventureWorks2008R2_Log'
		TO N'C:\DATA\AW_Restore_1.ldf',
	MOVE N'FileStreamDocuments2008R2'
		TO N'C:\DATA\AW_Restore_2.Documents2008R2',
	NOUNLOAD,
	STATS = 10;
GO
```



Looks like a handy feature! However, some limitations apply:
<ul>
	<li><em>If striped, the mirror must contain the same number of stripes</em>.
Looks sensible: each mirror copy is an exact copy of the main backup set, which would be impossible with a different number of devices.</li>
	<li><em>Must be used with FORMAT option</em>.
No append supported: the destination device must be overwritten.</li>
	<li><em>Destination media must be of the same type.</em>
You cannot use disk and tape together. I can understand the reason for this restriction, but, actually, it makes this feature much less useful than it could be.</li>
	<li><em>Fails the backup if <strong>ANY </strong>of the mirrored copies fails</em>.
This is the main pain point: creating multiple copies of the same backup set can end up <em>reducing</em> the protection level, because the whole backup process fails when at least one of the destination media is unavailable or faulty.</li>
</ul>
Does this mean that the ability to take mirrored backups is a useless feature?

Well, it highly depends on your point of view and what matters to you most. I would prefer having at least one copy of the database backup available rather than no backup at all.

Keeping in mind that:
<ul>
	<li>the same exact result can be accomplished using <em>copy</em>, <em>xcopy</em> or <em>robocopy</em></li>
	<li>non-local copies are much more likely to fail rather than local copies</li>
	<li>taking multiple local copies is quite pointless</li>
	<li>Enterprise Edition costs a lot of money</li>
	<li>There’s no GUI in SSMS backup dialog, nor in Maintenance Plans</li>
</ul>
…I think I could live without this feature. At least, this is not one of the countless reasons why I would prefer Enterprise over cheaper editions.
