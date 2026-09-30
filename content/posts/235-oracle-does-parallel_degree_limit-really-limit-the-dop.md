---
title: "Oracle: does PARALLEL_DEGREE_LIMIT really limit the DOP?"
date: "2011-07-20T15:04:48"
slug: "oracle-does-parallel_degree_limit-really-limit-the-dop"
source_url: "http://spaghettidba.com/2011/07/20/oracle-does-parallel_degree_limit-really-limit-the-dop/"
url: "/2011/07/20/oracle-does-parallel_degree_limit-really-limit-the-dop/"
categories: ["Oracle"]
tags: ["parallel execution", "parallel_degree_limit", "parallel_degree_policy"]
---

<h1><span class="Apple-style-span" style="font-size:13px;font-weight:normal;">Understanding Oracle Parallel Execution in 11.2 is a pain, not because the topic itself is overly complex, rather because Oracle made it much more complicated than it needed to be.</span></h1>
Basically, the main initialization parameter that controls the parallel execution is PARALLEL_DEGREE_POLICY.

According to <a href="http://download.oracle.com/docs/cd/E14072_01/server.112/e10820/initparams173.htm">Oracle online documentation</a>, this parameter can be set to:
<blockquote>
<ul>
	<li><strong>MANUAL:</strong> Disables automatic degree of parallelism, statement queuing, and in-memory parallel execution. This reverts the behaviour of parallel execution to what it was prior to Oracle Database 11<em>g</em> Release 2 (11.2). This is the default.</li>
	<li><strong>AUTO:</strong> Enables automatic degree of parallelism, statement queuing, and in-memory parallel execution.</li>
	<li><strong>LIMITED:</strong> Enables automatic degree of parallelism for some statements but statement queuing and in-memory Parallel Execution are disabled. Automatic degree of parallelism is only applied to those statements that access tables or indexes decorated explicitly with the PARALLEL clause. Tables and indexes that have a degree of parallelism specified will use that degree of parallelism.</li>
</ul>
</blockquote>
<strong>MANUAL</strong>

Using the manual degree policy means that tables and indexes decorated with the PARALLEL clause are accessed using the DOP specified on the object (either default or explicit). The default DOP is CPU_COUNT * PARALLEL_THREADS_PER_CPU.

When a query gets parallelized, the physical access plan is sliced into separate threads, called <em>parallel slaves</em>, that, in turn, consume a <em>parallel server</em> each. When all the parallel servers are exhausted (or there are less parallel servers available than the ones requested) the queries start getting downgraded to a lower DOP.

<strong>AUTO</strong>

This means that Oracle will choose the appropriate DOP to access tables and indexes, based on the size of the objects to read and on the HW resources in the system. Appropriate could also mean 1 (no parallel execution), but, if your tables are quite big, “appropriate” will typically mean default.

Setting this option will also mean that the queries will not be downgraded, but they get queued until all the requested parallel servers are available. This allows complex queries that highly benefit from a parallel plan to execute using all the available resources, but also means that the execution times for the same statement can vary a lot between different runs.

Another interesting feature activated by this setting is the in-memory parallel execution. When using the MANUAL setting, data is read directly from disk and not from the buffer cache. That makes sense, because it does not generate buffer cache latch contention and also because typically parallelism kicks in when scanning big tables that wouldn’t fit in the buffer cache anyway.

However, nowadays server machines are packed with lots of RAM and seeing databases that fit entirely in the buffer cache is not so uncommon. The AUTO degree policy enables reading data blocks directly from the buffer cache when appropriate, which could turn into a great performance enhancement.

<strong>LIMITED</strong>

The third option was probably meant to be a mix of the first two, but turns out to be the “child of a lesser god”, with a poor, half-backed implementation. The idea behind is to limit the maximum degree of parallelism allowed for a query, using the PARALLEL_DEGREE_LIMIT initialization parameter, that can be set to a numeric value or left to the default (CPU). Moreover, both statement queuing and in-memory parallel execution are disabled, and the automatic DOP is used only when accessing tables explicitly decorated with the PARALLEL clause.

What is really confusing is the scope of the degree limit, which is described very poorly in the documentation.

The “automatic DOP” is a plan scoped attribute and it is turned on only when at least one of the tables accessed by the query is decorated explicitly with the PARALLEL clause. With “PARALLEL”, Oracle means PARALLEL (DEGREE DEFAULT) and not a fixed DOP. When all the tables in the query are decorated with a fixed degree, the automatic DOP is turned off and the limit gets totally ignored. Under these circumstances, each table is accessed using the DOP it is decorated with, which could be higher or lower than the degree limit.

