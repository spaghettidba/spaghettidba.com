---
title: "Extracting DACPACs from all databases with Powershell"
date: "2013-02-13T18:20:34"
slug: "extracting-dacpacs-from-all-databases-with-powershell"
source_url: "http://spaghettidba.com/2013/02/13/extracting-dacpacs-from-all-databases-with-powershell/"
url: "/2013/02/13/extracting-dacpacs-from-all-databases-with-powershell/"
categories: ["SQL Server"]
tags: ["ALM", "PowerShell", "database project", "microsoft sql server", "sqlpackage", "ssdt"]
---

If you are adopting Sql Server Data Tools as your election tool to maintain database projects under source control and achieve an ALM solution, at some stage you will probably want to import all your databases in SSDT.

Yes, it can be done by hand, one at a time, using either the "import live database" or "schema compare" features, but what I have found to be more convenient is the "import dacpac" feature.

Basically, you can extract a dacpac from a live database and then import it in SSDT, entering some options in the import dialog.

The main reason why I prefer this method is the reduced amount of manual steps involved. Moreover, the dacpac extraction process can be fully automated using <a href="http://msdn.microsoft.com/en-us/library/hh550080(v=vs.103).aspx">sqlpackage.exe</a>.

Recently I had to import a lot of databases in SSDT and found that sqlpackage can be used in a PowerShell script to automate the process even further:



```powershell
#
# Extract DACPACs from all databases
#
# Author: Gianluca Sartori - @spaghettidba
# Date:   2013/02/13
# Purpose:
# Loop through all user databases and extract
# a DACPAC file in the working directory
#
#

Param(
    [Parameter(Position=0,Mandatory=$true)]
    [string]$ServerName
)

cls

try {
    if((Get-PSSnapin -Name SQlServerCmdletSnapin100 -ErrorAction SilentlyContinue) -eq $null){
        Add-PSSnapin SQlServerCmdletSnapin100
    }
}
catch {
    Write-Error "This script requires the SQLServerCmdletSnapIn100 snapin"
    exit
}

#
# Gather working directory (script path)
#
$script_path = Split-Path -Parent $MyInvocation.MyCommand.Definition

$sql = "
    SELECT name
    FROM sys.databases
    WHERE name NOT IN ('master', 'model', 'msdb', 'tempdb','distribution')
"

$data = Invoke-sqlcmd -Query $sql -ServerInstance $ServerName -Database master

$data | ForEach-Object {

    $DatabaseName = $_.name

    #
    # Run sqlpackage
    #
    &"C:\Program Files (x86)\Microsoft SQL Server\110\DAC\bin\sqlpackage.exe" `
        /Action:extract `
        /SourceServerName:$ServerName `
        /SourceDatabaseName:$DatabaseName `
        /TargetFile:$script_path\DACPACs\$DatabaseName.dacpac `
        /p:ExtractReferencedServerScopedElements=False `
        /p:IgnorePermissions=False

}
```



It's a very simple script indeed, but it saved me a lot of time and I wanted to share it with you.

Unfortunately, there is no way to automate the import process in SSDT, but looks like Microsoft is actually looking into <a href="https://connect.microsoft.com/SQLServer/feedback/details/772103/automate-creation-of-database-projects-from-sql-server-schema-or-dacpacs-automate-export-of-sql-server-schema-to-text-files">making this feature availabe in a future version</a>.
