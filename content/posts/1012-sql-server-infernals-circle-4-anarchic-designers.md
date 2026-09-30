---
title: "SQL Server Infernals - Circle 4: Anarchic Designers"
date: "2015-07-07T18:06:27"
slug: "sql-server-infernals-circle-4-anarchic-designers"
source_url: "http://spaghettidba.com/2015/07/07/sql-server-infernals-circle-4-anarchic-designers/"
url: "/2015/07/07/sql-server-infernals-circle-4-anarchic-designers/"
categories: ["SQL Server Infernals"]
tags: ["Business Rules", "CHECK constraint", "Database Design", "FOREIGN KEY constraint", "SQL Server", "Worst Practices", "constraints"]
---

<img class="alignnone size-full wp-image-976" src="/wp-content/uploads/2015/06/infernals1.png" alt="Infernals" width="604" height="158" />

Constraints are sometimes annoying in real life, but no society can exist without rules and regulations. The same concept is found in Database Design: no good data can exist without constraints.
<h2>What they say in Heaven</h2>
Constraints define what is acceptable in the database and what does not comply with business rules. In Heaven, where the perfect database runs smoothly, no constraint is overlooked and all the data obeys to the rules of angels:
<ul>
	<li>Every column accepts only the data it was meant for, using the appropriate data type</li>
	<li>Every column that requires a value has a NOT NULL constraint</li>
	<li>Every column that references a key in a different table has a FOREIGN KEY constraint</li>
	<li>Every column that must comply with a business rule has a CHECK constraint</li>
	<li>Every column that must be populated with a predefined value has a DEFAULT constraint</li>
	<li>Every table has a PRIMARY KEY constraint</li>
	<li>Every group of columns that does not accept duplicate values has a UNIQUE constraint</li>
</ul>
<h2>Chaos belongs to hell</h2>
OK: Heaven is Heaven, but what about hell? Let’s see what will get you instant damnation:

<a href="/wp-content/uploads/2015/07/anarchy.png"><img class="alignnone size-full wp-image-1013" src="/wp-content/uploads/2015/07/anarchy.png" alt="Anarchy" width="326" height="309" /></a>
<ol>
	<li><strong>Using the wrong data type</strong>: we already found out that the <a href="/2015/07/02/sql-server-infernals-circle-3-shaky-typers/">SQL Server hell is full of Shaky Typers</a>. The data type is the first constraint on your data: choose it carefully.</li>
</ol>
<ol start="2">
	<li><strong>No PRIMARY KEY constraints</strong>: In the relational model, tables have primary keys. Without a primary key, a table is not even a table (exception made for staging tables and other temporary objects). Do you want duplicate data and unusable data? Go on and drop your primary key.</li>
</ol>
<ol start="3">
	<li><strong>NULL and NOT NULL used interchangeably</strong>: NOT NULL is a constraint on your data: failing to mark required columns with NOT NULL will inevitably mean that you’ll end up having missing information in your rows. At the same time, marking all columns as NOT NULL will bring garbage data in the database, because users will start using dummy data to circumvent the stupid constraint. We already met these sinners in the <a href="/2015/06/17/sql-server-infernals-row-1-undernormalizers/">First Circle of the SQL Server hell</a>.</li>
</ol>
<ol start="4">
	<li><strong>No Foreign Key constraints</strong>: Foreign Keys can be annoying, because they force you to modify the database in the correct order, but following the rules pays off. Without proper constraints, what would happen if you tried to delete from a lookup table a key referenced in other tables? Unfortunately, it would work, silently destroying the correctness of your data.
What would happen if you tried to sneak in a row that references a non-existing key? Again, it would bring in invalid data.</li>
</ol>
<ol start="5">
	<li><strong>No CHECK constraints: </strong>Many columns have explicit or implicit constraints: failing to add them to the database schema means that values forbidden by the business rules will start to flow into the database. Some constraints are implicit, but equally important as the explicit ones. For instance:
<ul>
	<li>an order should never be placed in a future date</li>
	<li>a stock quantity should never be negative</li>
	<li>a ZIP code should only contain numeric characters</li>
	<li>a Social Security Number should be exactly 9 digits long</li>
</ul>
</li>
</ol>
<ol start="6">
	<li><strong>Relying on the application to validate data: </strong>If I had €0.01 for every time I found invalid data in a database and the developers said “the application will guarantee consistency”, I would be blogging from my castle in Mauritius. Maybe the application can guarantee consistency for the data that it manipulates (and it won’t, trust me), but it can do nothing for other applications using the same database. Often the database is a hub for many applications, each with its own degree of complexity and each with its level of quality. Pretending that all these applications will independently guarantee that no invalid data is brought in is totally unrealistic.</li>
</ol>
<strong> </strong>The last circle of SQL Server hell dedicated to Database Design sins is the circle of Inconsistent Baptists, those who fail to comply to sensible naming conventions. Stay tuned!