When at least one of the tables in the query is decorated with a default degree, the automatic DOP is turned on and the degree of parallelism will be capped by the PARALLEL_DEGREE_LIMIT. According to Oracle, all tables decorated with an explicit DOP should use that degree of parallelism, but it is not so: when the automatic DOP kicks in, it is always limited by the degree limit, even when accessing a table with a higher explicit DOP.
<h2>Seeing is believing:</h2>
Let’s try to demonstrate this odd behaviour.

This is the CPU configuration for the instance I will use for the test:

<strong> <a href="/wp-content/uploads/2011/07/parameter_cpu.png"><img class="alignnone size-full wp-image-239" title="parameter_cpu" alt="" src="/wp-content/uploads/2011/07/parameter_cpu.png" height="146" width="472" /></a></strong>

It’s a virtual machine with 4 cores and the instance is configured to use 2 threads per CPU. With this setup, the default DOP is 8.

<a href="/wp-content/uploads/2011/07/parameter_parallel.png"><img class="alignnone size-full wp-image-240" title="parameter_parallel" alt="" src="/wp-content/uploads/2011/07/parameter_parallel.png" height="400" width="472" /></a>

PARALLEL_DEGREE_POLICY is set to “LIMITED” and PARALLEL_DEGREE_LIMIT is set to 4. Both initialization parameters can be set at session scope.

Let’s create a test table holding 10 million rows of data:



```sql
CREATE TABLE TenMillionRows AS
WITH TenRows AS (
	SELECT 1 AS N FROM DUAL
	UNION ALL
	SELECT 2 FROM DUAL
	UNION ALL
	SELECT 3 FROM DUAL
	UNION ALL
	SELECT 4 FROM DUAL
	UNION ALL
	SELECT 5 FROM DUAL
	UNION ALL
	SELECT 6 FROM DUAL
	UNION ALL
	SELECT 7 FROM DUAL
	UNION ALL
	SELECT 8 FROM DUAL
	UNION ALL
	SELECT 9 FROM DUAL
	UNION ALL
	SELECT 10 FROM DUAL
)
SELECT ROW_NUMBER() OVER(ORDER BY A.N) AS N,
	A.N AS A, B.N AS B, C.N AS C, D.N AS D,
E.N AS E, F.N AS F, G.N AS G
FROM TenRows A
CROSS JOIN TenRows B
CROSS JOIN TenRows C
CROSS JOIN TenRows D
CROSS JOIN TenRows E
CROSS JOIN TenRows F
CROSS JOIN TenRows G;
```



Also, let’s make sure that the table gets accessed using a parallel plan:



```sql
ALTER TABLE TenMillionRows PARALLEL(DEGREE DEFAULT);
```



To complete the test, we will also need a second test table:



```sql
CREATE TABLE HundredMillionRows AS
WITH TenRows AS (
	SELECT N
	FROM TenMillionRows
	WHERE N <= 10
)
SELECT A.*
FROM TenMillionRows A
CROSS JOIN TenRows B;

ALTER TABLE HundredMillionRows PARALLEL(DEGREE DEFAULT);
```



Now that we have a couple of test tables, we can use them to see how they get accessed by queries.

As a first attempt, we set the limit to ‘CPU’, which means the default DOP (8 in this particular setup).



```sql
ALTER SESSION SET PARALLEL_DEGREE_POLICY = 'LIMITED';

ALTER SESSION SET PARALLEL_DEGREE_LIMIT = 'CPU';

SELECT COUNT(*)
FROM HundredMillionRows A
INNER JOIN TenMillionRows B
    ON A.N = B.N;

SELECT * FROM v$pq_sesstat;
```



<a href="/wp-content/uploads/2011/07/height7.png"><img class="alignnone size-full wp-image-242" title="height7" alt="" src="/wp-content/uploads/2011/07/height7.png" height="207" width="527" /></a>

Oracle decided to access the tables using a DOP 7.

Now, if we limit the DOP with a lower PARALLEL_DEGREE_LIMIT, we should see the limit enforced:



```sql
ALTER SESSION SET PARALLEL_DEGREE_LIMIT = '4';

SELECT COUNT(*)
FROM HundredMillionRows A
INNER JOIN TenMillionRows B
    ON A.N = B.N;

SELECT * FROM v$pq_sesstat;
```



<a href="/wp-content/uploads/2011/07/height4.png"><img class="alignnone size-full wp-image-243" title="height4" alt="" src="/wp-content/uploads/2011/07/height4.png" height="207" width="527" /></a>

In fact, no surprises here: we get an allocation height of 4 due to the degree limit.

What would happen if we set a fixed degree of parallelism on the tables?



