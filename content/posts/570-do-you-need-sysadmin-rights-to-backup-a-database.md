---
title: "Do you need sysadmin rights to backup a database?"
date: "2013-01-09T22:57:51"
slug: "do-you-need-sysadmin-rights-to-backup-a-database"
source_url: "http://spaghettidba.com/2013/01/09/do-you-need-sysadmin-rights-to-backup-a-database/"
url: "/2013/01/09/do-you-need-sysadmin-rights-to-backup-a-database/"
categories: ["SQL Server"]
tags: ["Connect", "Security", "VDI", "Virtual Device", "backup"]
---

<a href="/wp-content/uploads/2013/01/backup.png"><img class="size-full wp-image-572 alignright" alt="backup" src="/wp-content/uploads/2013/01/backup.png" width="260" height="260" /></a>Looks like a silly question, doesn't it? - Well, you would be surprised to know it's not.

Obviously, you don't need to be a sysadmin to simply issue a BACKUP statement. If you look up the <a href="http://msdn.microsoft.com/it-it/library/ms186865.aspx">BACKUP statement on BOL</a> you'll see in the "Security" section that
<blockquote>BACKUP DATABASE and BACKUP LOG permissions default to members of the <strong>sysadmin</strong> fixed server role and the <strong>db_owner</strong> and <strong>db_backupoperator</strong> fixed database roles.</blockquote>
But there's more to it than just permissions on the database itself: in order to complete successfully, the backup device must be accessible:
<blockquote>[...] SQL Server must be able to read and write to the device; the account under which the SQL Server service runs must have write permissions. [...]</blockquote>
While this statement sound sensible or even obvious when talking about file system devices, with other types of device it's less obvious what "permissions" means. With other types of device I mean tapes and Virtual Backup Devices. Since probably nobody uses tapes directly anymore, basically I'm referring to Virtual Backup Devices.

VDI (Virtual Backup device Interface) is the standard API intended for use by third-party backup software vendors to perform backup operations. Basically, it allows an application to act as a storage device.

The VDI specification is available <a href="http://www.microsoft.com/en-us/download/details.aspx?id=17282">here</a> (you just need the vbackup.chm help file contained in the self-extracting archive).

If you download and browse the documentation, under the "Security" topic, you will find a worrying statement:
<blockquote>The server connection for SQL Server that is used to issue the BACKUP or RESTORE commands must be logged in with the <b>sysadmin</b> fixed server role.</blockquote>
Wait, ... what???!?!??!! Sysadmin???????

Sad but true, sysadmin is the only way to let an application take backups using the VDI API. There is no individual permission you can grant: it's sysadmin or nothing.

Since most third-party backup sofwares rely on the VDI API, this looks like a serious security flaw: every SQL Server instance around the world that uses third-party backup utilities has a special sysadmin login used by the backup tool, or, even worse, the tool runs under the sa login.

In my opinion, this is an unacceptable limitation and I would like to see a better implementation in a future version, so I filed a<a href="https://connect.microsoft.com/SQLServer/feedback/details/775819/backup-and-restore-commands-using-vdi-require-sysadmin-role-membership"> suggestion on Connect</a>.

If you agree with me, feel free to upvote and comment it.
