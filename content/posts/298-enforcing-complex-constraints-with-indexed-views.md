---
title: "Enforcing Complex Constraints with Indexed Views"
date: "2011-08-03T16:55:33"
slug: "enforcing-complex-constraints-with-indexed-views"
source_url: "http://spaghettidba.com/2011/08/03/enforcing-complex-constraints-with-indexed-views/"
url: "/2011/08/03/enforcing-complex-constraints-with-indexed-views/"
categories: ["SQL Server"]
tags: ["Business Rules", "Indexed Views", "check", "constraints"]
---

Some days ago I blogged about a weird behaviour of “table-level” CHECK constraints. You can find that post <a href="/2011/07/27/table-level-check-constraints/">here</a>.

Somehow, I did not buy the idea that a CHECK with a scalar UDF or a trigger were the only possible solutions. Scalar UDFs are dog-slow and also <a href="http://sqlserverperformance.wordpress.com/2008/06/19/sql-server-dml-triggers-are-evil/">triggers are evil</a>.

I also read <a href="http://www.devx.com/dbzone/Article/34479">this interesting article</a> by Alexander Kuznetsov (<a href="http://sqlblog.com/blogs/alexander_kuznetsov/default.aspx">blog</a>) and some ideas started to flow.

Scalar UDFs are dog-slow because the function gets invoked RBAR (Row-By-Agonizing-Row, for those that don’t know this “<a href="/2011/07/29/exceptional-dba-awards-2011/">Modenism</a>”). If the UDF performs data access, the statement in the scalar function gets invoked for each row, hitting performance badly.

Triggers are evil, according to Glenn Berry (<a href="http://sqlserverperformance.wordpress.com/">blog</a>|<a href="http://twitter.com/#!/GlennAlanBerry">twitter</a>), because they are a “bad” way to implement referential integrity. Moreover, from a performance standpoint, even if triggers work with sets instead of rows (unlike UDFs), they fire an additional query (or even more than one).

However, I seem to have found a way to merge the “business logic” query plan into the same execution plan of the external DML statement that modifies the data.

The method I will discuss here makes use of Indexed Views.

First of all, we will need some tables.

<a href="/wp-content/uploads/2011/08/orders.png"><img class="alignnone size-full wp-image-302" title="orders" src="/wp-content/uploads/2011/08/orders.png" alt="" width="604" /></a>

And now some business rules:
<ol>
	<li>Users with a premium account can place orders with an unlimited total amount. Users with a normal account can place orders limited to a $1000 total amount.</li>
	<li>Minors cannot buy products in the ‘ADULT’ category.</li>
</ol>
Let’s create the tables and populate them with some sample data:



```sql
USE tempdb;
GO

-- Create users table
CREATE TABLE Users (
        user_id int PRIMARY KEY,
        user_name nvarchar(30) NOT NULL,
        birth_date date
)
GO

CREATE TABLE AccountTypes (
        account_type_id int PRIMARY KEY,
        account_type_code char(3) NOT NULL UNIQUE,
        account_type_description nvarchar(255) NOT NULL
)
GO

-- Create account table
CREATE TABLE Accounts (
        account_id int PRIMARY KEY,
        user_id int FOREIGN KEY REFERENCES Users(user_id),
        balance decimal(10,2),
        account_type_id int FOREIGN KEY REFERENCES AccountTypes(account_type_id)
)
GO

-- Create product categories table
CREATE TABLE ProductCategories (
        product_category_id int PRIMARY KEY,
        product_category_code char(5) NOT NULL UNIQUE,
        product_category_description nvarchar(255) NOT NULL
)
GO

-- Create products table
CREATE TABLE Products (
        product_id int PRIMARY KEY,
        EAN_code char(18) NOT NULL,
        product_description nvarchar(255) NOT NULL,
        product_category_id int FOREIGN KEY REFERENCES ProductCategories(product_category_id),
)
GO

-- Create orders table
CREATE TABLE Orders (
        order_id int PRIMARY KEY,
        user_id int FOREIGN KEY REFERENCES Users(user_id),
        total_amount decimal(10,2) NOT NULL CHECK(total_amount > 0),
        order_date datetime NOT NULL
)
GO

-- Create order details table
CREATE TABLE OrderDetails (
        order_id int NOT NULL FOREIGN KEY REFERENCES Orders(order_id),
        order_line int NOT NULL CHECK(order_line > 0),
        product_id int NOT NULL FOREIGN KEY REFERENCES Products(product_id),
        quantity int NOT NULL CHECK(quantity > 0),
        PRIMARY KEY(order_id, order_line)
)
GO

-- Insert sample data
INSERT INTO Users(user_id, user_name, birth_date)
        VALUES (1, N'Gianluca Sartori', '1977-11-25') –- This is me
INSERT INTO Users(user_id, user_name, birth_date)
        VALUES (2, N'Mladen Prajdić',   '1980-08-16') -- I suspect this is not Mladen’s birthday
INSERT INTO Users(user_id, user_name, birth_date)
        VALUES (3, N'Giulia Sartori',   '2009-07-02') -- This is my 2 year old baby girl
INSERT INTO AccountTypes(account_type_id, account_type_code, account_type_description)
        VALUES (1, 'NOR', N'Normal account')
INSERT INTO AccountTypes(account_type_id, account_type_code, account_type_description)
        VALUES (2, 'PRE', N'Premium account')

INSERT INTO Accounts(account_id, user_id, balance, account_type_id) VALUES (1, 1, 520, 2)
INSERT INTO Accounts(account_id, user_id, balance, account_type_id) VALUES (2, 2, 376, 2)
INSERT INTO Accounts(account_id, user_id, balance, account_type_id) VALUES (3, 3, 31,  1)

INSERT INTO ProductCategories(product_category_id, product_category_code, product_category_description)
        VALUES (1, 'MSCCD', N'Music CDs')
INSERT INTO ProductCategories(product_category_id, product_category_code, product_category_description)
        VALUES (2, 'TOONS', N'Disney Cartoons')
INSERT INTO ProductCategories(product_category_id, product_category_code, product_category_description)
        VALUES (3, 'ADULT', N'Adult stuff')

INSERT INTO Products(product_id, EAN_code, product_description, product_category_id)
        VALUES (1, 'MMFAFGRCDGKDGQEJ10', N'AC/DC – Back in Black', 1)
INSERT INTO Products(product_id, EAN_code, product_description, product_category_id)
        VALUES (2, 'DD245FS6D3KBNSDWNF', N'Finding Nemo', 2)
INSERT INTO Products(product_id, EAN_code, product_description, product_category_id)
        VALUES (3, 'B87S0NFDKSDFSAP2IS', N'Pics of hot chicks with little or no clothes to share with your friends on Twitter', 3)
```



Now that sample data is ready, let’s enforce the business rule #1: orders from users with a normal account must be limited to $1000.
To achieve this, we have to create an additional “dummy” table that holds exactly two rows. This table exists with the only purpose to implement a cartesian product and violate a UNIQUE constraint in the indexed view.



```sql
-- Create dummy table to store exactly two rows
CREATE TABLE TwoRows (
        N int NOT NULL PRIMARY KEY
)

INSERT INTO TwoRows VALUES(1)
INSERT INTO TwoRows VALUES(2)
GO
```



Everything is ready to create the view and the UNIQUE index bound to it:



```sql
CREATE VIEW CHECK_Orders_Amount
WITH SCHEMABINDING
AS
SELECT 1 AS ONE
FROM dbo.Orders AS ORD
INNER JOIN dbo.Accounts AS ACCT
        ON ORD.user_id = ACCT.user_id
INNER JOIN dbo.AccountTypes AS ACTY
        ON ACCT.account_type_id = ACTY.account_type_id
CROSS JOIN dbo.TwoRows AS TR
WHERE ORD.total_amount >= 1000
        AND ACTY.account_type_code <> 'PRE'

GO

CREATE UNIQUE CLUSTERED INDEX IX_CHECK_Orders_Accounts ON dbo.CHECK_Orders_Amount(ONE)
GO
```



We can now insert some sample data to test if the business rule gets enforced:



```sql
-- Insert order #1 for user #1 (me) and total amount $2500. Works.
INSERT INTO Orders (order_id, user_id, total_amount, order_date) VALUES (1, 1, 2500.00, GETDATE())
-- Insert order #2 for user #2 (Mladen) and total amount $500. Works
INSERT INTO Orders (order_id, user_id, total_amount, order_date) VALUES (2, 2, 500.00, GETDATE())

-- Insert order #3 for user #3 (My 2 year-old daughter) and total amount $5000. OUCH! Violates the UNIQUE constraint.
INSERT INTO Orders (order_id, user_id, total_amount, order_date) VALUES (3, 3, 5000.00, GETDATE())
-- Insert order #3 for Giulia with total amount $100. Works
INSERT INTO Orders (order_id, user_id, total_amount, order_date) VALUES (3, 3, 100.00, GETDATE())
```



If we look at the execution plan of the INSERT statements, we can see that the indexed view maintenance is merged into the INSERT query plan:

<a href="/wp-content/uploads/2011/08/insert_sqlplan.jpg"><img class="alignleft size-full wp-image-302" title="insert_sqlplan" src="/wp-content/uploads/2011/08/insert_sqlplan.jpg" alt="" width="604" height="242" /></a>

It may be interesting to note that SQL Server is smart enough to identify the statements that require updating the indexed view. For instance, if we try to update a column that is not used in the indexed view, we won’t see any index maintenance in the query plan.
For instance, we could update order_id and examine the query plan:



```sql
-- This statement does not update the indexed view, so it is not included in the plan
UPDATE Orders SET order_id = 3 WHERE order_id = 2
GO
```



<a href="/wp-content/uploads/2011/08/update_sqplplan.png"><img class="alignleft size-full wp-image-303" title="update_sqplplan" src="/wp-content/uploads/2011/08/update_sqplplan.png" alt="" width="604" height="200" /></a>

As you can see, there is no need to maintain the index on the view. To achieve the same with a trigger, you would have to explicitly define the behaviour of the code using IF UPDATE(ColumnName).
Moreover, the UNIQUE constraint gets evaluated whenever ANY table used in the indexed view gets modified: this would be very hard to achieve with a trigger.

Now that the first business rule is set, we can proceed with the second one: no ‘ADULT’ products can be ordered by minors.
This can get a tricky requirement, as we might be tempted to calculate the age of the user comparing it to GETDATE(). Unfortunately, non-deterministic functions cannot be used in indexed views. We will have to get around it by using the order_date column, that was set to GETDATE() previously.



```sql
CREATE VIEW CHECK_Orders_Adult
WITH SCHEMABINDING
AS
SELECT 1 AS ONE
FROM dbo.Orders AS ORD
CROSS JOIN dbo.TwoRows
INNER JOIN dbo.OrderDetails AS ODT
        ON ORD.order_id = ODT.order_id
INNER JOIN dbo.Products AS PR
        ON ODT.product_id = PR.product_id
INNER JOIN dbo.ProductCategories AS PRC
        ON PR.product_category_id = PRC.product_category_id
INNER JOIN dbo.Users AS USR
        ON ORD.user_id = USR.user_id
WHERE PRC.product_category_code = 'ADULT'
        AND DATEADD(year, 18, USR.birth_date) > ORD.order_date
GO

CREATE UNIQUE CLUSTERED INDEX IX_CHECK_Orders_Adult ON dbo.CHECK_Orders_adult(ONE)
GO
```



With the constraint in place, we can try to verify if the business rule gets enforced:



```sql
-- I order the AC/DC album. I will listen to it in my car while driving.
INSERT INTO OrderDetails (order_id, order_line, product_id, quantity) VALUES (1, 1, 1, 1)
-- Mladen orders the hot chicks DVD to send the pics via Twitter.
INSERT INTO OrderDetails (order_id, order_line, product_id, quantity) VALUES (2, 1, 3, 1)
-- Giulia tries to buy the hot chicks DVD as well. She likes boobs. For the milk, I suspect.
-- Fortunately, the INSERT statement fails.
INSERT INTO OrderDetails (order_id, order_line, product_id, quantity) VALUES (3, 1, 3, 1)
-- OK, Giulia: you'd better buy a Disney DVD
INSERT INTO OrderDetails (order_id, order_line, product_id, quantity) VALUES (3, 1, 2, 1)
```


<h2>Conclusion</h2>
Indexed Views provide an elegant way to enforce business rules that go beyond the scope of a single row in a table, without the kludge of CHECK constraints with scalar UDFs or the pain of DML triggers.
However, some limitations apply:
<ul>
	<li>Not all queries can be expressed in a way that can be used in an Indexed View. You can’t use non-deterministic functions, common table expressions, subqueries or self joins.</li>
	<li>Indexed Views cannot perform cross-database queries. If the business rule must be verified against a table stored in a different database, this method cannot be used.</li>
</ul>
Picking the right tool among CHECK constraints and triggers can be a hard decision. But now, hopefully, you have another option. ;-)

