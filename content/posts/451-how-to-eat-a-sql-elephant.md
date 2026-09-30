---
title: "How to Eat a SQL Elephant in 10 Bites"
date: "2012-03-15T14:04:12"
slug: "how-to-eat-a-sql-elephant"
source_url: "http://spaghettidba.com/2012/03/15/how-to-eat-a-sql-elephant/"
url: "/2012/03/15/how-to-eat-a-sql-elephant/"
categories: ["SQL Server", "T-SQL"]
tags: ["Optimization", "SQL", "Tuning"]
---

<div>

One byte at a time, obviously!



<figure id="attachment_457" class="wp-caption alignnone" style="width: 500px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/eat_the_sql_elephant.png"><img class="size-full wp-image-457" title="eat_the_sql_elephant" src="/wp-content/uploads/2012/03/eat_the_sql_elephant.png" alt="" width="500" height="308" /></a>
<figcaption class="wp-caption-text">No elephants were harmed during photoshopping.</figcaption>
</figure>



</div>
Sometimes, when you have to optimize a poor performing query, you may find yourself staring at a huge statement, wondering where to start.

Some developers think that a single elephant statement is better than multiple small statements, but this is not always the case.

Let’s try to look from the perspective of software quality:
<ul>
	<li>Efficiency
The optimizer will likely come up with a suboptimal plan, giving up early on optimizations and transformations.</li>
	<li>Reliability
Any slight change in statistics could lead the optimizer to produce a different and less efficient plan.</li>
	<li>Maintainability
A single huge statement is less readable and maintainable than multiple small statements.</li>
</ul>
With those points in mind, the only sensible thing to do is cut the elephant into smaller pieces and eat them one at a time.



<figure id="attachment_458" class="wp-caption alignnone" style="width: 604px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/original.png"><img class="size-full wp-image-458" title="original" src="/wp-content/uploads/2012/03/original.png" alt="" width="604" height="242" /></a>
<figcaption class="wp-caption-text">What should I do with this query??</figcaption>
</figure>



This is how I do it:
<ol>
	<li>Lay out the original code and read the statement carefully</li>
	<li>Decide whether a full rewrite is more convenient</li>
	<li>Set up a test environment</li>
	<li>Identify the query parts
<ul>
	<li>Identify the main tables</li>
	<li>Identify non correlated subqueries and UNIONs</li>
	<li>Identify correlated subqueries</li>
</ul>
</li>
	<li>Write a query outline</li>
	<li>Break the statement into parts with CTEs, views, functions and temporary tables</li>
	<li>Merge redundant subqueries</li>
	<li>Put it all together</li>
	<li>Verify the output based on multiple different input values</li>
	<li>Comment your work thoroughly</li>
</ol>
<div>The queries you will find in the pictures are (in very small part) a MySQL stored procedure I had to rewrite recently, so don't try to run them in SQL Server. The syntax may be different, but the method still stands.</div>
<h3>1.     Lay out the original code and read the statement carefully</h3>
Use one of the many SQL formatters you can find online. My favorite one is Tao Klerk’s <a href="http://www.architectshack.com/PoorMansTSqlFormatter.ashx">Poor Man’s T-SQL Formatter</a>: it’s very easy to use and configure and it comes with a handy SSMS add-in and plugins for Notepad++ and WinMerge. Moreover, it’s free and open source. A must-have.



<figure id="attachment_459" class="wp-caption alignnone" style="width: 511px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/layout.png"><img class="size-full wp-image-459" title="layout" src="/wp-content/uploads/2012/03/layout.png" alt="" width="511" height="901" /></a>
<figcaption class="wp-caption-text">Looks much better now.</figcaption>
</figure>



Once your code is readable, don’t rush to the keyboard: take your time and read it carefully.
<ul>
	<li>Do you understand (more or less) what it is supposed to do?</li>
	<li>Do you think you could have coded it yourself?</li>
	<li>Do you know all the T-SQL constructs it contains?</li>
</ul>
If you answered “yes” to all the above, you’re ready to go to the next step.
<h3>2.     Decide whether a full rewrite is more convenient</h3>
OK, that code sucks and you have to do something. It’s time to make a decision:
<ol>
	<li>Take the business rules behind the statement and rewrite it from scratch
