---
title: "SQL Server Infernals - Circle 2: Generalizers"
date: "2015-06-24T23:10:18"
slug: "sql-server-infernals-circle-2-generalizers"
source_url: "http://spaghettidba.com/2015/06/24/sql-server-infernals-circle-2-generalizers/"
url: "/2015/06/24/sql-server-infernals-circle-2-generalizers/"
categories: ["SQL Server", "SQL Server Infernals"]
tags: ["Database Design", "EAV", "Worst Practices", "normalization"]
---

<img class="alignnone size-full wp-image-976" src="/wp-content/uploads/2015/06/infernals1.png" alt="Infernals" width="604" height="158" />

Object-Oriented programming taught us that generalizing is a good thing and, whenever possible, we should do it. Complex class hierarchies are a good way of reusing code, hitting the specialized classes only when a special implementation is needed.

In the database world, the concept doesn’t play exactly well.
<h2>What they say in Heaven</h2>
In Heaven, there is a lookup table for each attribute, no matter how simple and no matter how small is the lookup table.

For instance, if your database is about sales, you probably have a Customers table and an Orders table, each with its own attributes resolved through a Foreign Key. The lookup tables are usually very small, with just a handful of rows in them:

<a href="/wp-content/uploads/2015/06/lookup_good.png"><img class="alignnone size-full wp-image-1000" src="/wp-content/uploads/2015/06/lookup_good.png" alt="lookup_good" width="604" height="288" /></a>
<h2>Temptation comes from our own desires</h2>
Wouldn’t that be great if you could stop adding small, insignificant tables to your database schema? Wouldn’t it be a lot easier if you had ONE table to store all that lookup nonsense? “Less is more” after all, isn’t it?

If you had a “<a href="https://www.simple-talk.com/blogs/2008/05/29/when-the-fever-is-over-and-ones-work-is-done/">One True Lookup Table</a>”, everything would be more elegant and simple. Look at this database schema:

<a href="/wp-content/uploads/2015/06/lookup_bad.png"><img class="alignnone size-full wp-image-1001" src="/wp-content/uploads/2015/06/lookup_bad.png" alt="lookup_bad" width="604" height="415" /></a>

Isn’t it elegant and clean?

Whenever you need a new lookup table, you just have to add rows to your <a href="https://www.simple-talk.com/blogs/2008/05/29/when-the-fever-is-over-and-ones-work-is-done/">OTLT™</a> (thanks <a href="https://twitter.com/Phil_Factor">Phil Factor</a> for the acronym):



```sql
INSERT INTO LookupTable
    (table_name, lookup_code, lookup_description)
VALUES
    ('Order_Status', 'OP', 'Open'),
    ('Order_Status', 'CL', 'Closed'),
    ('Order_Status', 'SH', 'Shipped');
```



<h2>Devil’s in the details</h2>
You may have less tables to deal with now, but there’s a price to pay. A bigger price than you would have expected.
<ol>
	<li><strong>No foreign keys</strong>: Did you notice that the foreign keys are gone? In order to create a foreign key, you would have to add the lookup table name to the Orders and Customers tables, for each attribute stored in the lookup table. I don’t think you would like it.</li>
</ol>
<ol start="2">
	<li><strong>Generic data type</strong>: In order to merge all lookup tables in one, you need to choose a “generic” data type that fits for all. The most generic data type is a character-based type, so you’ll probably end up with a huge nvarchar column. You probably don’t want the same huge column in the referencing tables and you could end up having different data types between the main tables and the lookups. One more not-so-good idea. Moreover, when you’re joining your tables with the lookup table, you will have implicit (or explicit) conversions happening, which is a performance nightmare.</li>
	<li><strong>Single Hotspot</strong>: Instead of hitting multiple tables for lookups, everyone will hit the same table over and over. This will create a hotspot in the database, with locking and latching issues all over the place.</li>
</ol>
<ol start="4">
	<li><strong>Acrobatic constraints: </strong>Defining constraints on a generic table becomes very difficult. Not an impossible deal, but very difficult. For the schema in this example, you could define a CHECK constraint to enforce the use of the correct data type, but the syntax of the constraint will not be very straightforward:



```sql
CHECK(
    CASE
        WHEN lookup_code = 'states'     AND lookup_code LIKE '[A-Z][A-Z]'      THEN 1
        WHEN lookup_code = 'priorities' AND lookup_code LIKE '[0-9]'           THEN 1
        WHEN lookup_code = 'countries'  AND lookup_code LIKE '[0-9][0-9][0-9]' THEN 1
        WHEN lookup_code = 'status'     AND lookup_code LIKE '[A-Z][A-Z]'      THEN 1
        ELSE 0
    END = 1
)
```



</li>
</ol>
<h2>It could get even worse</h2>
As soon as you start to realize that trading multiple lookup tables for an OTLT is not a good deal, devil will raise the bid and offer the ultimate generalization: the Entity Attribute Value, also known as “EAV”.

If you come to think of it, who needs fixed attributes in a table when you can have as many attributes as you want in a general-purpose table? Why messing with ALTER TABLE statements when you can have a single table that can store an infinite number of attributes that you can bind to any row in any table?

A typical EAV schema looks like this:

<a href="/wp-content/uploads/2015/06/eav.png"><img class="alignnone size-full wp-image-1002" src="/wp-content/uploads/2015/06/eav.png" alt="EAV" width="597" height="573" /></a>

This way, you can have any type of attribute bound to your main entities. For instance, to define a “ship_date” attribute in your Orders table, you just have to insert a couple of rows in your EAV schema:



```sql
INSERT INTO Entities
    (entity_id, entity_name)
VALUES
    (1, 'Orders');

INSERT INTO AttributeNames
    (attribute_id, entity_id, attribute_name)
VALUES
    (1, 1, 'ship_date');

INSERT INTO AttributeValues
    (attribute_id, entity_id, id, value)
VALUES
    (1, 1, 123, '2015-06-24 22:10:00.000');
```



Looks like a great idea, doesn’t it? Unfortunately, it is not.
<ol>
	<li><strong>Generic data types:</strong> again, what would prevent a date such as ‘2015-02-30 18:30:00.000’ from being assigned to the ship date? Uh-oh: nothing.</li>
</ol>
<ol start="2">
	<li><strong>No foreign keys: </strong>again, enforcing foreign key constraints would be impossible.</li>
</ol>
<ol start="3">
	<li><strong>A single hotspot in the database: </strong>every attribute for every table involved in this nonsense would have to be looked up in the same table.</li>
</ol>
<ol start="4">
	<li><strong>No constraints: </strong>how would you enforce a constraint as simple as “NOT NULL”? Good luck with that.</li>
</ol>
<ol start="5">
	<li><strong>Dreadful reporting queries: </strong>when you will be asked to create a report on a table that uses this paradigm (I said “when”, not “if”, because it <strong>will</strong> happen), you will have to OUTER JOIN to the EAV table for each and every attribute that you want to retrieve. In case you are wondering if this is good or bad, take into account that the optimizer starts to freak out when it finds too many JOINS in a query and will likely timeout looking for a decent execution plan, feeding you the best it could come up with (usually, a mess).</li>
</ol>
<h2>It depends?</h2>
Some software solutions are entirely based on user-defined attributes and the ability to define them is a central feature. For instance, many CRM solutions are heavily dependent on user-defined attributes. However, there are many ways to achieve the same results without resorting to an EAV design. For instance, one could wonder why ALTERing the database schema seems to be a less desirable solution.

There are also many flavors of EAV, with different degrees of evil involved. Some implementations at least provide different columns for different data types, some others use XML or JSON.

The EAV design comes with the intent of solving a real world problem that doesn’t have a definitive answer in the relational model. In partial defense of the “generalizers”, it has to be said that this is a challenging problem. Nevertheless, like Dante put his political enemies to hell, I am the “poet” and I’m afraid that the generalizers will have to get accustomed to sulfur. It just takes a couple of thousand years, after all.
<h2>Who will be damned next?</h2>
In the next circle of the SQL Server hell we will meet the shaky typers – the poor souls that chose the wrong data types for their columns. Stay tuned for more!

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (1)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-8028" class="archived-comment"><article><header><strong>suxstellino (Alessandro Alpi)</strong> <time datetime="2015-06-25T07:26:23Z">June 25, 2015 at 08:26</time></header><section class="archived-comment-content">Reblogged this on <a href="https://suxstellino.wordpress.com/2015/06/25/sql-server-infernals-circle-2-generalizers/" rel="nofollow ugc noopener noreferrer">Alessandro Alpi's Blog</a>.</section></article></li></ol></details>
</div>
