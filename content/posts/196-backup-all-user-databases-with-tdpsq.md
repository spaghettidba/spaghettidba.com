---
title: "Backup all user databases with TDPSQL"
date: "2011-07-06T14:49:06"
slug: "backup-all-user-databases-with-tdpsq"
source_url: "http://spaghettidba.com/2011/07/06/backup-all-user-databases-with-tdpsq/"
url: "/2011/07/06/backup-all-user-databases-with-tdpsq/"
categories: ["SQL Server"]
tags: ["TDP", "TDPSQL", "Tivoli", "backup", "batch"]
---

Stanislav Kamaletdin (<a title="Twitter" href="http://twitter.com/#!/zarnaya">twitter</a>) today asked on #sqlhelp how to backup all user databases with TDP for SQL Server:

<img class="alignnone size-full wp-image-208" title="Twitter" src="/wp-content/uploads/2011/07/zarnaya.png" alt="Twitter" width="549" height="101" />

My first thought was to use the "*" wildcard, but this actually means <strong><em>all</em></strong> databases, not just <strong><em>user</em></strong> databases.

I ended up adapting a small batch file I've been using for a long time to take backups of all user databases with full recovery model:



```powershell
@ECHO OFF

SQLCMD -E -Q "SET NOCOUNT ON; SELECT name FROM sys.databases WHERE name NOT IN ('master','model','msdb','tempdb')" -h -1 -o tdpsql_input.txt
FOR /F %%A IN (tdpsql_input.txt) DO CALL :perform %%A

GOTO end_batch

:perform
tdpsqlc backup %1 full /configfile=tdpsql.cfg /tsmoptfile=dsm.opt /sqlserver=servername /logfile=tdpsqlc.log

:end_batch
```



Most of the "trick" is in the SQLCMD line:
<ul>
	<li>-Q "query" executes the query and returns. I added "SET NOCOUNT ON;" to eliminate the row count from the output.</li>
	<li>-h -1 suppresses the column headers</li>
	<li>-o tdpsql_input.txt redirects the output to a text file</li>
</ul>
<div>With that syntax I create a text file that contains a database name for each line, that I can use in a FOR loop.</div>
<div><code>FOR /F %%A IN (tdpsql_input.txt) DO CALL :perform %%A</code></div>
<div>means: "For each token found in the file tdpsql_input.txt, assign the token to variable %%A and pass it to the function named 'perform'".</div>
<div>The function "perform" simply invokes tdpsqlc using the parameter %1.</div>
<div>I know that PowerShell would have been a better choice, but I coded this script a long time ago, when PS was not an option for me.</div>
<div>After all, the old DOS batch language still does the trick.</div>