When the statement is too complicated and unreadable, it might be less time-consuming to throw the old statement away and write your own version.
Usually it is quite easy when you know exactly what the code is supposed to do. Just make sure you’re not making wrong assumptions and be prepared to compare your query with the original one many times.</li>
	<li>Refactor the statement
When the business rules are unclear (or unknown) starting from scratch is <strong>not</strong> an option. No, don’t laugh! The business logic may have been buried in the sands of time or simply you may be working on a query without any will to understand the business processes behind it.
Bring a big knife: you’re going to cut the elephant in pieces.</li>
	<li>Leave the statement unchanged
Sometimes the statement is too big or too complicated to bother taking the time to rewrite it. For instance, <a href="http://dl.dropbox.com/u/49603664/BLOG/CODE/monsterQuery.sql">this query</a> would take months to rewrite manually.
It works? Great: leave it alone.</li>
</ol>
<h3>3.     Set up a test environment</h3>
It doesn’t matter how you decide to do it: at the end of the day you will have to compare the results of your rewritten query with the results of the “elephant” and make sure you did not introduce errors in your code.

The best way to do this is to prepare a script that compares the results of the original query with the results of your rewritten version. This is the script I am using (you will find it in the <a href="/code-repository/">code repository</a>, as usual).



```sql
-- =============================================
-- Author:      Gianluca Sartori - spaghettidba
-- Create date: 2012-03-14
-- Description: Runs two T-SQL statements and 
--              compares the results
-- =============================================

-- Drop temporary tables
IF OBJECT_ID('tempdb..#original') IS NOT NULL 
    DROP TABLE #original;

IF OBJECT_ID('tempdb..#rewritten') IS NOT NULL 
    DROP TABLE #rewritten;

-- Store the results of the original 
-- query into a temporary table
WITH original AS (
    <original, text, >
)
SELECT *
INTO #original
FROM original;

-- Add a sort column
ALTER TABLE #original ADD [______sortcolumn] int identity(1,1);



-- Store the results of the rewritten 
-- query into a temporary table
WITH rewritten AS (
    <rewritten, text, >
)
SELECT *
INTO #rewritten
FROM rewritten;

-- Add a sort column
ALTER TABLE #rewritten ADD [______sortcolumn] int identity(1,1);


-- Compare the results
SELECT 'original' AS source, *
FROM (
    SELECT * 
    FROM #original 
    
    EXCEPT 
    
    SELECT * 
    FROM #rewritten
) AS A

UNION ALL

SELECT 'rewritten' AS source, *
FROM (
    SELECT * 
    FROM #rewritten 
    
    EXCEPT 
    
    SELECT * 
    FROM #original
) AS B;
```



The script is a SSMS query template that takes the results of the original and the rewritten query and compares the resultsets, returning all the missing or different rows. The script uses two CTEs to wrap the two queries: this means that the ORDER BY predicate (if any) will have to be moved outside the CTE.

Also, the results of the two queries are piped to temporary tables, which means that you can’t have duplicate column names in the result set.

Another thing worth noting is that the statements to compare cannot be stored procedures. One simple way to overcome this limitation is to use the technique I described in <a href="/2011/11/16/discovering-the-output-of-dbcc-commands/">this post</a>.

The queries inside the CTEs should then be rewritten as:



```sql
SELECT *
FROM OPENQUERY(LOOPBACK,'<original, text,>')
```



Obviously, all the quotes must be doubled, which is the reason why I didn’t set up the script this way in the first place. It’s annoying, but it’s the only way I know of to pipe the output of a stored procedure into a temporary table without knowing the resultset definition in advance. If you can do better, suggestions are always welcome.
<h3>4.     Identify the query parts</h3>
OK, now you have everything ready and you can start eating the elephant. The first thing to do is to identify all the autonomous blocks in the query and give them a name. You can do this at any granularity and repeat the task as many times as you like: the important thing is that at the end of this process you have a list of query parts and a name for each part.



<figure id="attachment_460" class="wp-caption alignnone" style="width: 604px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/outline.png"><img class="size-full wp-image-460" title="outline" src="/wp-content/uploads/2012/03/outline.png" alt="" width="604" height="694" /></a>
<figcaption class="wp-caption-text">Identify the main parts and give them a name.</figcaption>
</figure>


