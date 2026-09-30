---
title: "Copy user databases to a different server with PowerShell"
date: "2013-10-31T18:08:46"
slug: "copy-user-databases-to-a-different-server-with-powershell"
source_url: "http://spaghettidba.com/2013/10/31/copy-user-databases-to-a-different-server-with-powershell/"
url: "/2013/10/31/copy-user-databases-to-a-different-server-with-powershell/"
categories: ["SQL Server"]
tags: ["PowerShell", "SQLServer", "backup"]
---

Sometimes you have to copy all user databases from a source server to a destination server.

Copying from development to test could be one reason, but I'm sure there are others.

Since the question came up on the forums at SQLServerCentral, I decided to modify a <a href="/2013/02/08/manual-log-shipping-with-powershell/">script I published some months ago</a> to accomplish this task.

Here is the code:



```powershell
## =============================================
## Author:      Gianluca Sartori - @spaghettidba
## Create date: 2013-10-07
## Description: Copy user databases to a destination
##              server
## =============================================
cls
sl "c:\"
$ErrorActionPreference = "Stop"

# Input your parameters here
$source = "SourceServer\Instance"
$sourceServerUNC = "SourceServer"
$destination = "DestServer\Instance"

# Shared folder on the destination server
# For instance "\\DestServer\D$"
$sharedFolder = "\\DestServer\sharedfolder"
# Path to the shared folder on the destination server
# For instance "D:"
$remoteSharedFolder = "PathOfSharedFolderOnDestServer"

$ts = Get-Date -Format yyyyMMdd

#
# Read default backup path of the source from the registry
#

$SQL_BackupDirectory = @"
    EXEC master.dbo.xp_instance_regread
        N'HKEY_LOCAL_MACHINE',
        N'Software\Microsoft\MSSQLServer\MSSQLServer',
        N'BackupDirectory'
"@

$info = Invoke-sqlcmd -Query $SQL_BackupDirectory -ServerInstance $source

$BackupDirectory = $info.Data

#
# Read master database files location
#
$SQL_Defaultpaths = "
    SELECT *
    FROM (
        SELECT type_desc,
            SUBSTRING(physical_name,1,LEN(physical_name) - CHARINDEX('\', REVERSE(physical_name)) + 1) AS physical_name
        FROM master.sys.database_files
    ) AS src
    PIVOT( MIN(physical_name) FOR type_desc IN ([ROWS],[LOG])) AS pvt
"

$info = Invoke-sqlcmd -Query $SQL_Defaultpaths -ServerInstance $destination

$DefaultData = $info.ROWS
$DefaultLog = $info.LOG

#
# Process all user databases
#
$SQL_FullRecoveryDatabases = @"
    SELECT name
    FROM master.sys.databases
    WHERE name NOT IN ('master', 'model', 'tempdb', 'msdb', 'distribution')
"@

$info = Invoke-sqlcmd -Query $SQL_FullRecoveryDatabases -ServerInstance $source

$info | ForEach-Object {

    try {

        $DatabaseName = $_.Name

        Write-Output "Processing database $DatabaseName"

        $BackupFile = $DatabaseName + "_" + $ts + ".bak"
        $BackupPath = $BackupDirectory + "\" + $BackupFile
        $RemoteBackupPath = $remoteSharedFolder + "\" + $BackupFile

        $SQL_BackupDatabase = "BACKUP DATABASE $DatabaseName TO DISK='$BackupPath' WITH INIT, COPY_ONLY, COMPRESSION;"

        #
        # Backup database to local path
        #
        Invoke-Sqlcmd -Query $SQL_BackupDatabase -ServerInstance $source -QueryTimeout 65535

        Write-Output "Database backed up to $BackupPath"

        $BackupPath = $BackupPath

        $BackupFile = [System.IO.Path]::GetFileName($BackupPath)

        $SQL_RestoreDatabase = "
            RESTORE DATABASE $DatabaseName
            FROM DISK='$RemoteBackupPath'
            WITH RECOVERY, REPLACE,
        "

        $SQL_RestoreFilelistOnly = "
            RESTORE FILELISTONLY
            FROM DISK='$RemoteBackupPath';
        "

        #
        # Move the backup to the destination
        #

        $remotesourcefile = $BackupPath.Substring(1, 2)
        $remotesourcefile = $BackupPath.Replace($remotesourcefile, $remotesourcefile.replace(":","$"))
        $remotesourcefile = "\\" + $sourceServerUNC + "\" + $remotesourcefile

        Write-Output "Moving $remotesourcefile to $sharedFolder"
        Move-Item $remotesourcefile $sharedFolder -Force

        #
        # Restore the backup on the destination
        #
        $i = 0
        Invoke-Sqlcmd -Query $SQL_RestoreFilelistOnly -ServerInstance $destination -QueryTimeout 65535 | ForEach-Object {
            $currentRow = $_
            $physicalName = [System.IO.Path]::GetFileName($CurrentRow.PhysicalName)
            if($CurrentRow.Type -eq "D") {
                $newName = $DefaultData + $physicalName
            }
            else {
                $newName = $DefaultLog + $physicalName
            }
            if($i -gt 0) {$SQL_RestoreDatabase += ","}
            $SQL_RestoreDatabase += " MOVE '$($CurrentRow.LogicalName)' TO '$NewName'"
            $i += 1
        }

        Write-Output "invoking restore command: $SQL_RestoreDatabase"
        Invoke-Sqlcmd -Query $SQL_RestoreDatabase -ServerInstance $destination -QueryTimeout 65535
        Write-Output "Restored database from $RemoteBackupPath"

        #
        # Delete the backup file
        #
        Write-Output "Deleting $($sharedFolder + "\" + $BackupFile) "
        Remove-Item $($sharedFolder + "\" + $BackupFile) -ErrorAction SilentlyContinue

    }
    catch {
       Write-Error $_
    }

}
```



It's a quick'n'dirty script, I'm sure there might be something to fix here and there.  Just drop a comment if you find something.
