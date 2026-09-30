---
title: "Trace Flag 3659"
date: "2011-05-20T22:15:01"
slug: "trace-flag-3659"
source_url: "http://spaghettidba.com/2011/05/20/trace-flag-3659/"
url: "/2011/05/20/trace-flag-3659/"
categories: ["SQL Server"]
tags: ["Log", "Trace"]
---

Many setup scripts for SQL Server include the 3659 trace flag, but I could not find official documentation that explains exactly what this flag means.
After a lot of research, I found a reference to this flag in a script called <a title="AddSelfToSqlSysadmin" href="http://archive.msdn.microsoft.com/Wiki/View.aspx?ProjectName=addselftosqlsysadmin" target="_blank">AddSelfToSqlSysadmin</a>, written by <a title="Ward Beattie at MSDN" href="http://archive.msdn.microsoft.com/UserAccount/UserProfile.aspx?UserName=wardbeattie" target="_blank">Ward Beattie</a>, a developer  in the SQL Server product group at Microsoft.

The script contains a line which suggests that this flag enables logging all errors to errorlog during server startup. I'm unsure of what kind of errors are not logged without setting the flag, but I didn't find any further reference. The <a href="http://msdn.microsoft.com/en-us/library/ms188396.aspx" target="_blank">BOL page for Trace Flags</a> doesn't list this one, so if you happen to know something more, feel free to add a comment here.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (3)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-10219" class="archived-comment"><article><header><strong>newguise</strong> <time datetime="2017-01-16T05:12:56Z">January 16, 2017 at 06:12</time></header><section class="archived-comment-content">Thanks. I'm following instructions (to change server collation) which include this trace flag with no explanation as to why.<br><br>Good to know what it does!</section></article></li><li id="wordpress-comment-12350" class="archived-comment"><article><header><strong>Rick Bielawski</strong> <time datetime="2018-03-28T14:53:04Z">March 28, 2018 at 15:53</time></header><section class="archived-comment-content">This flag is, to the best of my knowledge, typically used when running SQL Server interactively to perform some type of maintenance that requires single user mode.  By default not all possible messages are always logged.  Especially informational messages.  For example a message stating a given operation completed successfully may not appear.  If you need to know when that operation finished (maybe so you can shut down and restart normally) you need to enable such messages with this flag.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12351" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-03-28T14:55:17Z">March 28, 2018 at 15:55</time></header><section class="archived-comment-content">Thanks for the information! Very useful.</section></article></li></ol></li></ol></details>
</div>