<h4>Identify the main tables</h4>
Usually I like the idea that the data comes from one “main” table and all the rest comes from correlated tables. For instance, if I have to return a resultset containing some columns from the “SalesOrderHeader” table and some columns from the “SalesOrderDetail” table, I consider SalesOrderHeader the main table and SalesOrderHeader a correlated table. It fits well with my mindset, but you are free to see things the way you prefer.

Probably these tables are already identified by an alias: note down the aliases and move on.
<h4>Identify non correlated subqueries and UNIONs</h4>
Non-correlated subqueries are considered as inline views. Often these subqueries are joined to the main tables to enrich the resultset with additional columns.

Don’t be scared away by huge subqueries: you can always repeat all the steps for any single subquery and rewrite it to be more compact and readable.

Again, just note down the aliases and move to the next step.
<h4>Identify correlated subqueries</h4>
Correlated subqueries are not different from non-correlated subqueries, with the exception that you will have less freedom to move them from their current position in the query. However, that difference doesn’t matter for the moment: give them a name and note it down.
<h3>5.     Write a query outline</h3>
Use the names you identified in the previous step and write a query outline. It won’t execute, but it gives you the big picture.



<figure id="attachment_461" class="wp-caption alignnone" style="width: 240px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/query_outline.png"><img class="size-full wp-image-461" title="query_outline" src="/wp-content/uploads/2012/03/query_outline.png" alt="" width="240" height="154" /></a>
<figcaption class="wp-caption-text">Won't execute, but describes what the query does.</figcaption>
</figure>



If you really want the big picture, print the query. It may seem crazy, but sometimes I find it useful to be able to see the query as a whole, with all the parts with their names highlighted in different colors.



<figure id="attachment_462" class="wp-caption alignnone" style="width: 484px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/monsterquery_4.jpg"><img class="size-full wp-image-462" title="MonsterQuery_4" src="/wp-content/uploads/2012/03/monsterquery_4.jpg" alt="" width="484" height="662" /></a>
<figcaption class="wp-caption-text">A touch of colour for my office.</figcaption>
</figure>



Yes, that’s a single SELECT statement, printed in Courier new 8 pt. on 9 letter sheets, hanging on the wall in my office.
<h3>6.     Break the statement in parts with CTEs, views, functions and temporary tables</h3>
SQL Server offers a fair amount of tools that allow breaking a single statement into parts:
<ul>
	<li>Common Table Expressions</li>
	<li>Subqueries</li>
	<li>Views</li>
	<li>Inline Table Valued Functions</li>
	<li>Multi-Statement Table Valued Functions</li>
	<li>Stored procedures</li>
	<li>Temporary Tables</li>
	<li>Table Variables</li>
</ul>
Ideally, you will choose the one that performs best in your scenario, but you could also take usability and modularity into account.

CTEs and subqueries are a good choice when the statement they contain is not used elsewhere and there is no need to reuse that code.

Table Valued functions and views, on the contrary, are most suitable when there is an actual need to incapsulate the code in modules to be reused in multiple places.

Generally speaking, you will use temporary tables or table variables when the subquery gets used more than once in the statement, thus reducing the load.



<figure id="attachment_463" class="wp-caption alignnone" style="width: 516px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/cte_outline.png"><img class="size-full wp-image-463" title="cte_outline" src="/wp-content/uploads/2012/03/cte_outline.png" alt="" width="516" height="970" /></a>
<figcaption class="wp-caption-text">A place for everything and everything in its place.</figcaption>
</figure>



Though I would really like to go into deeper details on the performance pros and cons of each construct, that would take an insane amount of time and space. You can find a number of articles and blogs on those topics and I will refrain from echoing them here.
<h3>7.     Merge redundant subqueries</h3>
Some parts of your query may be redundant and you may have the opportunity to merge those parts. The merged query will be more compact and will likely perform significantly better.

For instance, you could have multiple subqueries that perform aggregate calculations on the same row set:



