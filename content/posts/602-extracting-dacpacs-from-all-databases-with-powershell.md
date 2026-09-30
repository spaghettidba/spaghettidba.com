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

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (7)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-1743" class="archived-comment"><article><header><strong>Richard Lee</strong> <time datetime="2013-09-11T15:06:21Z">September 11, 2013 at 16:06</time></header><section class="archived-comment-content">I posted something not too dissimilar earlier this year, and am so much more impressed with your offering.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1744" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2013-09-11T15:49:06Z">September 11, 2013 at 16:49</time></header><section class="archived-comment-content">Thanks. Glad you liked it.</section></article></li></ol></li><li id="wordpress-comment-9246" class="archived-comment"><article><header><strong>Rdkn</strong> <time datetime="2016-02-19T03:00:41Z">February 19, 2016 at 04:00</time></header><section class="archived-comment-content">This is great! I slightly tweaked it to add timestamp to a filename.<br><br>Have you tried scheduling this on regular basis through SQL Agent though? I tried, but I'm getting syntax errors all over. Runs fine in Powershell ISE though..</section></article></li><li id="wordpress-comment-9838" class="archived-comment"><article><header><strong>Sunil</strong> <time datetime="2016-10-18T19:52:40Z">October 18, 2016 at 20:52</time></header><section class="archived-comment-content">How do I avoid hardcoding the path to sqlpackage =&gt; C:\Program Files (x86)\Microsoft SQL Server\110\DAC\bin\sqlpackage.exe<br>Some of the machines have earlier version of Sql Server and the path varies C:\Program Files (x86)\Microsoft SQL Server\120\DAC\bin\sqlpackage.exe</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9839" class="archived-comment"><article><header><strong>Sunil</strong> <time datetime="2016-10-18T19:53:08Z">October 18, 2016 at 20:53</time></header><section class="archived-comment-content">test</section></article></li></ol></li><li id="wordpress-comment-10737" class="archived-comment"><article><header><strong>DorababuMeka</strong> <time datetime="2017-04-26T10:33:29Z">April 26, 2017 at 11:33</time></header><section class="archived-comment-content">Hello I am having a sqlcmd variable defined which is used while deploying the dacpac but after extracting I am not getting the same result is there a way to exclude<br><br>Sample image when verifying differences<br><br>https://social.msdn.microsoft.com/Forums/getfile/1054804</section></article></li><li id="wordpress-comment-11515" class="archived-comment"><article><header><strong>firstmovechess</strong> <time datetime="2017-07-07T05:56:37Z">July 7, 2017 at 06:56</time></header><section class="archived-comment-content">I created this solution to automate the import into Visual Studio solution<br><br>https://github.com/rwforest/dacpac2sln</section></article></li></ol></details>
</div>
