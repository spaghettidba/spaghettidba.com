---
title: "Code Repository"
date: "2012-01-02T12:18:26"
slug: "code-repository"
source_url: "http://spaghettidba.com/code-repository/"
url: "/code-repository/"
---

<div>This page is a repository for the code found in some of my blog posts.</div>
<div>If you like my code, feel free to download it and use it.</div>
<div></div>
<div></div>
<div>
<table border="1" width="100%" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td style="background-color:#17365d;color:white;" valign="top" width="35%"><strong>Code</strong></td>
<td style="background-color:#17365d;color:white;" valign="top" width="65%"><strong>Post</strong></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/3df988bd6f833de484ccab28cf8f8495">sp_Template.sql</a></td>
<td valign="top"><a href="/2011/07/08/my-stored-procedure-code-template/">My stored procedure code template</a></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/0484f8c8f3a252618f6122a396def162">dba_runCHECKDB.sql</a></td>
<td valign="top"><a href="/2011/11/28/email-alert-dbcc-checkdb/">Setting up an e-mail alert for DBCC CHECKDB errors</a></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/cd56c36463305409216996195f3120dc">dba_ForEachDB.sql</a></td>
<td valign="top"><a href="/2011/09/09/a-better-sp_msforeachdb/">A better sp_MSForEachDB</a></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/6e279d241263056d618619f6cd8976e9">verify_script.sql</a></td>
<td valign="top"><a href="/2012/03/15/how-to-eat-a-sql-elephant/">How to Eat a SQL Elephant in 10 Bites</a></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/2e58644556dbb162487306382c1f57b1">CustomDateFormat.cs</a></td>
<td valign="top"><a href="/2012/03/23/sql-server-and-custom-date-formats/">SQL Server and Custom Date Formats</a></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/254c03ba4d87e853d6c5c2c30de8aa46">formatDate_Islands_iTVF.sql</a></td>
<td valign="top"><a href="/2012/03/23/sql-server-and-custom-date-formats/">SQL Server and Custom Date Formats</a></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/7e1e49cc3f29eb66e71d51e918d5b36f">formatDate_Recursive_iTVF.sql</a></td>
<td valign="top"><a href="/2012/03/23/sql-server-and-custom-date-formats/">SQL Server and Custom Date Formats</a></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/d51e41f7c4399e4c6ca7ff58a23ea06c">formatDate_scalarUDF.sql</a></td>
<td valign="top"><a href="/2012/03/23/sql-server-and-custom-date-formats/">SQL Server and Custom Date Formats</a></td>
</tr>
<tr>
<td valign="top"><a href="https://gist.github.com/spaghettidba/726f135b3422f567ba7778e3949df396">parseDate_Islands_iTVF.sql</a></td>
<td valign="top"><a href="/2012/03/23/sql-server-and-custom-date-formats/">SQL Server and Custom Date Formats</a></td>
</tr>
</tbody>
</table>
</div>

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (4)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-5208" class="archived-comment"><article><header><strong>David Warner</strong> <time datetime="2014-03-27T10:27:40Z">March 27, 2014 at 11:27</time></header><section class="archived-comment-content">Good Morning,<br>I have had an issue with the pre-2012 version of the DBCC CheckDB script ... in the Catch statement on line 279 I have had to insert the error handling that you provide as part of lines 439 to 446 ... my error was that TempDB wasn't sized correctly and the only error I received was "The current transaction cannot be committed and cannot support operations that write to the log file. Roll back the transaction. [SQLSTATE 42000] (Error 50000)" with the additional error handing it logged the reason for the job failure as lack of space in TempDB. Aside from that it is extremely useful piece of code! :-D</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-5209" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2014-03-27T10:39:22Z">March 27, 2014 at 11:39</time></header><section class="archived-comment-content">Good to hear!<br>I hope you solved your issues with the new version.</section></article></li></ol></li><li id="wordpress-comment-11921" class="archived-comment"><article><header><strong>Dirk</strong> <time datetime="2017-10-05T06:23:47Z">October 5, 2017 at 07:23</time></header><section class="archived-comment-content">Bad link (sp_Template.sql) - did not check the others</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-11925" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2017-10-06T14:03:45Z">October 6, 2017 at 15:03</time></header><section class="archived-comment-content">Thanks for the heads-up! It was Dropbox that decided to change permalinks. Got rid of them and use gists now. Thanks again!</section></article></li></ol></li></ol></details>
</div>
