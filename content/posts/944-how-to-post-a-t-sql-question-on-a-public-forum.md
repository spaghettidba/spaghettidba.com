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

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (10)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-7788" class="archived-comment"><article><header><strong>David Sumlin</strong> <time datetime="2015-05-04T18:27:17Z">May 4, 2015 at 19:27</time></header><section class="archived-comment-content">Bravo!  Should be required reading before posting on SO or MSDN forums.</section></article></li><li id="wordpress-comment-7791" class="archived-comment"><article><header><strong>Alex Friedman</strong> <time datetime="2015-05-05T07:42:31Z">May 5, 2015 at 08:42</time></header><section class="archived-comment-content">My bookmarks thank you!</section></article></li><li id="wordpress-comment-7792" class="archived-comment"><article><header><strong>Tony Bater</strong> <time datetime="2015-05-05T10:00:48Z">May 5, 2015 at 11:00</time></header><section class="archived-comment-content">Another great way to turn a set of query results into a set of create table plus insert scripts is to use the SSMS add-on tSQL-Flex available from GitHub https://github.com/nycdotnet/TSqlFlex . This does all the work for you. Just paste your query into the query area, hit  and the script appears in the output pane, together with a convenient button to copy it to the clipboard. Simple! This add-on was described in SqlServerCentral - http://www.sqlservercentral.com/blogs/nycnet/2014/09/08/new-add-on-for-ssms-t-sql-flex</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-7793" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-05-05T10:03:38Z">May 5, 2015 at 11:03</time></header><section class="archived-comment-content">Thanks Tony! I had completely forgotten about TSqlFlex. It's a great add-in.</section></article></li><li id="wordpress-comment-9457" class="archived-comment"><article><header><strong>sateesh</strong> <time datetime="2016-04-26T03:32:32Z">April 26, 2016 at 04:32</time></header><section class="archived-comment-content">Excellent Plugin</section></article></li></ol></li><li id="wordpress-comment-9553" class="archived-comment"><article><header><strong>desperadomar</strong> <time datetime="2016-06-11T09:36:00Z">June 11, 2016 at 10:36</time></header><section class="archived-comment-content">Great formatting tips especially for SO !, but the sensefulsolutions is not working now. I found an alternative solution here http://www.tablesgenerator.com/markdown_tables which is more intuitive.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9554" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2016-06-11T10:29:14Z">June 11, 2016 at 11:29</time></header><section class="archived-comment-content">Thank you! I didn't notice the sensefulsolutions site went down. I will update the post to include some alternatives.</section></article></li></ol></li><li id="wordpress-comment-12123" class="archived-comment"><article><header><strong>kosmik5</strong> <time datetime="2017-12-08T09:00:40Z">December 8, 2017 at 10:00</time></header><section class="archived-comment-content">Hi,<br>Thanks for sharing the great information... Its useful and helpful information…Keep Sharing.<br><br>Thank you<br>Hari</section></article></li><li id="wordpress-comment-12992" class="archived-comment"><article><header><strong>pregunton</strong> <time datetime="2018-07-24T07:46:20Z">July 24, 2018 at 08:46</time></header><section class="archived-comment-content">Great fantastic post !!<br><br>Updates with good alternatives?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12993" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-07-24T08:15:12Z">July 24, 2018 at 09:15</time></header><section class="archived-comment-content">Thanks! I checked all the links and they seem to be working. Are you looking for something in particular?</section></article></li></ol></li></ol></details>
</div>
