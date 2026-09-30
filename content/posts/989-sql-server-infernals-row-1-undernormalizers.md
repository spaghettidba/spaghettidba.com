---
title: "SQL Server Infernals – Circle 1: Undernormalizers"
date: "2015-06-17T17:34:32"
slug: "sql-server-infernals-row-1-undernormalizers"
source_url: "http://spaghettidba.com/2015/06/17/sql-server-infernals-row-1-undernormalizers/"
url: "/2015/06/17/sql-server-infernals-row-1-undernormalizers/"
categories: ["SQL Server", "SQL Server Infernals"]
tags: ["Database Design", "Worst Practices", "normalization"]
---

<img class="alignnone size-full wp-image-976" src="/wp-content/uploads/2015/06/infernals1.png" alt="Infernals" width="604" height="158" />

There’s a special place in the SQL Server Hell for those who design their schema without following the Best Practices. In this first episode of SQL Server Infernals, we will explore together the Row of the Poor Schema Designers, also known as “undernormalizers”.
<h2>What they say in Heaven</h2>
In Heaven, where all Best Practices are followed and everything runs smoothly while angels sing, they design their databases following the rules of normalization. Once upon a time, there was a man who spent a considerable amount of his life working on defining the rules of the relational model. That man was <a href="https://en.wikipedia.org/wiki/Edgar_F._Codd">Edgar Codd</a>.

Mr. Codd laid down the rules of normalization, which are known as “normal forms”. The normal forms define the attributes of a well-designed database schema. While there are more normal forms, it is widely accepted that a schema is normalized when it follows the first three normal forms. Here is the simplest possible enunciations of each:
<blockquote style="width:100%;">
<ul>
	<li>1NF – Every relation has a primary key, every relation contains only atomic attributes</li>
	<li>2NF – 1NF + Every attribute in a relation depends on the whole key</li>
	<li>3NF – 2NF + Every attribute in a relation depends only on the key</li>
</ul>
In a single line: <em>“The key, the whole key, nothing but the key (so help me Codd)”</em>.</blockquote>
<h2>Clues you’re doing it wrong</h2>
<ul>
	<li>Repeating data (redundancies): the same information has to be saved in multiple places</li>
	<li>Inconsistent data between tables (anomalies): the same information has different values in different tables</li>
	<li>Data separated by commas</li>
	<li>Structured data in “note” columns</li>
	<li>Columns with a numeric suffix (e.g. Zone1, Zone2, Zone3…)</li>
</ul>
<h2><img class="alignnone wp-image-990 size-full" src="/wp-content/uploads/2015/06/databasedesign.png" alt="databasedesign" width="604" height="222" /></h2>
<h2>What will put you to hell</h2>
<ol>
	<li><strong>No primary key</strong>: did you notice that the normal forms talk about “relations” rather than “tables”? The relational model is a mathematical model, which, at some point has to be translated to a physical implementation. Tables are exactly this: the physical implementation of relations.
If your table has no primary key and relations must have a primary key, chances are that your table is the physical implementation of something else (a bin, a pile, a bag… whatever: not a relation anyway).
When tables have no primary key, any data can be stored inside them, even duplicate rows. Once duplicate data is inside the table, there is no way to tell which row is good and which one is the duplicate.</li>
</ol>
<ol start="2">
	<li><strong>Surrogate keys only</strong>: this is in fact a variation on the “no primary key” sin: if your table has a surrogate key (such as an identity or uniqueidentifier column), make sure that it is not the only unique key in the table, otherwise you will end up storing duplicates, with only the surrogate key as a difference. This is no different from having no primary key at all.
If you decide that your table is best implemented with a surrogate key (often because the natural key is composite or too wide), make sure that you create a UNIQUE constraint on the natural key.</li>
</ol>
<ol start="3">
	<li><strong>Non-atomic attributes</strong>: if your table has columns that contain multiple values, the likelihood of a design mistake goes to the roof. For instance, when you find data such as “sales@company.com,marketing@company.com” in a “email” column, chances are that the designer of the database forgot to take into account that the entity (for instance a customer) might have multiple email addresses.
While <a href="http://www.sqlservercentral.com/articles/Tally+Table/72993/">many efficient split algorithms are available</a>, storing the data in this format has many downsides:
<ul>
	<li>Indexing individual items is impossible</li>
	<li>Searching for individual items is hard</li>
	<li>Updating an item requires writing the whole comma separated value</li>
	<li>Locking a single item is impossible (reduced concurrency)</li>
	<li>CHECK constraints are hard to implement</li>
</ul>
Whenever you find non-atomic attributes, be prepared to refactor the database schema, because something is really wrong and there is no way to fix it without moving the attribute to a different table.</li>
</ol>
<ol start="4">
	<li><strong>Use of NULL when not necessary: </strong>NULL is a constraint on the data: if an attribute is mandatory, make it mandatory! Allowing NULLs on mandatory data will open the door to data that does not meet the business rules. What are you doing with rows that are missing mandatory attributes?
If your table has too many NULLs in it, you probably have designed it wrong and you are trying to fit too many attributes in a single table (an implicit dependency?): move them to a separate table.</li>
</ol>
<ol start="5">
	<li><strong>Use of dummy data: </strong>The other side of the coin is “no NULLs allowed anywhere”. Not all attributes are mandatory: if you pretend it is so, the users will start putting dummy data into your columns to work around the restriction. Typical examples are “.” or empty strings for character-based columns and “0” for numeric-based columns. Once those dummy values are in, can you tell the difference between “dummy” zeros and “real” zeros? Of course you can’t.</li>
</ol>
<ol start="6">
	<li><strong>Designing the database when specs are incomplete/unclear:</strong> This is the worst of all mistakes. Changing the database schema once it is in production is a bloodbath: everything built on top of that schema will have to change. Many of the design mistakes described above are the consequence of incomplete specifics or lack of analysis.
It is discouraging to note how some popular design patterns do not take into account the intrinsic complexity of refactoring a database schema and demand the implementation of the schema to automated tools, based on the object classes that represent the domain. Yes, I’m talking about you, Code First. In my book, “code first” is a synonym of “design someday”. Don’t let any automated tool design your database schema: you know better than that!</li>
</ol>
<ol start="7">
	<li><strong>Premature denormalization: </strong>some devil’s advocates will tell you that normalization slows down the database and that you should be denormalizing your schema from the start. Don’t believe what they say! Most normalized schemas can cope with sustained reads and SQL Server offers many features (such as indexed views) to deal with high numbers of joins, which is usually the point for denormalization. Of course, if you're working on a BI project, denormalization is expected and desirable instead.
An old saying goes: “Normalize ‘til it hurts, then denormalize ‘til it works”, but there's nothing preventing the database from working on a normalized schema. If reads on the database are slow, it is quite unlikely that the cause is over-normalization: it is much more presumable that your queries and/or your indexes <del>suck</del> are sub-optimal.</li>
</ol>
In the next episode of SQL Server Infernals I will discuss a particular database design sin: the dynamic schema. Stay tuned for more.
