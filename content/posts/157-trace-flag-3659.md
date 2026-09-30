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
