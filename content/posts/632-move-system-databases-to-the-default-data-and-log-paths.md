---
title: "Moving system databases to the default data and log paths"
date: "2013-03-22T13:02:03"
slug: "move-system-databases-to-the-default-data-and-log-paths"
source_url: "http://spaghettidba.com/2013/03/22/move-system-databases-to-the-default-data-and-log-paths/"
url: "/2013/03/22/move-system-databases-to-the-default-data-and-log-paths/"
categories: ["SQL Server", "T-SQL"]
tags: ["Maintenance", "SQL", "SQLServer", "setup"]
---

Recently I had to assess and tune quite a lot of SQL Server instances and one the things that are often overlooked is the location of the system databases.

I often see instance where the system databases are located in the system drives under the SQL Server default installation path, which is bad for many reasons, especially for tempdb.

I had to move the system databases so many times that I ended up coding a script to automate the process.

The script finds all system databases that are not sitting in the default data and log paths and issues the ALTER DATABASE statements needed to move the files to the default paths.

Obviously, to let the script work, the default data and log paths must have been set in the instance properties:

<a href="/wp-content/uploads/2013/03/movesystemdbs.png"><img class="alignnone size-full wp-image-638" alt="MoveSystemDBs" src="/wp-content/uploads/2013/03/movesystemdbs.png" width="604" height="542" /></a>

You may also point out that moving all system databases to the default data and log paths is not always a good idea. And you would be right: for instance, if possible, the tempdb database should be working on a fast dedicated disk. However, very often I find myself dealing with low-end servers where separate data and log disks are a luxury, not to mention a dedicated tempdb disk.  If you are concerned about moving tempd to the default data and log paths, you can modify the script accordingly.



```sql
-- =============================================
-- Author:      Gianluca Sartori - spaghettidba
-- Create date: 2013-03-22
-- Description: Moves the system databases to the
--              default data and log paths and 
--              updates SQL Server startup params
--              accordingly.
-- =============================================
SET NOCOUNT ON;

USE master;

-- Find default data and log paths
-- reading from the registry

DECLARE @defaultDataLocation nvarchar(4000)
DECLARE @defaultLogLocation nvarchar(4000)

EXEC master.dbo.xp_instance_regread
    N'HKEY_LOCAL_MACHINE',
    N'Software\Microsoft\MSSQLServer\MSSQLServer',
    N'DefaultData',
    @defaultDataLocation OUTPUT

EXEC master.dbo.xp_instance_regread
    N'HKEY_LOCAL_MACHINE',
    N'Software\Microsoft\MSSQLServer\MSSQLServer',
    N'DefaultLog',
    @defaultLogLocation OUTPUT

-- Loop through all system databases
-- and move to the default data and log paths

DECLARE @sql nvarchar(max)

DECLARE stmts CURSOR STATIC LOCAL FORWARD_ONLY
FOR
SELECT
    ' ALTER DATABASE '+ DB_NAME(database_id) +
    ' MODIFY FILE ( ' +
    '     NAME = '''+ name +''', ' +
    '     FILENAME = '''+
    CASE type_desc
        WHEN 'ROWS' THEN @defaultDataLocation
        ELSE @defaultLogLocation
    END +
    '\'+ RIGHT(physical_name,CHARINDEX('\',REVERSE(physical_name),1)-1) +'''' +
    ' )'
FROM sys.master_files
WHERE DB_NAME(database_id) IN ('master','model','msdb','tempdb')
    AND (
        physical_name NOT LIKE @defaultDataLocation + '%'
        OR physical_name NOT LIKE @defaultLogLocation + '%'
    )

OPEN stmts
FETCH NEXT FROM stmts INTO @sql

WHILE @@FETCH_STATUS = 0
BEGIN

    PRINT @sql
    EXEC(@sql)

    FETCH NEXT FROM stmts INTO @sql
END

CLOSE stmts
DEALLOCATE stmts

-- Update SQL Server startup parameters
-- to reflect the new master data and log
-- files locations

DECLARE @val nvarchar(500)
DECLARE @key nvarchar(100)

DECLARE @regvalues TABLE (
    parameter nvarchar(100),
    value nvarchar(500)
)

INSERT @regvalues
EXEC master.dbo.xp_instance_regenumvalues
        N'HKEY_LOCAL_MACHINE',
        N'SOFTWARE\Microsoft\MSSQLServer\MSSQLServer\Parameters'

DECLARE reg CURSOR STATIC LOCAL FORWARD_ONLY
FOR
SELECT *
FROM @regvalues
WHERE value LIKE '-d%'
    OR value LIKE '-l%'

OPEN reg

FETCH NEXT FROM reg INTO @key, @val

WHILE @@FETCH_STATUS = 0
BEGIN

    IF @val LIKE '-d%'
        SET @val = '-d' + (
            SELECT physical_name
            FROM sys.master_files
            WHERE DB_NAME(database_id) = 'master'
                AND type_desc = 'ROWS'
        )
    IF @val LIKE '-l%'
        SET @val = '-l' + (
            SELECT physical_name
            FROM sys.master_files
            WHERE DB_NAME(database_id) = 'master'
                AND type_desc = 'LOG'
        )

    EXEC master.dbo.xp_instance_regwrite
        N'HKEY_LOCAL_MACHINE',
        N'SOFTWARE\Microsoft\MSSQLServer\MSSQLServer\Parameters',
        @key,
        N'REG_SZ',
        @val

    FETCH NEXT FROM reg INTO @key, @val

END

CLOSE reg
DEALLOCATE reg
```



After running this script, you can shut down the SQL Server service and move the data and log files to the appropriate locations.

When the files are ready, you can bring SQL Server back online.

BE CAREFUL! Before running this script against a clustered instance, check what the xp_instance_regread commands return: I have seen cases with SQL Server not reading from the appropriate keys.
