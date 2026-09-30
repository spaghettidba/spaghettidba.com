---
title: "Database Free Space Monitoring - The right way"
date: "2014-09-05T15:28:03"
slug: "database-free-space-monitoring-the-right-way"
source_url: "http://spaghettidba.com/2014/09/05/database-free-space-monitoring-the-right-way/"
url: "/2014/09/05/database-free-space-monitoring-the-right-way/"
categories: ["SQL Server", "T-SQL"]
tags: ["Monitoring", "SQL", "SQLServer"]
---

Lately I spent some time evaluating some monitoring tools for SQL Server and one thing that struck me very negatively is how none of them (to date) has been reporting database free space correctly.
I was actively evaluating one of those tools when one of my production databases ran out of space without any sort of warning.
I was so upset that I decided to code my own monitoring script.

Some things to take into account:
<ul>
	<li>Hard set limits for file growth have to be considered: a drive with lots of space is useless if the database file cannot grow and take it.</li>
	<li>If fixed growth is used, there must be enough space in the drive to accomodate the growth amount you set.</li>
	<li>If percent growth is used, you have to calculate recursively how much your database file will grow before taking all the space in the drive</li>
	<li>Some scripts found in blogs and books don't account for mount points. Use <code>sys.dm_os_volume_stats</code> to include mount points in your calculation (unless you're running SQL Server versions prior to 2012).</li>
	<li>Database free space alone is not enough. NTFS performance start degrading when the drive free space drops below 20%. Make sure you're monitoring that as well.</li>
	<li>20% of a huge database can be lots of space. You can change that threshold to whatever you find appropriate (for instance, less than 20% AND less than 20 GB)</li>
</ul>
That said, here is my script, I hope you find it useful.



```sql
-- create a temporary table to hold data from sys.master_files
IF OBJECT_ID('tempdb..#masterfiles') IS NOT NULL
    DROP TABLE #masterfiles;

CREATE TABLE #masterfiles (
    database_id int,
    type_desc varchar(10),
    name sysname,
    physical_name varchar(255),
    size_mb int,
    max_size_mb int,
    growth int,
    is_percent_growth bit,
    data_space_id int,
    data_space_name nvarchar(128) NULL,
    drive nvarchar(512),
    mbfree int
);

-- extract file information from sys.master_files
-- and correlate each file to its logical volume
INSERT INTO #masterfiles
SELECT
     mf.database_id
    ,type_desc
    ,name
    ,physical_name
    ,size_mb = size / 128
    ,max_size_mb =
        CASE
            WHEN max_size = 268435456 AND type_desc = 'LOG' THEN -1
            ELSE
                CASE
                    WHEN max_size = -1 THEN -1
                    ELSE max_size / 128
                END
        END
    ,mf.growth
    ,mf.is_percent_growth
    ,mf.data_space_id
    ,NULL
    ,d.volume_mount_point
    ,d.available_bytes / 1024 / 1024
FROM sys.master_files AS mf
CROSS APPLY sys.dm_os_volume_stats(database_id, file_id) AS d;

-- add an "emptyspace" column to hold empty space for each file
ALTER TABLE #masterfiles ADD emptyspace_mb int NULL;

-- iterate through all databases to calculate empty space for its files
DECLARE @name sysname;

DECLARE c CURSOR FORWARD_ONLY READ_ONLY STATIC LOCAL
FOR
SELECT name
FROM sys.databases
WHERE state_desc = 'ONLINE'

OPEN c
FETCH NEXT FROM c INTO @name

WHILE @@FETCH_STATUS = 0
BEGIN

    DECLARE @sql nvarchar(max)
    DECLARE @statement nvarchar(max)
    SET @sql = '
        UPDATE mf
        SET emptyspace_mb = size_mb - FILEPROPERTY(name,''SpaceUsed'') / 128,
            data_space_name =
                ISNULL(
                    (SELECT name FROM sys.data_spaces WHERE data_space_id = mf.data_space_id),
                    ''LOG''
                )
        FROM #masterfiles AS mf
        WHERE database_id = DB_ID();
    '
    SET @statement = 'EXEC ' + QUOTENAME(@name) + '.sys.sp_executesql @sql'
    EXEC sp_executesql @statement, N'@sql nvarchar(max)', @sql

    FETCH NEXT FROM c INTO @name
END

CLOSE c
DEALLOCATE c

-- create a scalar function to simulate the growth of the database in the drive's available space
IF OBJECT_ID('tempdb..calculateAvailableSpace') IS NOT NULL
    EXEC tempdb.sys.sp_executesql N'DROP FUNCTION calculateAvailableSpace'

EXEC tempdb.sys.sp_executesql N'
CREATE FUNCTION calculateAvailableSpace(
    @diskFreeSpaceMB float,
    @currentSizeMB float,
    @growth float,
    @is_percent_growth bit
)
RETURNS int
AS
BEGIN
    IF @currentSizeMB = 0
        SET @currentSizeMB = 1
    DECLARE @returnValue int = 0
    IF @is_percent_growth = 0
    BEGIN
        SET @returnValue = (@growth /128) * CAST((@diskFreeSpaceMB / (ISNULL(NULLIF(@growth,0),1) / 128)) AS int)
    END
    ELSE
    BEGIN
        DECLARE @prevsize AS float = 0
        DECLARE @calcsize AS float = @currentSizeMB
        WHILE @calcsize < @diskFreeSpaceMB
        BEGIN
            SET @prevsize = @calcsize
            SET @calcsize = @calcsize + @calcsize * @growth / 100.0
        END
        SET @returnValue = @prevsize - @currentSizeMB
        IF @returnValue < 0
            SET @returnValue = 0
    END

    RETURN @returnValue
END
'

-- report database filegroups with less than 20% available space
;WITH masterfiles AS (
    SELECT *
        ,available_space =
            CASE mf.max_size_mb
                WHEN -1 THEN tempdb.dbo.calculateAvailableSpace(mbfree, size_mb, growth, is_percent_growth)
                ELSE max_size_mb - size_mb
            END
            + emptyspace_mb
    FROM #masterfiles AS mf
),
spaces AS (
    SELECT
         DB_NAME(database_id) AS database_name
        ,data_space_name
        ,type_desc
        ,SUM(size_mb) AS size_mb
        ,SUM(available_space) AS available_space_mb
        ,SUM(available_space) * 100 /
            CASE SUM(size_mb)
                WHEN 0 THEN 1
                ELSE SUM(size_mb)
            END AS available_space_percent
    FROM masterfiles
    GROUP BY DB_NAME(database_id)
        ,data_space_name
        ,type_desc
)
SELECT *
FROM spaces
WHERE available_space_percent < 20
ORDER BY available_space_percent ASC

IF OBJECT_ID('tempdb..#masterfiles') IS NOT NULL
    DROP TABLE #masterfiles;

IF OBJECT_ID('tempdb..calculateAvailableSpace') IS NOT NULL
    EXEC tempdb.sys.sp_executesql N'DROP FUNCTION calculateAvailableSpace'
```



I am sure that there are smarter scripts around that calculate it correctly and I am also sure that there are other ways to obtain the same results (PowerShell, to name one). The important thing is that your script takes every important aspect into account and warns you immediately when the database space drops below your threshold, not when the available space is over.

Last time it happened to me it was a late saturday night and, while I really love my job, I can come up with many better ways to spend my saturday night.

I&#039;m pretty sure you do as well.