<strong>P.S.</strong> : Mladen Prajdić (<a href="http://weblogs.sqlteam.com/mladenp/">blog</a>|<a href="http://www.twitter.com/MladenPrajdic">twitter</a>) kindly gave his blessing to the publishing of this post.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (12)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-578" class="archived-comment"><article><header><strong>Dukagjin Maloku</strong> <time datetime="2011-08-04T07:52:07Z">August 4, 2011 at 08:52</time></header><section class="archived-comment-content">Great stuff, thanks for sharing!</section></article></li><li id="wordpress-comment-919" class="archived-comment"><article><header><strong>Jeff Moden</strong> <time datetime="2011-08-31T01:43:37Z">August 31, 2011 at 02:43</time></header><section class="archived-comment-content">I REALLY like the "TwoRows" trick, Gianluca.  Nicely done.<br><br>As a bit of a sidebar, you could substitute the following as a subquery instead of making a separate table...<br><br>CROSS JOIN (SELECT 1 UNION ALL SELECT 2) TwoRows (N)<br><br>Of course, you could always use a Tally Table. ;-)</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-921" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2011-08-31T07:47:46Z">August 31, 2011 at 08:47</time></header><section class="archived-comment-content">Thanks, Jeff! Glad you liked the trick.<br>Also, thank you for your suggestion. I agree that (SELECT 1 UNION ALL SELECT 2) would have been nicer, but, unfortunately, some restrictions apply when coding views for materialization. Subqueries and UNIONs are on the forbidden constructs list.<br>I didn't test it, but I suspect that a permanent Tally table (typically 11000 rows) could make performance slightly worse than a dummy two-row table. I would have to check.</section></article></li></ol></li><li id="wordpress-comment-922" class="archived-comment"><article><header><strong>Jeff Moden</strong> <time datetime="2011-08-31T13:10:06Z">August 31, 2011 at 14:10</time></header><section class="archived-comment-content">Ah... dang it... I forgot about those restrictions.  Thanks for the correction, Gianluca.</section></article></li><li id="wordpress-comment-1718" class="archived-comment"><article><header><strong>Dan Jackiels</strong> <time datetime="2013-05-16T12:40:10Z">May 16, 2013 at 13:40</time></header><section class="archived-comment-content">Awesome stuff thanks. Got stuck with the exact same problem and didn't want to use triggers , UDFs etc to enforce the constraint. This worked beautifully.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1720" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2013-05-16T13:05:39Z">May 16, 2013 at 14:05</time></header><section class="archived-comment-content">Great! Glad I could help.</section></article></li></ol></li><li id="wordpress-comment-11692" class="archived-comment"><article><header><strong>94Enrique</strong> <time datetime="2017-08-13T01:54:01Z">August 13, 2017 at 02:54</time></header><section class="archived-comment-content">Hi blogger, i must say you have very interesting articles here.<br>Your website should go viral. You need initial traffic <br>boost only. How to get it? Search for; Mertiso's tips go viral</section></article></li><li id="wordpress-comment-12354" class="archived-comment"><article><header><strong>Dennes Torres</strong> <time datetime="2018-03-29T07:59:15Z">March 29, 2018 at 08:59</time></header><section class="archived-comment-content">Hi, Gianluca!<br><br>Is this method still valid nowadays, after when had updates on the query optimizer and even adaptive query tuning, both affecting UDF's?<br><br>Do you have some method to deal with the danger of an indexed view? I already faced a situation where a system in production stopped because an indexed view (it blocks DML with different set options), so, do you have some method to deal with this kind of danger?<br><br>Thank you!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12355" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-03-29T09:33:37Z">March 29, 2018 at 10:33</time></header><section class="archived-comment-content">This method still works, even on the newer versions of the optimizer. I did not check whether the changes of behaviour on UDFs improved the performance or not.<br><br>Regarding the indexed views, it's indeed dangerous to create them in production without extensive testing. The same applies to filtered indexes. It's a shame, because both these tuning measures would come handy in many situations, but I tend to avoid them unless I can test thoroughly.</section></article></li></ol></li><li id="wordpress-comment-38773" class="archived-comment"><article><header><strong>Mike Amsler</strong> <time datetime="2022-01-26T17:28:42Z">January 26, 2022 at 18:28</time></header><section class="archived-comment-content">The fact that this is the only place I've ever seen this blows my mind. I've been using this method for a couple years now (found it on your blog) and it just seems superior to using triggers in every way. Less error prone then writing triggers, in lining the logic into one query plan. I tell people about this and they look at my like I'm crazy until I start showing them benchmark performance test.</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-38774" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2022-01-26T17:30:49Z">January 26, 2022 at 18:30</time></header><section class="archived-comment-content">Ha! Thanks for the feedback!</section></article></li></ol></li><li id="wordpress-comment-45990" class="archived-comment"><article><header><strong>Caiden Craig</strong> <time datetime="2026-09-16T18:40:35Z">September 16, 2026 at 19:40</time></header><section class="archived-comment-content"><br><p>This is a very interesting approach to implementing business logic.</p><br></section></article></li></ol></details>
</div>
