---
title: "Table-level CHECK constraints"
date: "2011-07-27T22:12:00"
slug: "table-level-check-constraints"
source_url: "http://spaghettidba.com/2011/07/27/table-level-check-constraints/"
url: "/2011/07/27/table-level-check-constraints/"
categories: ["SQL Server", "SQL Server Central", "T-SQL"]
tags: ["check", "constraints", "multicolumn", "table-level"]
---

<blockquote><strong>EDITED 2011-08-05:</strong> <em>This post is <strong>NOT</strong> about the "correct" way to implement table-level check constraints. If that is what you're looking for, see <strong><a href="/2011/08/03/enforcing-complex-constraints-with-indexed-views/">this post</a></strong> instead.</em></blockquote>
Today on SQL Server Central I stumbled upon an apparently simple question on CHECK constraints. The question can be found <a href="http://www.sqlservercentral.com/Forums/FindPost1148910.aspx">here</a>.

The OP wanted to know how to implement a CHECK constraint based on data from another table. In particular, he wanted to prohibit modifications to records in a detail table based on a datetime column on the master table. A simple way to achieve it is to use a trigger, but he was concerned about performance and wanted to implement it with a CHECK constraint.

Let's see how this can be done. First of all, we will need a couple of test tables, with some sample data:



```sql
USE tempdb;
GO

-- Create master table
CREATE TABLE masterTable (
        id int identity(1,1) PRIMARY KEY,
        dateColumn datetime
)
GO

-- Create referenced table
CREATE TABLE detailTable (
        id int identity(1,1) PRIMARY KEY,
        master_id int FOREIGN KEY REFERENCES masterTable(id),
        valueColumn varchar(50)
)
GO

-- Insert sample data
INSERT INTO masterTable(dateColumn) VALUES(GETDATE())
INSERT INTO masterTable(dateColumn) VALUES(DATEADD(day,-1,GETDATE()))
INSERT INTO masterTable(dateColumn) VALUES(DATEADD(day,-2,GETDATE()))

SELECT * FROM masterTable

-- Insert sample data in referenced table
INSERT INTO detailTable(master_id, valueColumn) VALUES (1,'Value for id 1')
INSERT INTO detailTable(master_id, valueColumn) VALUES (2,'Value for id 2')
INSERT INTO detailTable(master_id, valueColumn) VALUES (3,'Value for id 3')

SELECT * FROM detailTable
```



Now we need to create the CHECK constraint. The only way to code it to validate data against a different table is to use a scalar UDF, which, to answer the original question, makes it a poor choice from a performance standpoint.



```sql
-- Create a scalar UDF: you will need this in the CHECK constraint
CREATE FUNCTION getMasterDate(@id int)
RETURNS datetime
AS
BEGIN
        RETURN ISNULL((SELECT dateColumn FROM masterTable WHERE id = @id),'30110101')
END
GO

-- Add the constraint WITH NOCHECK: existing rows are not affected
ALTER TABLE detailTable WITH NOCHECK ADD CONSTRAINT chk_date
        CHECK (DATEADD(day,-1,GETDATE()) > dbo.getMasterDate(master_id))
```



No surprises: the constraints gets added to the table and SQL Server does not complain about the existing rows that don't pass the check, since we decided to use the NOCHECK switch.

Now, with the constraint in place, we should be unable to modify the data in a way that violates the constraint:



```sql
UPDATE detailTable
SET valueColumn = 'New ' + valueColumn
```



Surprise! Some rows conflict with the CHECK constraint, but no complaints from SQL Server, because the constraint is attached to a single column (master_id), and we left that column untouched.
In fact, if we query sys.check_constraints, we can see that this is a column-scoped constraint:



```sql
SELECT parent_column_id, definition, is_not_trusted
FROM sys.check_constraints
WHERE parent_object_id = OBJECT_ID('detailTable')
```



Parent_column_id = 0 means table scoped constraint, parent_column_id &gt; 0 means column-scoped constraint.
If we try to update the column "master_id", the constraint prevents the modification:



```sql
-- If you try to update master_id it fails
UPDATE detailTable
SET master_id = master_id + 1 - 1
```




```text
Msg 547, Level 16, State 0, Line 2
The UPDATE statement conflicted with the CHECK constraint "chk_date". The conflict occurred in database "tempdb", table "dbo.detailTable", column 'master_id'.
The statement has been terminated.
```



What is really surprising is how SQL Server behaves if we decide to make the constraint table-scoped, adding another predicate to the CHECK:



```sql
-- Drop the constraint
ALTER TABLE detailTable DROP CONSTRAINT chk_date
GO

-- Create the constraint referencing multiple columns
ALTER TABLE detailTable WITH NOCHECK ADD CONSTRAINT chk_date
        CHECK (
                DATEADD(day,-1,GETDATE()) > dbo.getMasterDate(master_id)
                AND
                ISNULL(valueColumn,'') = ISNULL(valueColumn,SPACE(0))
        )
GO
```



As we might expect, it doesn't work any more:



```sql
UPDATE detailTable
SET valueColumn = 'New ' + valueColumn
```




```text
Msg 547, Level 16, State 0, Line 2
The UPDATE statement conflicted with the CHECK constraint "chk_date". The conflict occurred in database "tempdb", table "dbo.detailTable", column 'master_id'.
The statement has been terminated.
```



But, wait: what is REALLY attaching the constraint to the column we are trying to modify? Does a thing such as a "table-scoped" constraint really exist?

We just need to add another column and see how it changes the behaviour of the CHECK constraint:



```sql
ALTER TABLE detailTable ADD anotherColumn int
```



Now, if we try to update the newly created column, since we have a "table-scoped" CHECK constraint, we should get an error:



```sql
UPDATE detailTable
SET anotherColumn = 1
```



... but it's not so!



```text
(3 row(s) affected)
```



The constraint does not include any reference to "anotherColumn", so it does not even get executed. If you don't believe it is so, you can check with Profiler and capture any call to scalard UDFs: you wan't see any in this case.

This means that what Microsoft calls a table level CHECK constraint is something that does not really exist and a better name for it would be "Multicolumn CHECK constraint".

The main thing to keep in mind is that if we want the constraint to check the data regardless of the column getting modified we MUST include ALL the columns of the table in the constraint definition.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (1)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-13073" class="archived-comment"><article><header><strong>daveboltman</strong> <time datetime="2018-09-11T17:15:23Z">September 11, 2018 at 18:15</time></header><section class="archived-comment-content">Brilliant into - thank you.<br><br>It is good to be aware that even including all the columns in the constraint definition, it can still by bypassed under certain conditions. See more or less pages 192 to 212 of Alex Kuznetsov's excellent book Defensive Database Programming (from here <br>https://www.red-gate.com/library/defensive-database-programming)</section></article></li></ol></details>
</div>
