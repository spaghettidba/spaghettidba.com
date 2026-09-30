---
title: "Weird Things Happen with Windows Users"
date: "2016-03-18T11:48:44"
slug: "weird-things-happen-with-windows-users"
source_url: "http://spaghettidba.com/2016/03/18/weird-things-happen-with-windows-users/"
url: "/2016/03/18/weird-things-happen-with-windows-users/"
categories: ["SQL Server"]
tags: ["Login", "SQL", "SQLServer", "Security", "Users", "Windows"]
---

This will be no surprise to those who have been working with SQL Server for a long time, but it can be puzzling at first and actually I was a bit confused myself when I stumbled upon this behavior for the first time.

SQL Server treats windows users in a special way, a way that could lead us to some interesting observations.

First of all, we need a test database and a couple of windows principals to perform our tests:

1. In a command prompt, create a windows group named 'testGroup'



```text
net localgroup testGroup /ADD
```



2. In a command prompt, create a windows user named 'testUser' and add it to the group



```text
net user testUser "testUser" /ADD

net localgroup testGroup testUser /ADD
```



3. In SSMS, create a test database:



```sql
CREATE DATABASE testWindowsUser;
```



Now that everything is set up, we can start our investigation.
<h2>You can create a database user for a Windows user with no corresponding login</h2>
When dealing with windows users, you don’t need to create a login in SQL Server in order to create a database user, but you can create it directly:



```sql
USE testWindowsUser;
GO

CREATE USER [XPS13-SQLC\testUser];
GO
```



We just created a user in the database, without creating a login first and without having to add “WITHOUT LOGIN” to the CREATE USER statement. If you search for a login with the same SID in sys.logins, nothing will turn up:



```sql
SELECT svp.name AS login_name, 
	dbp.name AS user_name, 
	dbp.default_schema_name
FROM sys.database_principals AS dbp
LEFT JOIN sys.server_principals AS svp
	ON dbp.sid = svp.sid
WHERE dbp.name LIKE '%testUser';
```






```text
login_name  user_name            default_schema_name 
----------- -------------------- --------------------
NULL        XPS13-SQLC\testUser  dbo
```



It is interesting to note that the default schema for the user, if you don’t specify one, will be “dbo”.

At this point, the Windows user cannot log in to SQL Server, but the user can be impersonated to perform operations against the databases, in the same exact way as with any other user without login.

Before we proceed with the investigation, let’s clean up our mess:



```sql
DROP USER [XPS13-SQLC\testUser];
```



<h2>You can create a database user for a Windows group with no corresponding login</h2>
If we try to do the same thing with a Windows group, we get even more interesting findings.



```sql
USE testWindowsUser;
GO

CREATE USER [XPS13-SQLC\testGroup]
GO
```



Again, we did not have to specify an existing login name and we did not have to add “WITHOUT LOGIN”. Looking at the user data in sys.database_principals and sys.logins shows again that no login is associated with this user, but this time we can see that no default schema was set.



```sql
SELECT svp.name AS login_name, 
	dbp.name AS user_name, 
	dbp.default_schema_name
FROM sys.database_principals AS dbp
LEFT JOIN sys.server_principals AS svp
	ON dbp.sid = svp.sid
WHERE dbp.name LIKE '%testGroup';
```






```text
login_name  user_name             default_schema_name
----------- --------------------- --------------------
NULL        XPS13-SQLC\testGroup  NULL
```



As common sense suggests, we cannot impersonate a database user that corresponds to a Windows group. If we try that, we are met with an error message.



```sql
EXECUTE AS USER = 'XPS13-SQLC\testGroup'; -- '
```






```text
Msg 15517, Level 16, State 1, Line 85
Cannot execute as the database principal because the principal "XPS13-SQLC\testGroup" does not exist, 
this type of principal cannot be impersonated, or you do not have permission.
```



<h2>Windows users are granted access through groups in surprising ways</h2>
Now the fun begins. Turns out that you can impersonate a Windows user that is not a user in the database, as long as the Windows user is a member of the group.

Let’s grant some permissions to the group and see what happens:



```sql
ALTER ROLE db_owner ADD MEMBER [XPS13-SQLC\testGroup];
GO

EXECUTE AS USER = 'XPS13-SQLC\testUser'; -- '
EXEC('CREATE VIEW testView AS SELECT 1 AS one');
REVERT;
GO
```



Surprisingly enough, we were able to impersonate a database principal that doesn’t exist at all. In fact we dropped it right before we started to play with the groups, right? Let’s check again the database principals:



