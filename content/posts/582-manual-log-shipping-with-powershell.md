---
title: "Manual Log Shipping with PowerShell"
date: "2013-02-08T13:57:31"
slug: "manual-log-shipping-with-powershell"
source_url: "http://spaghettidba.com/2013/02/08/manual-log-shipping-with-powershell/"
url: "/2013/02/08/manual-log-shipping-with-powershell/"
categories: ["SQL Server"]
tags: ["High Availability", "Log Shipping", "PowerShell"]
---

Recently I had to implement log shipping as a HA strategy for a set of databases which were originally running under the simple recovery model.

Actually, the databases were subscribers for a merge publication, which leaves database mirroring out of the possible HA options. Clustering was not an option either, due to lack of shared storage at the subscribers.

After turning all databases to full recovery model and setting up log shipping, I started to wonder if there was a better way to implement it. Log shipping provides lots of flexibility, which I didn't need: I just had to ship the transaction log from the primary to a single secondary and have transaction logs restored immediately. Preserving transaction log backups was not needed, because the secondary database was considered a sufficient backup in this case.

Another thing that I observed was the insane amount of memory consumed by SQLLogShip.exe (over 300 MB), which ended up even failing due to OutOfMemoryException at times.

After reading <a href="https://twitter.com/EdwinMSarmiento">Edwin Sarmiento</a>'s fine chapter on <a href="http://www.manning.com/nielsen/">SQL Server MVP Deep Dives</a> "The poor man's SQL Server log shipping", some ideas started to flow.

First of all I needed a table to hold the configuration for my manual log shipping:



```sql
-- =============================================
-- Author:      Gianluca Sartori - @spaghettidba
-- Create date: 2013-02-07
-- Description: Creates a table to hold manual
--              log shipping configuration
-- =============================================

CREATE TABLE msdb.dbo.ManualLogShippingConfig (
    secondary sysname PRIMARY KEY CLUSTERED, -- Name of the secondary SQL Server instance
    sharedBackupFolder varchar(255),         -- UNC path to the backup path on the secondary
    remoteBackupFolder varchar(255)          -- Path to the backup folder on the secondary
                                             -- It's the same path as sharedBackupFolder,
                                             -- as seen from the secondary server
)
GO

INSERT INTO msdb.dbo.ManualLogShippingConfig (
    secondary,
    sharedBackupFolder,
    remoteBackupFolder
)
VALUES (
    'SomeServer',
    '\\SomeShare',
    'Local path of SomeShare on secondary'
)
GO
```



And then I just needed a PowerShell script to do the heavy lifting.

I think the code is commented and readable enough to show what happens behind the scenes.



