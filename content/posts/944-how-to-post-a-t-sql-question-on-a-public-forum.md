---
title: "How to post a T-SQL question on a public forum"
date: "2015-04-24T18:42:10"
slug: "how-to-post-a-t-sql-question-on-a-public-forum"
source_url: "http://spaghettidba.com/2015/04/24/how-to-post-a-t-sql-question-on-a-public-forum/"
url: "/2015/04/24/how-to-post-a-t-sql-question-on-a-public-forum/"
categories: ["SQL Server", "SQL Server Central", "T-SQL"]
tags: ["Forum Question"]
---

If you want to have faster turnaround on your forum questions, you will need to provide enough information to the forum users in order to answer your question.

In particular, talking about T-SQL questions, there are three things that your question <strong>must</strong> include:
<ol>
	<li>Table scripts</li>
	<li>Sample data</li>
	<li>Expected output</li>
</ol>
&nbsp;
<h3><strong>Table Script and Sample data</strong></h3>
Please make sure that anyone trying to answer your question can quickly work on the same data set you’re working on, or, at least the problematic part of it. The data should be in the same place where you have it, which is inside your tables.

You will have to provide a script that creates your table and inserts data inside that table.

Converting your data to INSERT statements can be tedious: fortunately, some tools can do it for you.

How do you convert a SSMS results grid, a CSV file or an Excel spreadsheet to INSERT statements? In other words, how do you convert this...

<a href="/wp-content/uploads/2015/04/table_data.png"><img class="alignnone wp-image-945 size-full" src="/wp-content/uploads/2015/04/table_data.png" alt="table_data" width="336" height="208" /></a>

into this?



```sql
USE [tempdb]
GO

CREATE TABLE [dbo].[Person](
	[BusinessEntityID] [int] NOT NULL PRIMARY KEY CLUSTERED,
	[PersonType] [nchar](2) NOT NULL,
	[FirstName] [nvarchar](50) NOT NULL,
	[LastName] [nvarchar](50) NOT NULL
)

GO

INSERT INTO Person VALUES (6106,'IN','Beth','Carlson');
INSERT INTO Person VALUES (17889,'IN','Dennis','Li');
INSERT INTO Person VALUES (17989,'IN','Brent','Li');
INSERT INTO Person VALUES (9424,'IN','Brad','Raji');
INSERT INTO Person VALUES (5842,'IN','Aimee','She');
INSERT INTO Person VALUES (2144,'GC','Carol','Philips');
INSERT INTO Person VALUES (2582,'IN','Gregory','Tang');
INSERT INTO Person VALUES (2012,'SC','Jian','Wang');
INSERT INTO Person VALUES (12624,'IN','Clayton','She');
INSERT INTO Person VALUES (12509,'IN','Madison','Russell');
GO
```



The easiest way to perform the transformation is to copy all the data and paste it over at <a href="http://www.convertcsv.com/csv-to-sql.htm">ConvertCSV</a>:

<a href="/wp-content/uploads/2015/04/convertcsvtosql_1.png"><img class=" wp-image-953 size-full aligncenter" src="/wp-content/uploads/2015/04/convertcsvtosql_1.png" alt="ConvertCSVToSQL_1" width="604" height="296" /></a>

<a href="/wp-content/uploads/2015/04/convertcsvtosql_2.png"><img class=" wp-image-954 size-full aligncenter" src="/wp-content/uploads/2015/04/convertcsvtosql_2.png" alt="ConvertCSVToSQL_2" width="604" height="236" /></a>

<a href="/wp-content/uploads/2015/04/convertcsvtosql_3.png"><img class=" size-full wp-image-955 aligncenter" src="/wp-content/uploads/2015/04/convertcsvtosql_3.png" alt="ConvertCSVToSQL_3" width="604" height="610" /></a>

Another great tool for this task is <a href="http://sqlfiddle.com/">SQLFiddle</a>.

<strong>OPTIONAL</strong>: The insert statements will include the field names: if you want to make your code more concise, you can remove that part by selecting the column names with your mouse holding the ALT key and then delete the selection. <a href="http://www.brentozar.com/archive/2015/04/ssms-alt-shift-trick/">Here’s a description</a> of how the rectangular selection works in SSMS 2012 and 2014 (doesn’t work in SSMS 2008).
<h3><strong>Expected output</strong></h3>
The expected output should be something immediately readable and understandable. There’s another tool that can help you obtain it.

Go to <a href="https://ozh.github.io/ascii-tables/">https://ozh.github.io/ascii-tables/</a>, paste your data in the "Input" textarea, press “Create Table” and grab your table from the "Output" textarea.<img class="alignnone size-full wp-image-1132" src="/wp-content/uploads/2015/04/text-tables-generator1.png" alt="text tables generator" width="979" height="1009" />Here’s what your output should look like:



```text
+------------+-------------+
| PersonType | PersonCount |
+------------+-------------+
| GC         |           1 |
| IN         |           8 |
| SC         |           1 |
+------------+-------------+
```


<h3><strong>Show what you have tried</strong></h3>
Everybody will be more willing to help you if you show that you have put some effort into solving your problem. If you have a query, include it, even if it doesn’t do exactly what you’re after.

Please please please, format your query before posting! You can format your queries online for free at <a href="http://poorsql.com/">PoorSQL.com</a>

<a href="/wp-content/uploads/2015/04/poormans2.png"><img class=" size-full wp-image-958 aligncenter" src="/wp-content/uploads/2015/04/poormans2.png" alt="PoorMans2" width="604" height="458" /></a>

Simply paste your code then open the “Formatted SQL” tab to grab your code in a more readable way.
<h3><strong>Putting it all together</strong></h3>
Here is what your question should look like when everything is ok:
<blockquote>Hi all, I have a table called Person and I have to extract the number of rows for each person type.

This is the table script and some sample data:



```sql
USE [tempdb]
GO

CREATE TABLE [dbo].[Person](
	[BusinessEntityID] [int] NOT NULL PRIMARY KEY CLUSTERED,
	[PersonType] [nchar](2) NOT NULL,
	[FirstName] [nvarchar](50) NOT NULL,
	[LastName] [nvarchar](50) NOT NULL
)

GO

INSERT INTO Person VALUES (6106,'IN','Beth','Carlson');
INSERT INTO Person VALUES (17889,'IN','Dennis','Li');
INSERT INTO Person VALUES (17989,'IN','Brent','Li');
INSERT INTO Person VALUES (9424,'IN','Brad','Raji');
INSERT INTO Person VALUES (5842,'IN','Aimee','She');
INSERT INTO Person VALUES (2144,'GC','Carol','Philips');
INSERT INTO Person VALUES (2582,'IN','Gregory','Tang');
INSERT INTO Person VALUES (2012,'SC','Jian','Wang');
INSERT INTO Person VALUES (12624,'IN','Clayton','She');
INSERT INTO Person VALUES (12509,'IN','Madison','Russell');
```



This is what I’m trying to obtain:



```text
+------------+-------------+
| PersonType | PersonCount |
+------------+-------------+
| GC         |           1 |
| IN         |           8 |
| SC         |           1 |
+------------+-------------+
```



Here is what I have tried:



```sql
SELECT PersonType
FROM Person
```



How do I do that?</blockquote>
If you include this information in your posts, I promise you will get blazingly fast answers.