```sql
SELECT svp.name AS login_name, 
	dbp.name AS user_name, 
	dbp.default_schema_name
FROM sys.database_principals AS dbp
LEFT JOIN sys.server_principals AS svp
	ON dbp.sid = svp.sid
WHERE dbp.name LIKE '%test%';
GO
```






```text
login_name  user_name             default_schema_name 
----------- --------------------- --------------------
NULL        XPS13-SQLC\testGroup  NULL
NULL        XPS13-SQLC\testUser   XPS13-SQLC\testUser
```



<strong>Wait, what? Who created that user?</strong> Looks like SQL Server creates the database user automatically when it needs to impersonate one of the group members that are not created in the database yet.
Another interesting fact is that the default schema of the newly created user matches the user name. If we don’t like that, we can change it afterwards, but wouldn’t it be cool if we could simply change that on the Windows group and let it propagate to the users created during this process? Let’s try and see if this is possible.



```sql
-- First let's drop the user and dependent objects
DROP VIEW [XPS13-SQLC\testUser].testView;
DROP SCHEMA [XPS13-SQLC\testUser];
DROP USER [XPS13-SQLC\testUser];
GO

-- Then let's change the default schema for the group
ALTER USER [XPS13-SQLC\testGroup] WITH default_schema = dbo;
GO

-- Let's re-create the view impersonating the user
EXECUTE AS USER = 'XPS13-SQLC\testUser'; -- '
EXEC('CREATE VIEW testView AS SELECT 1 AS One');
REVERT
GO

-- Check if the view is there
SELECT OBJECT_SCHEMA_NAME(object_id) AS schema_name, name 
FROM sys.views 
WHERE name = 'testView';
GO

-- Check database users:
SELECT svp.name AS login_name, 
	dbp.name AS user_name, 
	dbp.default_schema_name
FROM sys.database_principals AS dbp
LEFT JOIN sys.server_principals AS svp
	ON dbp.sid = svp.sid
WHERE dbp.name LIKE '%test%';
GO
```






```text
schema_name  name
------------ ---------
dbo          testView 

login_name   user_name             default_schema_name 
------------ --------------------- --------------------
NULL         XPS13-SQLC\testGroup  dbo
```



This time the view was placed in the “dbo” schema as expected (remember? We set the default schema on the group), but the really weird thing is that no new user was added. Why? I couldn’t find any answer in the documentation. It is even more puzzling that SQL Server was able to impersonate a user that is not present at all. Nevertheless, as far as I can remember it has always been like this, at least starting from SQL Server 2005.
To be sure we’re not imagining things, let’s change again the default schema of the Windows group:



```sql
-- Note the weird syntax
ALTER USER [XPS13-SQLC\testGroup] WITH default_schema = NULL;
GO

-- Let's re-create the view impersonating the user
EXECUTE AS USER = 'XPS13-SQLC\testUser'; -- '
EXEC('CREATE VIEW testView AS SELECT 1 AS One');
REVERT
GO

-- Check if the view is there
SELECT OBJECT_SCHEMA_NAME(object_id) AS schema_name, name
FROM sys.views
WHERE name = 'testView';
GO

-- Check database users:
SELECT svp.name AS login_name,
	dbp.name AS user_name,
	dbp.default_schema_name
FROM sys.database_principals AS dbp
LEFT JOIN sys.server_principals AS svp
	ON dbp.sid = svp.sid
WHERE dbp.name LIKE '%test%';
GO
```






```text
schema_name          name
-------------------- ---------------------
dbo                  testView
XPS13-SQLC\testUser  testView

login_name           user_name             default_schema_name
-------------------- --------------------- --------------------
NULL                 XPS13-SQLC\testGroup  NULL
NULL                 XPS13-SQLC\testUser   XPS13-SQLC\testUser 
```



Again, SQL Server creates a new user and assigns it a default schema with the same name. The view was placed in the user’s default schema.

Now let’s revert to a clean database and drop some objects.



```sql
DROP VIEW dbo.testView;
DROP VIEW [XPS13-SQLC\testUser].testView;
DROP SCHEMA [XPS13-SQLC\testUser];
DROP USER [XPS13-SQLC\testUser];
GO
```



In order to have a complete picture, we can now check what happens if we create a login for the windows user.