```powershell
## =============================================
## Author:      Gianluca Sartori - @spaghettidba
## Create date: 2013-02-07
## Description: Ships the log to a secondary server
## =============================================
sl c:\
$ErrorActionPreference = "Stop"

$primary = "$(ESCAPE_DQUOTE(SRVR))"

#
# Read Configuration from the table in msdb
#

$SQL_Config = @"
    SELECT * FROM msdb.dbo.ManualLogShippingConfig
"@

$info = Invoke-sqlcmd -Query $SQL_Config -ServerInstance $primary

$secondary = $info.secondary
$sharedFolder = $info.sharedBackupFolder
$remoteSharedFolder = $info.remoteBackupFolder

$ts = Get-Date -Format yyyyMMddHHmmss

#
# Read default backup path of the primary from the registry
#

$SQL_BackupDirectory = @"
    EXEC master.dbo.xp_instance_regread
        N'HKEY_LOCAL_MACHINE',
        N'Software\Microsoft\MSSQLServer\MSSQLServer',
        N'BackupDirectory'
"@

$info = Invoke-sqlcmd -Query $SQL_BackupDirectory -ServerInstance $primary

$BackupDirectory = $info.Data

#
# Ship the log of all databases in FULL recovery model
# You can change this to ship a single database's log
#

$SQL_FullRecoveryDatabases = @"
    SELECT name
    FROM master.sys.databases
    WHERE recovery_model_desc = 'FULL'
        AND name NOT IN ('master', 'model', 'msdb', 'tempdb')
"@

$info = Invoke-sqlcmd -Query $SQL_FullRecoveryDatabases -ServerInstance $primary

$info | ForEach-Object {

    $DatabaseName = $_.Name

    Write-Output "Processing database $DatabaseName"

    $BackupFile = $DatabaseName + "_" + $ts + ".trn"
    $BackupPath = Join-Path $BackupDirectory $BackupFile
    $RemoteBackupPath = Join-Path $remoteSharedFolder $BackupFile

    $SQL_BackupDatabase = "BACKUP LOG $DatabaseName TO DISK='$BackupPath' WITH INIT;"

    $SQL_NonCopiedBackups = "
        SELECT physical_device_name
        FROM msdb.dbo.backupset AS BS
        INNER JOIN msdb.dbo.backupmediaset AS BMS
            ON BS.media_set_id = BMS.media_set_id
        INNER JOIN msdb.dbo.backupmediafamily AS BMF
            ON BMS.media_set_id = BMF.media_set_id
        WHERE BS.database_name = '$DatabaseName'
            AND BS.type = 'L'
            AND expiration_date IS NULL
        ORDER BY BS.backup_start_date
    "

    #
    # Backup log to local path
    #
    Invoke-Sqlcmd -Query $SQL_BackupDatabase -ServerInstance $primary -QueryTimeout 65535

    Write-Output "LOG backed up to $BackupPath"

    #
    # Query noncopied backups...
    #
    $nonCopiedBackups = Invoke-Sqlcmd -Query $SQL_NonCopiedBackups -ServerInstance $primary

    $nonCopiedBackups | ForEach-Object {

        $BackupPath = $_.physical_device_name

        $BackupFile = Split-Path $BackupPath -Leaf

        $RemoteBackupPath = Join-Path $remoteSharedFolder $BackupFile

        $SQL_RestoreDatabase = "
            RESTORE LOG $DatabaseName
            FROM DISK='$RemoteBackupPath'
            WITH NORECOVERY;
        "

        $SQL_ExpireBackupSet = "
            UPDATE BS
            SET expiration_date = GETDATE()
            FROM msdb.dbo.backupset AS BS
            INNER JOIN msdb.dbo.backupmediaset AS BMS
                ON BS.media_set_id = BMS.media_set_id
            INNER JOIN msdb.dbo.backupmediafamily AS BMF
                ON BMS.media_set_id = BMF.media_set_id
            WHERE BS.database_name = '$DatabaseName'
                AND BS.type = 'L'
                AND physical_device_name = '$BackupPath'
        "

        #
        # Move the transaction log backup to the secondary
        #
        if (Test-Path $BackupPath) {
            Write-Output "Moving $BackupPath to $sharedFolder"
            Move-Item -Path ("Microsoft.PowerShell.Core\FileSystem::" + $BackupPath) -Destination ("Microsoft.PowerShell.Core\FileSystem::" + $sharedFolder) -Force
        }

        #
        # Restore the backup on the secondary
        #
        Invoke-Sqlcmd -Query $SQL_RestoreDatabase -ServerInstance $secondary -QueryTimeout 65535
        Write-Output "Restored LOG from $RemoteBackupPath"

        #
        # Delete the backup file
        #
        Write-Output "Deleting $RemoteBackupPath"
        Remove-Item $RemoteBackupPath -ErrorAction SilentlyContinue

        #
        # Mark the backup as expired
        #
        Write-Output "Expiring backup set $BackupPath"
        Invoke-Sqlcmd -Query $SQL_ExpireBackupSet -ServerInstance $primary

    }
}
```



The script can be used in a SQLAgent PowerShell job step and it's all you need to start shipping your transaction logs.

Obviously, you need to take a full backup on the primary server and restore it to the secondary WITH NORECOVERY.

Once you're ready, you can schedule the job to ship the transaction logs.
