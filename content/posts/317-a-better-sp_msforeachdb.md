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
