---
title: "A short-circuiting edge case"
date: "2011-03-03T23:40:52"
slug: "a-short-circuiting-edge-case"
source_url: "http://spaghettidba.com/2011/03/03/a-short-circuiting-edge-case/"
url: "/2011/03/03/a-short-circuiting-edge-case/"
categories: ["SQL Server", "T-SQL"]
tags: ["Short-Circuit"]
---

Bart Duncan (<a title="Bart Duncan" href="http://bartduncansql.wordpress.com/" target="_blank">blog</a>) found a very strange <a title="Don’t depend on expression short circuiting in T-SQL (not even with CASE)" href="http://bartduncansql.wordpress.com/2011/03/03/dont-depend-on-expression-short-circuiting-in-t-sql-not-even-with-case/" target="_blank">edge case for short-circuiting</a> and commented on my article on sqlservercentral.

In my opinion it should be considered a bug. <a title="CASE (Transact-SQL)" href="http://msdn.microsoft.com/en-us/library/ms181765.aspx" target="_blank">BOL </a>says it clearly:
<blockquote><strong>Searched CASE expression:</strong>
<ul>
	<li>Evaluates, in the order specified, Boolean_expression for each WHEN clause.</li>
	<li><strong>Returns result_expression of the first Boolean_expression that evaluates to TRUE.</strong></li>
	<li>If no Boolean_expression evaluates to TRUE, the Database Engine returns the else_result_expression if an ELSE clause is specified, or a NULL value if no ELSE clause is specified.</li>
</ul>
</blockquote>
What makes Bart's example weird, is the fact that the ITVF seems to be the only scenario where the ELSE branch of the expression gets evaluated:



```sql
-- Autonomous T-SQL batch: everything runs just fine
DECLARE @input int
SELECT @input = 0
SELECT calculated_value =
    CASE
        WHEN @input <= 0 THEN 0
        ELSE LOG10 (@input)
    END
GO

-- Scalar function: runs fine
CREATE FUNCTION dbo.test_case_short_circuit2 (@input INT)
RETURNS int
AS BEGIN
RETURN (
    SELECT calculated_value =
        CASE
            WHEN @input <= 0 THEN 0
            ELSE LOG10 (@input)
        END
)
END
GO

SELECT dbo.test_case_short_circuit2 (-1);
GO
```



However, short-circuiting should never be something to rely upon: whenever there's an alternative way to express the statement, I suggest using it.

<strong>2011/03/04 UPDATE:</strong>

Paul White (<a href="http://sqlblog.com/blogs/paul_white/">blog </a>| <a href="http://twitter.com/#!/sql_kiwi">twitter</a>) agrees to consider this as a bug:
<blockquote>It is constant-folding at work. If you replace the literal constant zero with a variable, the problem no longer occurs. SQL Server expands the in-line TVF at optimization time and fully evaluates the CASE with the constant values available.
Constant-folding should never cause an error condition (such as an overflow) at compilation time - there have been other bugs in this area fixed for the same reason.</blockquote>
More details on the <a href="http://www.sqlservercentral.com/Forums/FindPost1073068.aspx">discussion thread of my article</a>.
