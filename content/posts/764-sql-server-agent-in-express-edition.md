---
title: "SQL Server Agent in Express Edition"
date: "2014-01-23T19:38:40"
slug: "sql-server-agent-in-express-edition"
source_url: "http://spaghettidba.com/2014/01/23/sql-server-agent-in-express-edition/"
url: "/2014/01/23/sql-server-agent-in-express-edition/"
categories: ["SQL Server"]
tags: ["Codeplex", "PowerShell", "SQL", "SQL Agent", "SQL Server 2008", "SQL Server 2012", "SQL Server Agent", "SQL Server Express", "SQLServer"]
---

As you probably know, <a href="http://msdn.microsoft.com/en-us/library/cc645993(v=sql.110).aspx#Mgmt_Tools">SQL Server Express doesn't ship with SQL Server Agent</a>.

This is a known limitation and many people offered alternative solutions to schedule jobs, including windows scheduler, free and commercial third-party applications.

My favourite SQL Server Agent replacement to date is <a href="https://twitter.com/mrdenny">Denny Cherry</a>'s <a href="https://standalonesqlagent.codeplex.com/">Standalone SQL Agent</a>, for two reasons:
<ol>
	<li>It uses msdb tables to read job information.
This means that jobs, schedules and the like can be scripted using the same script you would use in the other editions.</li>
	<li>It's open source and it was started by a person I highly respect.</li>
</ol>
However, while I still find it a great piece of software, there are a couple of downsides to take into account:
<ol>
	<li>It's still a beta version and the project hasn't been very active lately.</li>
	<li>There's no GUI tool to edit jobs or monitor job progress.</li>
	<li>It fails to install when UAC is turned on</li>
	<li>It's not 100% compatible with SQL Server 2012</li>
	<li>It doesn't restart automatically when the SQL Server instance starts</li>
	<li>It requires sysadmin privileges</li>
</ol>
The UAC problem during installation is easy to solve: open an elevated command prompt and run the installer msi. Easy peasy.

As far as SQL Server 2012 is concerned, the service fails to start when connected to a 2012 instance. In the ERRORLOG file (the one you find in the Standalone SQL Agent directory, not SQL Server's) you'll quickly find the reason of the failure: it can't create the stored procedure sp_help_job_SSA. I don't know why this happens: I copied the definition of the stored procedure from a 2008 instance and it worked fine.

If you don't have a SQL Server 2008 instance available, you can extract the definition of the stored procedure from the <a href="https://standalonesqlagent.codeplex.com/SourceControl/latest#Standalone SQL Agent/Standalone SQL Agent Service/SQLInstance.vb">source code at CodePlex</a>.

<span style="line-height:1.5em;">Issue 5) is a bit more tricky to tackle. When the service loses the connection to the target SQL Server instance, it won't restart automatically and it will remain idle until you cycle the service manually. In the ERRORLOG file you'll find a message that resembles to this:</span>



```text
Error connecting to SQL Instance.
No connection attempt will be made until Sevice is restarted.
```



You can overcome this limitation using a startup stored procedure that restarts the service:



```sql
USE master
GO

EXEC sp_configure 'advanced',1
RECONFIGURE WITH OVERRIDE

EXEC sp_configure 'xp_cmdshell',1
RECONFIGURE WITH OVERRIDE
GO

USE master
GO

CREATE PROCEDURE startStandaloneSQLAgent
AS
BEGIN
    SET NOCOUNT ON;

    EXEC xp_cmdshell 'net stop "Standalone SQL Agent"'
    EXEC xp_cmdshell 'net start "Standalone SQL Agent"'

END
GO

EXEC sp_procoption @ProcName = 'startStandaloneSQLAgent'
      , @OptionName = 'startup'
      , @OptionValue = 'on';
 GO
```



However, you'll probably notice that the SQL Server service account does not have sufficient rights to restart the service.

The following PowerShell script grants the SQL Server service account all the rights it needs. In order to run it, you need to download the code available <a href="http://rohnspowershellblog.wordpress.com/2013/04/13/modifying-service-acls/">at Rohn Edwards' blog</a>.



```powershell
# Change to the display name of your SQL Server Express service
$service = Get-WmiObject win32_service |
	where-object { $_.DisplayName -eq "SQL Server (SQLEXPRESS2008R2)" }

$serviceLogonAccount = $service.StartName

$ServiceAcl = Get-ServiceAcl "Standalone SQL Agent"
$ServiceAcl.Access

# Add an ACE allowing the service user Start and Stop service rights:
$ServiceAcl.AddAccessRule((New-AccessControlEntry -ServiceRights "Start,Stop" -Principal $serviceLogonAccount))

# Apply the modified ACL object to the service:
$ServiceAcl | Set-ServiceAcl

# Confirm the ACE was saved:
Get-ServiceAcl "Standalone SQL Agent" | select -ExpandProperty Access
```



After running this script from an elevated Powershell instance, you can test whether the startup stored procedure has enough privileges by invoking it manually.

If everything works as expected, you can restart the SQL Server Express instance and the Standalone SQL Agent service will restart as well.

In conclusion, Standalone SQL Agent is a good replacement for SQL Server Agent in Express edition and, while it suffers from some limitations, I still believe it's the best option available.
