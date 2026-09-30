---
title: "Another good reason to avoid AUTO_CLOSE"
date: "2014-11-13T19:10:09"
slug: "another-good-reason-to-avoid-auto_close"
source_url: "http://spaghettidba.com/2014/11/13/another-good-reason-to-avoid-auto_close/"
url: "/2014/11/13/another-good-reason-to-avoid-auto_close/"
categories: ["SQL Server"]
tags: ["AUTO_CLOSE", "Best Practices", "SQL", "SQL Server 2012", "SQLServer"]
---

Does anybody need another good reason to avoid setting AUTO_CLOSE on a database? Looks like I found one.

Some days ago, all of a sudden, a database started to throw errors along the lines of "The log for database MyDatabase is not available". The instance was an old 2008 R2 Express (don't get me started on why an Express Edition is in production...) with some small databases.

The log was definitely there and the database looked online. Actually, I was able to query the tables, but every attempt to update the contents ended up with the "log unavailable" error.

Then I opened the ERRORLOG and found something really interesting: lots and lots of entries similar to "Starting up database MyDatabase" over and over... Does it ring a bell?

Yes, it's <a href="http://msdn.microsoft.com/en-us/library/bb402929.aspx">AUTO_CLOSE</a>

Looks like SQL Server closed the database and failed to open it completely, hence the "log unavailable" errors.

What should be done now to bring the database back to normal behaviour? Simply bring the database offline and then back online:



```sql
ALTER DATABASE MyDatabase SET OFFLINE;
ALTER DATABASE MyDatabase SET ONLINE;
```



And while we're at it, let's disable AUTO_CLOSE:



```sql
ALTER DATABASE MyDatabase SET AUTO_CLOSE OFF;
```



How can such a situation be prevented? There are many ways to accomplish this, ranging from PBM (<a href="https://www.simple-talk.com/sql/database-administration/policy-based-management/">Policy Based Management</a>) to scheduled T-SQL health checks (see <a href="http://www.brentozar.com/blitz/">sp_blitz</a> for instance).

See? Best practices are not for losers!
