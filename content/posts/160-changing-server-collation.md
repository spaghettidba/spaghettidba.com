---
title: "Changing Server Collation"
date: "2011-05-26T13:25:21"
slug: "changing-server-collation"
source_url: "http://spaghettidba.com/2011/05/26/changing-server-collation/"
url: "/2011/05/26/changing-server-collation/"
categories: ["SQL Server"]
tags: ["collation", "setup", "trace flags", "undocumented"]
---

In order to avoid collation conflict issues with TempDB, all user databases on a SQL Server instance should be set to the same collation.

Temporary tables and table variables are stored in TempDB, that means that, unless explicitly defined, all character-based columns are created using the database collation, which is the same of the master database. If user databases have a different collation, joining physical tables to temporary tables may cause a collation conflict.

For instance you could have a user database with collation SQL_Latin1_General_CP1_CI_AS on a server with collation Latin1_General_CI_AS:



```sql
SELECT  name,
        collation_name,
        is_system =
        CASE
            WHEN name IN ('master', 'model', 'tempdb', 'msdb') THEN 1
            ELSE 0
        END
FROM    sys.databases
ORDER BY is_system DESC, name ASC
```



<a href="/wp-content/uploads/2011/05/databases.png"><img class="alignnone size-full wp-image-165" title="databases" src="/wp-content/uploads/2011/05/databases.png" alt="" width="355" height="210" /></a>
Every time you create a temporary table and join it to a permanent table in this database, you have to ensure that the collations match, or you will run into a collation conflict:



```sql
USE dblocal
GO

CREATE TABLE TestTable (
    testColumn varchar(10)
)

INSERT INTO TestTable VALUES ('conflict')

CREATE TABLE #TempTable (
    tempColumn varchar(10)
)

INSERT INTO #TempTable VALUES ('conflict')

SELECT *
FROM TestTable
INNER JOIN #TempTable
    ON testColumn = tempColumn
```




<a href="/wp-content/uploads/2011/05/conflict.png"><img class="alignnone size-full wp-image-167" title="conflict" src="/wp-content/uploads/2011/05/conflict.png" alt="" width="604" height="139" /></a>

The only ways to avoid the conflict are:
<ul>
	<li>Define explicitly the collation on the temporary table with a collation name or database_default</li>
	<li>Add the COLLATE clause to the join predicate, using a collation name or database_default</li>
</ul>


```sql
-- OPTION 1: define the collation when creating the table
CREATE TABLE #TempTable (
    tempColumn varchar(10) COLLATE database_default
)

-- OPTION 2: force a specific collation when querying the table
SELECT *
FROM TestTable
INNER JOIN #TempTable
    ON testColumn = tempColumn COLLATE database_default
```



The first option must be preferred when possible, because it doesn’t need performing scalar calculations that end up making any index referencing the column virtually useless.

However, both methods require editing the code, which is not always possible. In those cases, changing the server collation is the only possible solution.

In the SQL Server 2000 days, there was a “nice” tool called rebuildm, that recreated the master database and could achieve this task simply. From SQL Server 2005 on, the only tool to rebuild system databases is the setup utility.

This is what Microsoft recommends to rebuild system databases: <a href="http://msdn.microsoft.com/en-us/library/ms179254.aspx">http://msdn.microsoft.com/en-us/library/ms179254.aspx</a>



```text
Setup /QUIET /ACTION=REBUILDDATABASE /INSTANCENAME=InstanceName
/SQLSYSADMINACCOUNTS=accounts /[ SAPWD= StrongPassword ]
/SQLCOLLATION=CollationName
```



Be warned that blogs and forums are filled with bad advice on this topic. The most frequent ones are these:
<ol start="1">
	<li>Change the collation of the model database
TempDB is created from model when the service starts, which makes this method look smart. It’s not! Changing the database collation for model doesn’t change the collation of the objects inside the database: you would end up with a messy template for every new database.</li>
	<li>Copy the model database from another instance with the desired collation.
It <em>could</em> work, given that you copy the database from an instance with the exact same @@version. Even if you managed to copy the database, tempdb would have a collation other than those of master and msdb, which would mean moving the original problem among the system databases. Believe me, this is not what you want.</li>
</ol>
The recommended method requires running the setup and usually is not a big deal. This blog on  MSDN (CSS Support Engineers) describes in depth how the setup works and how to troubleshoot some common issues: <a href="http://blogs.msdn.com/b/psssql/archive/2008/08/29/how-to-rebuild-system-databases-in-sql-server-2008.aspx">http://blogs.msdn.com/b/psssql/archive/2008/08/29/how-to-rebuild-system-databases-in-sql-server-2008.aspx</a>

<h2>An undocumented method</h2>
There seems to be another undocumented method, mentioned (and advertised as safe) by Paul Randal (<a title="http://www.sqlskills.com/blogs/paul" href="http://www.sqlskills.com/blogs/paul" target="_blank">blog</a> | <a title="http://twitter.com/PaulRandal" href="http://twitter.com/PaulRandal" target="_blank">twitter</a>) in one of his presentations: <a href="http://devconnections.com/updates/LasVegas_Fall10/SQL/Randal-SQL-SDB407-Undocumented.pdf">http://devconnections.com/updates/LasVegas_Fall10/SQL/Randal-SQL-SDB407-Undocumented.pdf</a> (page 17).  The method relies on a startup parameter that allows changing the server collation when combined with a couple of trace flags:



```text
 sqlservr -m -T4022 -T3659 -q"new collation" 
```



Trace flag 3659 allows logging all errors to sql server logs
Trace flag 4022 forces SQL Server to skip startup stored procedures (if you have any).
Startup option “-m” forces single user mode.
Startup option “-q” rebuilds all databases and contained objects into the specified collation, without reinstalling the instance.

Besides being undocumented, this method seems to have some pitfalls. Gail Shaw (<a href="http://sqlinthewild.co.za/">blog</a> | <a href="http://www.twitter.com/SQLintheWild">twitter</a>) raises a couple of warnings on this thread at SqlServerCentral: <a href="http://www.sqlservercentral.com/Forums/Topic269173-146-1.aspx">http://www.sqlservercentral.com/Forums/Topic269173-146-1.aspx</a>

So, why recommend a method that could fail or cause harm to your instance? There is a scenario where this method comes extremely handy, mainly because the documented and supported method fails, which is a big SQL Server 2005 cluster.

One of the biggest innovations in SQL Server 2008 setup concerned the cluster installation: in SQL Server 2005 the setup process was run against all passive nodes and then against the active node for the instance, while SQL Server 2008 setup runs only against the local machine and has to be repeated for each node in the cluster.

Running the setup on all the passive nodes, as SQL Server 2005 setup does, can be a pain in the rear. The more nodes you have, more things can go wrong.

Despite all my efforts, I was unable to run the setup successfully with rebuild database action on a SQL Server 2005 cluster. The log files did not report anything useful for troubleshooting: they were only saying that one of the passive nodes could not complete the setup. I was ready to uninstall the instance and install from scratch when I came across the undocumented –q parameter. I tried (I had nothing to lose, after all) and it worked.

I hope it can work for you too.