```sql
CREATE LOGIN [XPS13-SQLC\testUser] FROM WINDOWS;
GO

EXECUTE AS LOGIN = 'XPS13-SQLC\testUser'; 
EXEC('CREATE VIEW testView AS SELECT 1 AS One');
REVERT
GO

-- Check if the view is there
SELECT OBJECT_SCHEMA_NAME(object_id) AS schema_name, name 
FROM sys.views 
WHERE name = 'testView';
GO

-- Check database users:
SELECT svp.name AS login_name, 
	dbp.name AS user_name, 
	dbp.default_schema_name
FROM sys.database_principals AS dbp
LEFT JOIN sys.server_principals AS svp
	ON dbp.sid = svp.sid
WHERE dbp.name LIKE '%test%';
GO
```






```text
schema_name          name
-------------------- ---------------------
XPS13-SQLC\testUser  testView


login_name           user_name             default_schema_name
-------------------- --------------------- --------------------
NULL                 XPS13-SQLC\testGroup  NULL
XPS13-SQLC\testUser  XPS13-SQLC\testUser   XPS13-SQLC\testUser 
```



Again, SQL Server creates a new database user for this login and a schema with the same name. The view gets added to the user’s default schema.
What is interesting to note is that we could access the database by logging in as the Windows user, without having an explicit permission path to allow it. Only after accessing the database an explicit database user is created.

If we try the same thing with the default schema set to “dbo” on the windows group, the behavior matches what we got for the user:



```sql
-- let's try again with a default schema on the group
ALTER USER [XPS13-SQLC\testGroup] WITH default_schema = dbo;
GO

-- cleanup
DROP VIEW dbo.testView;
DROP VIEW [XPS13-SQLC\testUser].testView;
DROP SCHEMA [XPS13-SQLC\testUser];
DROP USER [XPS13-SQLC\testUser];
GO

EXECUTE AS LOGIN = 'XPS13-SQLC\testUser'; -- '
EXEC('CREATE VIEW testView AS SELECT 1 AS One');
REVERT
GO

-- Check if the view is there
SELECT OBJECT_SCHEMA_NAME(object_id) AS schema_name, name 
FROM sys.views 
WHERE name = 'testView';
GO

-- Check database users:
SELECT svp.name AS login_name, 
	dbp.name AS user_name, 
	dbp.default_schema_name
FROM sys.database_principals AS dbp
LEFT JOIN sys.server_principals AS svp
	ON dbp.sid = svp.sid
WHERE dbp.name LIKE '%test%';
GO
```



This means that this behavior has to be taken into account when we’re querying permissions on the databases to see who can access what. In order to know whether a windows user is member of a windows group, we can use the system function IS_MEMBER().

In our case, it would be enough to call the function in this way:



```sql
EXECUTE AS LOGIN = 'XPS13-SQLC\testUser'; -- '
SELECT IS_MEMBER('XPS13-SQLC\testGroup');
REVERT
GO
```



Unfortunately, there is no additional parameter available to specify which windows user to test for group membership and the function will always test against the current login. This has two important consequences:
<ol>
	<li>To test multiple logins, we need to impersonate them one at a time, which is difficult to achieve in scripts.</li>
	<li>There is no way to test database users: impersonating the database user will not be enough to test the windows group membership for the windows user associated to the database user.</li>
</ol>
Summing it up, this is what we have:
<table>
<tbody>
<tr>
<th><strong>Windows user impersonated as</strong></th>
<th><strong>Group's Default Schema set</strong></th>
<th><strong>New user added</strong></th>
<th><strong>New user's schema</strong></th>
</tr>
<tr>
<td>Database User</td>
<td>No</td>
<td>Yes</td>
<td>User name</td>
</tr>
<tr>
<td>Database User</td>
<td>Yes</td>
<td>No</td>
<td>-</td>
</tr>
<tr>
<td>Login</td>
<td>No</td>
<td>Yes</td>
<td>User name</td>
</tr>
<tr>
<td>Login</td>
<td>Yes</td>
<td>No</td>
<td>-</td>
</tr>
</tbody>
</table>
&nbsp;
<h2>The dbo user can be mapped to a non-existing Windows User</h2>
This is extremely tricky and I was bitten by this behavior recently, wasting countless hours trying to figure out what was happening.

Imagine that a developer creates a database in the development environment, while logged in with Windows authentication. This is a very common scenario, both if you’re using a centralized development server or developers’ workstations.

When development is complete, the developer hands us a database backup to restore in production, because the database already contains some data (built-in values in lookup tables or something else required by the application). We restore the database in production, where the developer does not have a login, confident that he will be unable to access it. Well, that’s not exactly what is going to happen.