```sql
SELECT ProductID
    ,Name
    ,AverageSellOutPrice = (
        SELECT AVG(UnitPrice)
        FROM Sales.SalesOrderDetail
        WHERE ProductID = PR.ProductID
    )
    ,MinimumSellOutPrice = (
        SELECT MIN(UnitPrice)
        FROM Sales.SalesOrderDetail
        WHERE ProductID = PR.ProductID
    )
    ,MaximumSellOutPrice = (
        SELECT MAX(UnitPrice)
        FROM Sales.SalesOrderDetail
        WHERE ProductID = PR.ProductID
    )
FROM Production.Product AS PR;
```



The above query can be rewritten easily to avoid hitting the SalesOrderDetail table multiple times:



```sql
SELECT ProductID
    ,Name
    ,AverageSellOutPrice
    ,MinimumSellOutPrice
    ,MaximumSellOutPrice
FROM Production.Product AS PR
CROSS APPLY (
    SELECT AVG(UnitPrice), MIN(UnitPrice), MAX(UnitPrice)
    FROM Sales.SalesOrderDetail
    WHERE ProductID = PR.ProductID
) AS SellOuPrices (AverageSellOutPrice, MinimumSellOutPrice, MaximumSellOutPrice);
```



Another typical situation where you can merge some parts is when multiple subqueries perform counts on slightly different row sets:



```sql
SELECT ProductID
    ,Name
    ,OnlineOrders = (
        SELECT COUNT(*)
        FROM Sales.SalesOrderHeader AS SOH
        WHERE SOH.OnlineOrderFlag = 1
            AND EXISTS (
                SELECT *
                FROM Sales.SalesOrderDetail
                WHERE SalesOrderID = SOH.SalesOrderID
                    AND ProductID = PR.ProductID
            )
    )
    ,OfflineOrders = (
        SELECT COUNT(*)
        FROM Sales.SalesOrderHeader AS SOH
        WHERE SOH.OnlineOrderFlag = 0
            AND EXISTS (
                SELECT *
                FROM Sales.SalesOrderDetail
                WHERE SalesOrderID = SOH.SalesOrderID
                    AND ProductID = PR.ProductID
            )
    )
FROM Production.Product AS PR;
```



The only difference between the two subqueries is the predicate on SOH.OnlineOrderFlag. The two queries can be merged introducing a CASE expression in the aggregate:



```sql
SELECT ProductID
    ,Name
    ,ISNULL(OnlineOrders,0) AS OnlineOrders
    ,ISNULL(OfflineOrders,0) AS OfflineOrders
FROM Production.Product AS PR
CROSS APPLY (
    SELECT SUM(CASE WHEN SOH.OnlineOrderFlag = 1 THEN 1 ELSE 0 END),
           SUM(CASE WHEN SOH.OnlineOrderFlag = 0 THEN 1 ELSE 0 END)
    FROM Sales.SalesOrderHeader AS SOH
    WHERE EXISTS (
            SELECT *
            FROM Sales.SalesOrderDetail
            WHERE SalesOrderID = SOH.SalesOrderID
                AND ProductID = PR.ProductID
        )
) AS Orderscount (OnlineOrders, OfflineOrders);
```



There are infinite possibilities and enumerating them all would be far beyond the scope of this post. This is one of the topics that my students often find hard to understand and I realize that it really takes some experience to identify merge opportunities and implement them.



<figure id="attachment_464" class="wp-caption alignnone" style="width: 604px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/rewritten.png"><img class="size-full wp-image-464" title="rewritten" src="/wp-content/uploads/2012/03/rewritten.png" alt="" width="604" height="193" /></a>
<figcaption class="wp-caption-text">Hi query, you look very fit. Did you lose weight?</figcaption>
</figure>


<h3>8.     Put it all together</h3>
Remember the query outline you wrote previously? It’s time to put it into action.

Some of the identifiers may have gone away in the merge process, some others are still there and have been transformed into different SQL constructs, such as CTEs, iTVFs or temporary tables.
<h3>9.     Verify the output based on multiple different input values</h3>
Now it’s time to see if your new query works exactly like the original one. You already have a script for that: you can go on and use it.

Remember that the test can be considered meaningful only if you repeat it a reasonably large number of times, with different parameters. Some queries could appear to be identical, but still be semantically different. Make sure the rewritten version handles NULLs and out-of-range parameters in the same way.
<h3>10.Comment your work thoroughly</h3>
If you don’t comment your work, somebody will find it even more difficult to maintain than the elephant you found when you started.

