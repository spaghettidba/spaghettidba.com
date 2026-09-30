---
title: "An annoying Bug in the Restore Dialog"
date: "2016-02-23T17:06:00"
slug: "an-annoying-bug-in-the-restore-dialog"
source_url: "http://spaghettidba.com/2016/02/23/an-annoying-bug-in-the-restore-dialog/"
url: "/2016/02/23/an-annoying-bug-in-the-restore-dialog/"
categories: ["SQL Server"]
tags: ["BUG", "Connect", "Restore", "SQLServer", "SSMS"]
---

Today, thanks to a customer, I discovered  one of those annoying little things that can really drive you nuts.

Basically, they were trying to restore a backup using the SSMS Restore Database window and they kept getting "No backupset selected to be restored" whenever a backup file was selected.

You just had to select a file for restore and click OK...

<img class="alignnone size-full wp-image-1052" src="/wp-content/uploads/2016/02/choosefile.png" alt="chooseFile" width="604" height="443" />

... to be met with an error message in the Restore Database window:

<img class="alignnone size-full wp-image-1049" src="/wp-content/uploads/2016/02/restore_error_initial.png" alt="Restore_Error_Initial" width="604" height="175" />

The weird thing about it is that the backup file restored perfectly fine from a T-SQL script:

<img class="alignnone size-full wp-image-1050" src="/wp-content/uploads/2016/02/t-sql.png" alt="T-SQL" width="604" height="202" />

So it had to be something wrong with SSMS, but what?

Looking closer at the restore script, one thing stands out. Look at the file name:

<img class="alignnone size-full wp-image-1051" src="/wp-content/uploads/2016/02/t-sql_highlight.png" alt="T-SQL_highlight" width="604" height="202" />

Yep, there's a leading whitespace in the file name. Could that be the source of the problem?

Let's try again with the GUI in a slightly different way. This time I will copy the folder path from the "Backup File Location" textbox...

<img class="alignnone size-full wp-image-1053" src="/wp-content/uploads/2016/02/choosefile_copyfolder.png" alt="chooseFile_CopyFolder" width="604" height="443" />

... and paste it directly in the "File name" textbox, right before the file name:

<img class="alignnone size-full wp-image-1054" src="/wp-content/uploads/2016/02/choosefile_copyfolder2.png" alt="chooseFile_CopyFolder2" width="604" height="443" />

This time everything works as expected.

Bottom line:
<ol>
	<li>This is a bug in SSMS: go on and vote <a href="https://connect.microsoft.com/SQLServer/feedback/details/2395147">this Connect item</a> to have it fixed in a future version.</li>
	<li>Don't use the GUI to restore a database.</li>
	<li>Don't use the GUI at all.</li>
</ol>