Let’s see it with an example:



```sql
-- Grant dbcreator permissions to the windows user
ALTER SERVER ROLE dbcreator ADD MEMBER [XPS13-SQLC\testUser]
GO

-- The user creates a database. It may happen in development, right?
EXECUTE AS LOGIN = 'XPS13-SQLC\testUser';
CREATE DATABASE testWindowsGroup
REVERT
GO

-- Let's pretend that developers finish working with the database
-- and ask to move it from development to production
-- He takes a backup and we restore it to production
BACKUP DATABASE testWindowsGroup TO DISK = 'c:\temp\testWindowsGroup.bak';
GO

-- We don't have two separate servers to test, we will simulate
-- the same situation by dropping some objects. Let's drop the database.
DROP DATABASE testWindowsGroup;
GO

-- Now let's drop the associated windows login
DROP LOGIN [XPS13-SQLC\testUser]
GO

-- The database gets restored in production (again, we will use the same instance,
-- but the main point is that the login of the database owner is not present).
RESTORE DATABASE testWindowsGroup FROM DISK = 'c:\temp\testWindowsGroup.bak'
GO

-- Who's the owner of the database? You, the DBA. Looking good.
SELECT db.name, svp.name
FROM sys.databases AS db
INNER JOIN sys.server_principals AS svp
	ON db.owner_sid = svp.sid
WHERE database_id = DB_ID('testWindowsGroup');
```



Everything is set up the way it should: the database is restored to production, the DBA is the database owner, the developer has no access to the database and everybody is happy.

Now imagine that a new totally unrelated database gets added to the production instance, a database where everybody in the company must have read-only access. We create a new login for a Windows group that includes all authorized logins and we grant access to the new database.

Again, let’s see it with an example (using tempdb):



```sql
-- Let's add a login for the group and grant permissions on another database
-- I will use tempdb here, but it could be any other database. 
CREATE LOGIN [XPS13-SQLC\testGroup] FROM WINDOWS;
GO

USE tempdb;
GO

-- The group gets added to tempdb with read-only permissions
CREATE USER [XPS13-SQLC\testGroup] FOR LOGIN [XPS13-SQLC\testGroup];
ALTER ROLE db_datareader ADD MEMBER [XPS13-SQLC\testGroup];
GO

-- Let’s go back to the database we restored previously
USE testWindowsGroup;
GO

-- Now see what happens:
EXECUTE AS LOGIN = 'XPS13-SQLC\testUser'; -- '
EXEC('CREATE VIEW testView AS SELECT 1 AS One');
REVERT
GO
```



WTF? A windows user that has no matching SQL Server login could create a view in a database where no matching user exists? How could that happen?



```sql
-- Let's check the permissions of this user:
EXECUTE AS LOGIN = 'XPS13-SQLC\testUser'; -- '
SELECT IS_ROLEMEMBER('db_owner') AS IAmDbOwner, 
	IS_MEMBER('db_owner') AS AgainDbOwner;
REVERT 
GO
```






```text
IAmDbOwner	AgainDbOwner
----------- -------------
          1             1
```



Weird. The login of the Windows user seems to be the database owner, but we checked upon restore that the DBA is the database owner. Moreover, there is no explicit login in the server for this Windows user and the only Windows group that contains this user does not have access at all to the database: how is this possible?
The answer is buried inside the database principals table:



```sql
-- The sid of the dbo user is still the sid of the user that created the database,
-- even if the windows user is not a login in SQL Server
SELECT sid
FROM sys.database_principals
WHERE name = 'dbo';
```



We got access to the database thanks to a windows group added to grant access to a totally unrelated database. The group has no permissions whatsoever on the database, but it allows its members to log in: the actual permissions on the database are granted through the SID of the dbo user.
This can be spotted immediately with the GUI, which is a fact that hides the resolution even more from experienced DBAs that don't use the GUI at all.

<img class="alignnone size-full wp-image-1062" src="/wp-content/uploads/2016/03/dbo.png" alt="dbo" width="604" height="275" />
<h2>Bottom line</h2>
Windows authentication comes handy most of the times and it offers better protection compared to SQL Server authentication, but sometimes the way SQL Server treats Windows users can be puzzling.

Don't take things for granted and check now if you really understand who has access to your databases: the answer might be very different from what you expect.

<strong>P.S.</strong> If you're wondering why I placed a comment with a quote after every "EXECUTE AS" statement, it's just to fix this WordPress wacky syntax highlighter going nuts.
