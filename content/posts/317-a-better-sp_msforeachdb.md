---
title: "A better sp_MSForEachDB"
date: "2011-09-09T17:53:17"
slug: "a-better-sp_msforeachdb"
source_url: "http://spaghettidba.com/2011/09/09/a-better-sp_msforeachdb/"
url: "/2011/09/09/a-better-sp_msforeachdb/"
categories: ["SQL Server", "T-SQL"]
tags: ["sp_MSForEachDb"]
---

Though undocumented and unsupported, I’m sure that at least once you happened to use Microsoft’s built-in stored procedure to execute a statement against all databases. Let’s face it: it comes handy very often, especially for maintenance tasks.

Some months ago, Aaron Bertand (<a href="http://sqlblog.com/blogs/aaron_bertrand/default.aspx">blog</a>|<a href="http://twitter.com/AaronBertrand">twitter</a>) came up with <a href="http://www.mssqltips.com/sqlservertip/2201/making-a-more-reliable-and-flexible-spmsforeachdb/">a nice replacement</a> and I thought it would be fun to code my own.

The main difference with his (and Microsoft’s) implementation is the absence of a cursor. While flagged correctly (LOCAL FORWARD_ONLY STATIC READ_ONLY) and run against a temporary table, nevertheless I was a bit disturbed by that tiny little cursor, so I decided to get rid of it.

Basically, my code relies on a dynamic SQL pushed down three levels:
<ol>
	<li>sp_executesql <em></em></li>
	<li>sp_executesql <em></em></li>
	<li>EXEC <em></em></li>
</ol>
This trick can be used as many times as you like, given that you keep on declaring and passing all the parameters you need to the lower levels.

I didn’t provide ad-hoc parameters to implement complex filters on sysdatabases, as I’m convinced that they would not be useful enough in a day to day use. If you like this code and want to use it, feel free to change it to incorporate any kind of filter.

Here is the code:

<script src="https://gist.github.com/cd56c36463305409216996195f3120dc.js"></script>

Let’s see some examples of its use:
Print the database name for each user database:



```sql
EXEC [dba_ForEachDB] @statement = 'PRINT DB_NAME()', @replacechar = '?', @name_pattern =  '[USER]'
```



Display the file path of each database file of system databases:



```sql
EXEC [dba_ForEachDB] @statement = 'SELECT physical_name, size FROM sys.database_files', @replacechar = '?', @name_pattern =  '[SYSTEM]'
```


I hope you like it and find it useful.
Happy coding.</pre>

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (8)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-991" class="archived-comment"><article><header><strong>Jason Brimhall (@sqlrnnr)</strong> <time datetime="2011-12-05T17:24:09Z">December 5, 2011 at 18:24</time></header><section class="archived-comment-content">Gianluca - thanks for the script.  When looking at trying to not use MSforeachdb recently I was going to venture down this same path.  You just saved me a bunch of work.</section></article></li><li id="wordpress-comment-992" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2011-12-05T17:27:51Z">December 5, 2011 at 18:27</time></header><section class="archived-comment-content">Thanks! Glad you liked it, Jason.</section></article></li><li id="wordpress-comment-1740" class="archived-comment"><article><header><strong>Erez</strong> <time datetime="2013-08-22T19:49:29Z">August 22, 2013 at 20:49</time></header><section class="archived-comment-content">This works for me. thanks a lot !<br>Erez</section></article></li><li id="wordpress-comment-4045" class="archived-comment"><article><header><strong>Anon</strong> <time datetime="2014-02-17T06:56:32Z">February 17, 2014 at 07:56</time></header><section class="archived-comment-content">Thanks, but I got some problem. I don´t think it handles dbname with multiple - in the name. <br>I got these databases and it failes can´t find X123456.<br><br>X123456-XXXX<br>X123456-YYY<br>X123456-CashM<br>X123456-XXXX-Demo50B<br>X123456-YYY-Demo50B<br>X123456-XXXX-CUR</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-4047" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2014-02-17T08:54:59Z">February 17, 2014 at 09:54</time></header><section class="archived-comment-content">I just tried with the database names you suggested and it works for me. <br>Can you provide the whole set of parameters you are using?<br>Which version are you running?</section></article></li><li id="wordpress-comment-9708" class="archived-comment"><article><header><strong>corey Lawson</strong> <time datetime="2016-09-12T23:02:33Z">September 13, 2016 at 00:02</time></header><section class="archived-comment-content">put square brackets around the string, or use QUOTENAME('[', objname), for building up your SQL string.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9709" class="archived-comment"><article><header><strong>corey Lawson</strong> <time datetime="2016-09-12T23:04:55Z">September 13, 2016 at 00:04</time></header><section class="archived-comment-content">put square brackets around the parts in the SQL string for field names, table names or database names, or use QUOTENAME('[', objname), for building up your SQL string<br><br>as in:<br><br>@sql = 'select * from [' + @dbname + '].dbo.[' + @tbl + '];'<br><br>or <br><br>@sql = 'select * from ' + quotename('[', @dbname) + '.dbo.'+quotename('[', @tbl)+';'</section></article></li></ol></li></ol></li><li id="wordpress-comment-31432" class="archived-comment"><article><header><strong>mobile</strong> <time datetime="2019-11-19T23:23:38Z">November 20, 2019 at 00:23</time></header><section class="archived-comment-content">In a "It's better than nothing" mindset we ran a COPY_ONLY backup of every database on our servers in the dark of the early morning. This is not a great plan but it was not for production data either. Now if that has got gotten the ire of folks raised hold onto your hat.</section></article></li></ol></details>
</div>
