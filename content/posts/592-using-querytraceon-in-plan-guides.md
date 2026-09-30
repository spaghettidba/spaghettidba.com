---
title: "Using QUERYTRACEON in plan guides"
date: "2013-02-08T18:34:02"
slug: "using-querytraceon-in-plan-guides"
source_url: "http://spaghettidba.com/2013/02/08/using-querytraceon-in-plan-guides/"
url: "/2013/02/08/using-querytraceon-in-plan-guides/"
categories: ["SQL Server", "T-SQL"]
tags: ["Performance Tuning", "Profiler", "Trace", "trace flags", "undocumented"]
---

Yesterday the <a href="http://blogs.msdn.com/b/psssql/archive/2013/02/07/query-hint-querytraceon-is-now-documented-publically.aspx">CSS team</a> made the <a href="http://support.microsoft.com/kb/2801413/en-us">QUERYTRACEON</a> hint publicly documented.

This means that now it's officially supported and you can use it in production code.

After reading the post on the CSS blog, I started to wonder whether there is some actual use in production for this query hint, given that it requires the same privileges as <a href="http://msdn.microsoft.com/it-it/library/ms187329(v=sql.110).aspx">DBCC TRACEON</a>, which means you have to be a member of the sysadmin role.

In fact, if you try to use that hint when connected as a low privileged user, you get a very precise error message, that leaves no room for interpretation:



```sql
SELECT *
FROM [AdventureWorks2012].[Person].[Person]
OPTION (QUERYTRACEON 4199)
```




Msg 2571, Level 14, State 3, Line 1
User 'guest' does not have permission to run DBCC TRACEON.

How can a query hint available to sysadmins only be possibly useful for production?

I posted my doubt on Twitter using the #sqlhelp hashtag and got interesting replies from <a href="http://twitter.com/PaulRandal">Paul Randal</a>, <a href="http://twitter.com/SQL_Kiwi">Paul White</a> and <a href="http://twitter.com/SQLSoldier">Robert Davis</a>.

My concerns were not about the usefulness of the hint per se, but about the usefulness in production code. Often 140 chars are not enough when you want to express your thoughts clearly, in fact I decided to write this blog post to clarify what I mean.

As we have seen, the QUERYTRACEON query hint cannot be used directly by users not in the sysadmin role, but it can be used in stored procedures with "EXECUTE AS owner" and in plan guides.

While it's completely clear what happens when the hint is used in procedures executed in the context of the owner, what happens in plan guides is not so obvious (at least, not to me). In fact, given that the secuirty context is not changed when the plan guide is matched and applied, I would have expected it to fail miserably when executed by a low privileged user, but it's not the case.

Let's try and see what happens:

First of all we need a query "complex enough" to let the optimizer take plan guides into account. A straight "SELECT * FROM table" and anything else that results in a trivial plan won't be enough.



```sql
SELECT *
FROM [Person].[Person] AS P
INNER JOIN [Person].[PersonPhone] AS H
    ON P.BusinessEntityID = H.BusinessEntityID
INNER JOIN [Person].[BusinessEntity] AS BE
    ON P.BusinessEntityID = BE.BusinessEntityID
INNER JOIN [Person].[BusinessEntityAddress] AS BEA
    ON BE.BusinessEntityID = BEA.BusinessEntityID
WHERE BEA.ModifiedDate > '20080101'
```



Then we need a plan guide to apply the QUERYTRACEON hint:



```sql
EXEC sp_create_plan_guide @name = N'[querytraceon]', @stmt = N'SELECT *
FROM [Person].[Person] AS P
INNER JOIN [Person].[PersonPhone] AS H
	ON P.BusinessEntityID = H.BusinessEntityID
INNER JOIN [Person].[BusinessEntity] AS BE
	ON P.BusinessEntityID = BE.BusinessEntityID
INNER JOIN [Person].[BusinessEntityAddress] AS BEA
	ON BE.BusinessEntityID = BEA.BusinessEntityID
WHERE BEA.ModifiedDate > ''20080101''', @type = N'SQL', @hints = N'OPTION (QUERYTRACEON 4199)'
```



If we enable the plan guide and try to issue this query in the context of a low privileged user, we can see no errors thrown any more:



```sql
CREATE LOGIN testlogin WITH PASSWORD = 'testlogin123';
GO
USE AdventureWorks2012;
GO
CREATE USER testlogin FOR LOGIN testlogin;
GO
GRANT SELECT TO testlogin;
GO
EXECUTE AS USER = 'testlogin';
GO
SELECT *
FROM [Person].[Person] AS P
INNER JOIN [Person].[PersonPhone] AS H
    ON P.BusinessEntityID = H.BusinessEntityID
INNER JOIN [Person].[BusinessEntity] AS BE
    ON P.BusinessEntityID = BE.BusinessEntityID
INNER JOIN [Person].[BusinessEntityAddress] AS BEA
    ON BE.BusinessEntityID = BEA.BusinessEntityID
WHERE BEA.ModifiedDate > '20080101';
GO
REVERT;
GO
```



If we open a profiler trace and capture the "Plan Guide Successful" and "Plan Guide Unsuccessful" events, we can see that the optimizer matches the plan guide and enforces the use of the query hint.

Lesson learned: even if  users are not allowed to issue that particular query hint directly, adding it to a plan guide is a way to let anyone use it indirectly.

Bottom line is OPTION QUERYTRACEON can indeed be very useful when we identify some queries that obtain a decent query plan only when a specific trace flag is active and we don't want to enable it for the whole instance. In those cases, a plan guide or a stored procedure in the owner's context can be the answer.