Comments are for free and don’t affect the query performance in any way. Don’t add comments that mimic what the query does, instead, write a meaningful description of the output of the query.

For instance, given a code fragment like this:



```sql
SELECT SalesOrderID, OrderDate, ProductID
INTO #orders
FROM Sales.SalesOrderHeader AS H
INNER JOIN Sales.SalesOrderDetail AS D
    ON H.SalesOrderID = D.SalesOrderID
WHERE OrderDate BETWEEN @StartDate AND @EndDate
```



a comment like “joins OrderHeader to OrderDetail” adds nothing to the clarity of the code. A comment like “Selects the orders placed between the @StartDate and @EndDate and saves the results in a temporary table for later use” would be a much better choice.
<h3>Elephant eaten. (Burp!)</h3>


<figure id="attachment_465" class="wp-caption alignnone" style="width: 604px; max-width: 100%;">
<a href="/wp-content/uploads/2012/03/piccoloprincipe.jpg"><img class="size-full wp-image-465" title="piccoloprincipe" src="/wp-content/uploads/2012/03/piccoloprincipe.jpg" alt="" width="604" height="260" /></a>
<figcaption class="wp-caption-text">If you don't see a hat, sorry: you're getting old.</figcaption>
</figure>



After all, it was not too big, was it?

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (9)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-1056" class="archived-comment"><article><header><strong>Dukagjin Maloku</strong> <time datetime="2012-03-15T13:32:24Z">March 15, 2012 at 14:32</time></header><section class="archived-comment-content">Very nice post, my friend!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1057" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2012-03-15T13:34:34Z">March 15, 2012 at 14:34</time></header><section class="archived-comment-content">Thank you very much, Dugi. Glad you liked it.;-)</section></article></li></ol></li><li id="wordpress-comment-1058" class="archived-comment"><article><header><strong>ismapro</strong> <time datetime="2012-03-15T18:10:04Z">March 15, 2012 at 19:10</time></header><section class="archived-comment-content">Great Post... Really necessary for some job i been doing lately...</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1059" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2012-03-15T18:13:04Z">March 15, 2012 at 19:13</time></header><section class="archived-comment-content">Thanks! You're very kind.</section></article></li></ol></li><li id="wordpress-comment-1060" class="archived-comment"><article><header><strong>Tracy Hamlin</strong> <time datetime="2012-03-15T18:19:21Z">March 15, 2012 at 19:19</time></header><section class="archived-comment-content">Awesome!  Yeah, I hate it when someone hands me a giant, ugly query and then hovers over my shoulder waiting for my to wave the magic wand!  These things can take some time . . . :)</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1061" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2012-03-15T18:26:06Z">March 15, 2012 at 19:26</time></header><section class="archived-comment-content">It definitely takes some time and it's worth every minute IMHO.<br>People don't like the idea of rewriting something that WORKS, but 90% of the tuning opportunities lies there. Physical optimizazions like indexes and indexed views can mitigate the effect of bad SQL, but nothing like a good rewrite can help performance.</section></article></li></ol></li><li id="wordpress-comment-1074" class="archived-comment"><article><header><strong>Jeff Moden</strong> <time datetime="2012-04-04T23:46:40Z">April 5, 2012 at 00:46</time></header><section class="archived-comment-content">That's one heck of a blog entry you have there, ol' friend.  And very nicely done, as well!  Thanks for taking the time to help others.  Lots of special "sauce" to help the SQL Elephant go down more easily.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1076" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2012-04-05T08:22:38Z">April 5, 2012 at 09:22</time></header><section class="archived-comment-content">Thank you, Jeff.<br>I just tried to blog my personal experience and make a method out of it.<br>Glad you liked it.</section></article></li></ol></li><li id="wordpress-comment-1084" class="archived-comment"><article><header><strong>Eric Russell</strong> <time datetime="2012-04-09T15:10:22Z">April 9, 2012 at 16:10</time></header><section class="archived-comment-content">I don't know how many times I've been called into optimize or debug some database process, and the introduction goes something like this:<br> <br>"The process is actually quite simple, there's this single procedure call ..."</section></article></li></ol></details>
</div>