```sql
ALTER TABLE HundredMillionRows PARALLEL(DEGREE 6);
ALTER TABLE TenMillionRows     PARALLEL(DEGREE 3);
```



With both tables using a fixed DOP, according to the documentation, we should see the explicit DOP used:



```sql
SELECT COUNT(*)
FROM HundredMillionRows A
INNER JOIN TenMillionRows B
    ON A.N = B.N;

SELECT * FROM v$pq_sesstat;
```



<a href="/wp-content/uploads/2011/07/height6.png"><img class="alignnone size-full wp-image-244" title="height6" alt="" src="/wp-content/uploads/2011/07/height6.png" height="207" width="527" /></a>

Once again, no surprises: the degree limit gets ignored because both tables are decorated with an explicit fixed DOP.
However, the true reason behind this behaviour is not the explicit DOP on the tables, but the fact that no other table in the query uses a default DOP.

Let’s see what happens if we change the degree of parallelism for one of the tables:



```sql
ALTER TABLE TenMillionRows PARALLEL(DEGREE DEFAULT);
```



Now, joining HundredMillionRows with TenMillionRows will produce a different allocation height:



```sql
SELECT COUNT(*)
FROM HundredMillionRows A
INNER JOIN TenMillionRows B
    ON A.N = B.N;

SELECT * FROM v$pq_sesstat;
```



<a href="/wp-content/uploads/2011/07/height4_2.png"><img class="alignnone size-full wp-image-245" title="height4_2" alt="" src="/wp-content/uploads/2011/07/height4_2.png" height="207" width="527" /></a>

The reason for this is that the degree limit is enforced only when the automatic DOP kicks in, which happens only when at least one table in the query is decorated with the PARALLEL(DEGREE DEFAULT) clause.

This is really annoying, because the DOP defined on a table does not determine the real DOP used to access that table, which instead is determined by the DOP defined on <span style="text-decoration:underline;">another</span> table.

This makes the query optimizer behave in a totally unpredictable manner: you get manual DOP when all tables use a fixed parallel clause and you get limited DOP when at least one table uses the parallel default clause.
<h2>Workaround:</h2>
The only way to really limit the parallelism on all tables is to use the resource manager.

You set it up with:



```sql
exec dbms_resource_manager.clear_pending_area();
exec dbms_resource_manager.create_pending_area();
exec dbms_resource_manager.create_plan( plan =>; 'LIMIT_DOP', comment => 'Limit Degree of Parallelism');
exec dbms_resource_manager.create_plan_directive(plan=> 'LIMIT_DOP', group_or_subplan => 'OTHER_GROUPS' , comment => 'limits the parallelism', parallel_degree_limit_p1=> 4);
exec dbms_resource_manager.validate_pending_area();
exec dbms_resource_manager.submit_pending_area();
```



You switch it on with:



```sql
alter system set resource_manager_plan = 'LIMIT_DOP' sid='*';
```



You switch it off with:



```sql
alter system reset resource_manager_plan sid='*';
alter system set resource_manager_plan = '' sid='*';
```



And drop it afterwards with:



```sql
exec dbms_resource_manager.clear_pending_area();
exec dbms_resource_manager.create_pending_area();
exec dbms_resource_manager.delete_plan_cascade('LIMIT_DOP')
exec dbms_resource_manager.validate_pending_area();
exec dbms_resource_manager.submit_pending_area();
```


<h2>What Oracle says:</h2>
I filed a bug with Oracle support a long time ago and their feedback is, as usual, disappointing.

<a href="https://support.oracle.com/CSP/main/article?cmd=show&amp;type=BUG&amp;id=11933336&amp;productFamily=Oracle">https://support.oracle.com/CSP/main/article?cmd=show&amp;type=BUG&amp;id=11933336&amp;productFamily=Oracle</a>
<a href="/wp-content/uploads/2011/07/doc_bug1.png"><img class="alignnone size-full wp-image-257" title="doc_bug" alt="" src="/wp-content/uploads/2011/07/doc_bug1.png" height="155" width="580" /></a>

I find this reply disappointing for at least three reasons:
<ol start="1">
	<li>They decided to change the documentation instead of fixing the code</li>
	<li>The text they suggested to fix the documentation is wrong and even more misleading than before</li>
	<li>The documentation has not been changed yet</li>
</ol>
<h2>Conclusions:</h2>
Oracle provides three different policies for parallelism: AUTO, MANUAL and LIMITED.
AUTO and MANUAL have their upsides and downsides, but both reflect the behaviour described in the documentation.
LIMITED is a mix of AUTO and MANUAL, but behaves in a very strange and undocumented way and I suggest avoiding it, unless you reset all tables to PARALLEL(DEGREE DEFAULT).
