---
title: "Check SQL Server logins with weak password"
date: "2013-09-09T18:22:10"
slug: "check-sql-server-logins-with-weak-password"
source_url: "http://spaghettidba.com/2013/09/09/check-sql-server-logins-with-weak-password/"
url: "/2013/09/09/check-sql-server-logins-with-weak-password/"
categories: ["PowerShell", "SQL Server"]
tags: ["DBA", "SQL", "SQLServer", "Security"]
---

SQL Server logins can implement the same password policies found in Active Directory to make sure that strong passwords are being used.

Unfortunately, especially for servers upgraded from previous versions, the password policies are often disabled and some logins have very weak passwords.

In particular, some logins could have the password set as equal to the login name, which would by one of the first things I would try to hack a server.

Are you sure none of your logins has such a poor password?

<em>PowerShell to the rescue!</em>



```powershell
try {
    if((Get-PSSnapin -Name SQlServerCmdletSnapin100 -ErrorAction SilentlyContinue) -eq $null){
        Add-PSSnapin SQlServerCmdletSnapin100
    }
}
catch {
    Write-Error "This script requires the SQLServerCmdletSnapIn100 snapin"
    exit
}

cls

# Query server names from your Central Management Server
$qry = "
SELECT server_name
FROM msdb.dbo.sysmanagement_shared_registered_servers
"

$servers = Invoke-Sqlcmd -Query $qry -ServerInstance "YourCMSServerGoesHere"

# Extract SQL Server logins
# Why syslogins and not sys.server_principals?
# Believe it or not, I still support a couple of SQL Server 2000
$qry_logins = "
SELECT loginname, sysadmin
FROM syslogins
WHERE isntname = 0
AND loginname NOT LIKE '##%##'
"

$dangerous_logins = @()

$servers | % {
    $currentServer = $_.server_name
    $logins = Invoke-Sqlcmd -Query $qry_logins -ServerInstance $currentServer

    $logins | % {

        $currentLogin = $_.loginname
        $isSysAdmin = $_.sysadmin

        try {
            # Attempt logging in with login = password
            $one = Invoke-Sqlcmd -Query "SELECT 1" -ServerInstance $currentServer -Username $currentLogin -Password $currentLogin -ErrorAction Stop
            # OMG! Login successful
            # Add the login to $dangerous_logins
            $info = @{}
            $info.LoginName = $currentLogin
            $info.Sysadmin = $isSysAdmin
            $info.ServerName = $currentServer
            $loginInfo = New-Object -TypeName PsObject -Property $info
            $dangerous_logins += $loginInfo
        }
        catch {
            # If the login attempt fails, don't add the login to $dangerous_logins
        }

    }
}

#display dangerous logins
$dangerous_logins
```
