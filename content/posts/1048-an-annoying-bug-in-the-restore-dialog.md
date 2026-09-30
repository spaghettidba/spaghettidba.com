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

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (8)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-9271" class="archived-comment"><article><header><strong>Jeff Moden</strong> <time datetime="2016-02-23T17:35:28Z">February 23, 2016 at 18:35</time></header><section class="archived-comment-content">I'll be damned. I didn't even think of checking for such a thing.  Ended up using a script but this is good to know.  Thanks, ol' friend.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9272" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2016-02-23T17:40:47Z">February 23, 2016 at 18:40</time></header><section class="archived-comment-content">You're welcome, Jeff. Not my sauce anyway: I'm just shouting out what the customer found out.</section></article></li></ol></li><li id="wordpress-comment-9296" class="archived-comment"><article><header><strong>David McKinney.</strong> <time datetime="2016-03-01T08:48:33Z">March 1, 2016 at 09:48</time></header><section class="archived-comment-content">If you used the GUI to begin with, it probably wouldn't have let you put a leading space on your filename.  To be honest, I don't have a lot of sympathy for anyone who finds surprising behaviour around a file which they have chosen to name with a leading space (or have I missed the point?)</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9297" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2016-03-01T09:54:15Z">March 1, 2016 at 10:54</time></header><section class="archived-comment-content">Yep, I think you missed the point. For the record, when you back up a database with the GUI, you can enter file names with leading spaces. That would have been easy to check, especially before posting abrasive comments. To each his own, I suppose.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9298" class="archived-comment"><article><header><strong>David McKinney.</strong> <time datetime="2016-03-01T10:04:34Z">March 1, 2016 at 11:04</time></header><section class="archived-comment-content">I can't check it as I don't have SQL Server installed or available to me in my current role.  I didn't intend my comments to be abrasive, but I still maintain that creating files of any sort which begin with a space is inviting problems. <br><br>With the limited amount of testing I was able to do (albeit not with SQL Server) I note that Windows Explorer, Word and Excel for example will strip out a leading space, while I also saw that from a command prompt this is indeed possible.  If someone accidentally creates a file with a space in front, then this is unfortunate, however to do it deliberately I suggest again is unwise, and I am sure that SQL Server is not the only tool to react badly in this circumstance.<br><br>However I repeat that my intention was not to offend, and I apologise if you felt offended by it.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9299" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2016-03-01T10:21:14Z">March 1, 2016 at 11:21</time></header><section class="archived-comment-content">Don't worry, no offense taken. I concur that leading whitespaces in file names is an unwise choice and nobody in their right mind would do that. However, typos can happen. If SSMS wanted to fix the problem for you, I think it should at least try to be consistent: trim the file name from both backup and restore dialogs, which is not happening.</section></article></li></ol></li></ol></li></ol></li><li id="wordpress-comment-9302" class="archived-comment"><article><header><strong>Markus</strong> <time datetime="2016-03-02T12:39:21Z">March 2, 2016 at 13:39</time></header><section class="archived-comment-content">What version, service pack level and CU is this bug showing itself?  Is it the base version.. is it a specific service pack or CU?....</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9303" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2016-03-02T13:12:49Z">March 2, 2016 at 14:12</time></header><section class="archived-comment-content">Tried in latest and greatest. Can't say for older versions.</section></article></li></ol></li></ol></details>
</div>
