---
title: "Formatting dates in T-SQL"
date: "2011-10-05T17:10:53"
slug: "formatting-dates-in-t-sql"
source_url: "http://spaghettidba.com/2011/10/05/formatting-dates-in-t-sql/"
url: "/2011/10/05/formatting-dates-in-t-sql/"
categories: ["SQL Server", "T-SQL"]
tags: ["SQLServer", "Scalar Function", "UDF"]
---

First of all, let me say it: I don't think this should ever be done on the database side. Formatting dates is a task that belongs to the application side and procedural languages are already featured with lots of functions to deal with dates and regional formats.

However, since the question keeps coming up on the forums at SQLServerCentral, I decided to code a simple scalar UDF to format dates.



```sql
/*
 * AUTHOR: Gianluca Sartori @spaghettidba
 * Returns a data formatted according to the format String.
 * The format string can contain the following tokens in any order:
 *
 * yy	--> Year, two digits
 * YYYY	--> Year, four digits
 * MM	--> Month, two digits
 * m	--> Month, one digit
 * DD	--> Day, two digits
 * d	--> Day, one digit
 * HH	--> Hour, two digits
 * h	--> Hour, one digit
 * NN	--> Minute, two digits
 * n	--> Minute, one digit
 * SS	--> Second, two digits
 * s	--> Second, one digit
 * AP	--> AM/PM
 * 
 * Any character not in the token list gets concatenated
 * to the string and left untouched.
 *
 * EXAMPLE: 
 * SELECT dbo.formatDate(GETDATE(), 'YYYY-MM-DD hh:nn:ss')
 * OUTPUT: 2007-01-25 17:35:21
 *
 * SELECT dbo.formatDate(GETDATE(), 'DD-MM-YYYY')
 * OUTPUT: 25-01-2007
 */
CREATE FUNCTION [dbo].[formatDate](@date as datetime, @format_string as varchar(50)  )
RETURNS varchar(50) 
AS  
BEGIN 
    DECLARE @format varchar(50)
    DECLARE @result AS varchar(50)
    DECLARE @iter AS int
    DECLARE @prevchar AS char(1) 
    DECLARE @currchar AS char(1) 
    DECLARE @currtoken AS varchar(4)
    

    SET @iter = 1
    SET @result = ''
    SET @format = CONVERT(varchar(50),@format_string) COLLATE Latin1_General_CS_AS

    WHILE @iter <= LEN(@format)
    BEGIN
        SET @currchar = CONVERT(char(1),SUBSTRING(@format,@iter,1)) COLLATE Latin1_General_CS_AS
        IF @currchar <> @prevchar OR @iter = LEN(@format)
        BEGIN
            SET @currtoken = 
                CASE (@prevchar) COLLATE Latin1_General_CS_AS -- Use a case-sensitive collation
                    WHEN 'Y' THEN RIGHT('0000' + CAST(YEAR(@date) AS varchar(4)),4)
                    WHEN 'y' THEN RIGHT('00' + CAST(YEAR(@date) AS varchar(4)),2)
                    WHEN 'M' THEN RIGHT('00' + CAST(MONTH(@date) AS varchar(2)),2)
                    WHEN 'm' THEN CAST(MONTH(@date) AS varchar(2))
                    WHEN 'D' THEN RIGHT('00' + CAST(DAY(@date) AS varchar(2)),2)
                    WHEN 'd' THEN CAST(DAY(@date) AS varchar(2))
                    WHEN 'H' THEN RIGHT('00' + CAST(DATEPART(hour,@date) AS varchar(2)),2)
                    WHEN 'h' THEN CAST(DATEPART(hour,@date) AS varchar(2))
                    WHEN 'N' THEN RIGHT('00' + CAST(DATEPART(minute,@date) AS varchar(2)),2)
                    WHEN 'n' THEN CAST(DATEPART(minute,@date) AS varchar(2))
                    WHEN 'S' THEN RIGHT('00' + CAST(DATEPART(second,@date) AS varchar(2)),2)
                    WHEN 's' THEN CAST(DATEPART(second,@date) AS varchar(2))
                    WHEN 'A' THEN CASE WHEN DATEPART(hour,@date) >= 12 THEN 'PM' ELSE 'AM' END
                    WHEN ' ' THEN ' '
                    ELSE RTRIM(@prevchar)
                END
            SET @result = @result + @currtoken
        END
        SET @prevchar = @currchar COLLATE Latin1_General_CS_AS
        SET @iter = @iter + 1
    END
    RETURN @result
END
```




Let's see this function in action:


```sql
SELECT dbo.formatDate(GETDATE(), 'YYYY-MM-d h:NN:SS AP')
-- RETURNS: 2011-10-5 18:07:09 PM
SELECT dbo.formatDate(GETDATE(), 'YYYY-MM-DD HH:NN:SS')
-- RETURNS: 2011-10-05 18:07:09
```



The code is simple and (I hope) clear enough. It's not intended to be the best way to format dates in T-SQL and, honestly, I hope it contains some nasty hidden bug, because you shouldn't be using this code at all!

<blockquote>
For more information on custom date formats in SQLServer, see this post: <a href="/2012/03/23/sql-server-and-custom-date-formats/">SQL Server and custom date formats</a>
</blockquote>
