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

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (14)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-1453" class="archived-comment"><article><header><strong>Jeff Moden</strong> <time datetime="2013-02-08T21:57:31Z">February 8, 2013 at 22:57</time></header><section class="archived-comment-content">I was going to ask why you redeveloped the proverbial wheel here but then I saw the following in your fine article"<br><br>"Another thing that I observed was the insane amount of memory consumed by SQLLogShip.exe (over 300 MB), "<br><br>That's a darned good reason!  Well done, Gianluca!.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1455" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2013-02-10T18:27:30Z">February 10, 2013 at 19:27</time></header><section class="archived-comment-content">Thanks Jeff, your comments are always welcome here. <br>I was kind of feeling like reinventing the wheel while coding this script indeed. Also, I was a bit concerned about shipping logs in an "unsupported" way. But 300 mb was too much to issue a couple of backup and copy commands in my opinion.</section></article></li></ol></li><li id="wordpress-comment-1764" class="archived-comment"><article><header><strong>waynesheffield</strong> <time datetime="2013-11-04T16:09:09Z">November 4, 2013 at 17:09</time></header><section class="archived-comment-content">Well done Gianluca.<br>Would you care to comment on your choice of updating the expiration date to show that you have copied the log file over?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1765" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2013-11-04T18:42:43Z">November 4, 2013 at 19:42</time></header><section class="archived-comment-content">Thank you Wayne.<br>In my scenario the log backups were taken exclusively to ship them to the secondary. The expiration date was the easiest way I could think of to mark the backup as copied. SInce the file gets deleted right after restoring, I could also have deleted the record in backupset.</section></article></li></ol></li><li id="wordpress-comment-6474" class="archived-comment"><article><header><strong>Brandon Upson</strong> <time datetime="2014-09-10T17:45:57Z">September 10, 2014 at 18:45</time></header><section class="archived-comment-content">Great Article, but I'm getting an error when running that the specified drive could not be found.  Here is the error.<br><br>A job step received an error at line 58 in a PowerShell script. The corresponding line is '    $RemoteBackupPath = Join-Path $remoteSharedFolder $BackupFile'. Correct the script and reschedule the job. The error information returned by PowerShell is: 'Cannot find drive. A drive with the name 'i' does not exist.<br>'<br><br>I did not setup anything on the secondary server except the Proxy account for executing powershell.  The Full path to the backup folder on the secondary server is i:\logshipping.  Thanks in advance</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-6480" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2014-09-11T08:47:56Z">September 11, 2014 at 09:47</time></header><section class="archived-comment-content">Hi Brandon,<br>I updated the script to incorporate some small corrections.<br>Let me know if it works for you now.<br>Cheers</section></article></li></ol></li><li id="wordpress-comment-6483" class="archived-comment"><article><header><strong>Brandon Upson</strong> <time datetime="2014-09-11T14:03:55Z">September 11, 2014 at 15:03</time></header><section class="archived-comment-content">Thanks Spaghettidba, but I'm getting a different error now.  It looks like there is an issue with the backup file names.  The tlog backup generated is named  OSiTraffic_20140911065600.trn and the file it is looking for in the error message is OSiTraffic_backup_2013_10_01_120001_4426977.trn.  Here is the entire text of the error message<br><br><br>Message<br>Executed as user: OSI-CW\sql-sa-cwservice. A job step received an error at line 125 in a PowerShell script. The corresponding line is '        Invoke-Sqlcmd -Query $SQL_RestoreDatabase -ServerInstance $secondary -QueryTimeout 65535'. Correct the script and reschedule the job. The error information returned by PowerShell is: 'Cannot open backup device 'c:\logshipping\OSiTraffic_backup_2013_10_01_120001_4426977.trn'. Operating system error 2(The system cannot find the file specified.).  RESTORE LOG is terminating abnormally.  '.  Process Exit Code -1.  The step failed.<br><br><br>Thanks again for your help</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-6484" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2014-09-11T14:07:07Z">September 11, 2014 at 15:07</time></header><section class="archived-comment-content">Looks like you have older transaction log backups in the way. Set the expiry date in backupset.</section></article></li></ol></li><li id="wordpress-comment-8183" class="archived-comment"><article><header><strong>goforebroke</strong> <time datetime="2015-07-23T20:17:10Z">July 23, 2015 at 21:17</time></header><section class="archived-comment-content">What is the best way to verify? checking the lsn values and the restore date in the msdb..restorehistory? Also possibly cross refrencing the lsn values of a   "restore headeronly from disk" ?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8188" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-07-24T07:52:44Z">July 24, 2015 at 08:52</time></header><section class="archived-comment-content">What exactly do you want to verify? In this post you already have found evidence that copy-only log backups are not suitable for building a complete log chain. If you want to check if the backups you already have contain a complete log chain, RESTORE HEADERONLY is the way to go.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8191" class="archived-comment"><article><header><strong>goforebroke</strong> <time datetime="2015-07-24T14:38:55Z">July 24, 2015 at 15:38</time></header><section class="archived-comment-content">I am just want to make sure that everything is applying correctly on the secondary. I am not taking copy_only log backups. I have used the RESTORE HEADERONLY to verify the log chain. Everything appears to be working...</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-8192" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-07-24T16:21:45Z">July 24, 2015 at 17:21</time></header><section class="archived-comment-content">OK, sorry, I misinterpreted your comment. Yes, RESTORE HEADERONLY shows which LSNs are in the backup sets and restorehistory shows which ones are in the already restored ones.</section></article></li></ol></li></ol></li></ol></li><li id="wordpress-comment-11670" class="archived-comment"><article><header><strong>83Ermelinda</strong> <time datetime="2017-08-01T23:48:54Z">August 2, 2017 at 00:48</time></header><section class="archived-comment-content">Hi admin, i must say you have hi quality posts here.<br><br>Your page can go viral. You need initial traffic boost only.<br><br>How to get it? Search for; Mertiso's tips go viral</section></article></li><li id="wordpress-comment-36315" class="archived-comment"><article><header><strong>Weyard</strong> <time datetime="2021-07-23T08:54:53Z">July 23, 2021 at 09:54</time></header><section class="archived-comment-content">I wish you included how to back up the database in powershell as well. I found Backup-SqlDatabase but im not sure if thats the right command, because there's also the additional switch for backing transaction log: -BackupAction Log so now im confused: Is this the way to backup the database? and is that enough then along with restore command to enable DB log shipping? If so, why all this complexity?</section></article></li></ol></details>
</div>
