---
title: "Oracle BUG: UNPIVOT returns wrong data for non-unpivoted columns"
date: "2011-03-09T10:08:27"
slug: "oracle-bug-unpivot-returns-wrong-data-for-non-unpivoted-columns"
source_url: "http://spaghettidba.com/2011/03/09/oracle-bug-unpivot-returns-wrong-data-for-non-unpivoted-columns/"
url: "/2011/03/09/oracle-bug-unpivot-returns-wrong-data-for-non-unpivoted-columns/"
categories: ["Oracle"]
tags: ["BUG", "UNPIVOT"]
---

Some bugs in Oracle's code are really surprising. Whenever I run into this kind of issue, I can't help but wonder how nobody else noticed it before.

Some days ago I was querying AWR data from DBA_HIST_SYSMETRIC_SUMMARY and I wanted to turn the columns AVERAGE, MAXVAL and MINVAL into rows, in order to fit this result set into a performance graphing application that expects input data formatted as {TimeStamp, SeriesName, Value}.

Columns to rows? A good match for UNPIVOT.

Oracle 11g introduced PIVOT and UNPIVOT operators to allow rows-to-columns and columns-to-rows transformations. Prior to 11g, this kind of transformation had to be coded with bulky CASE expressions (for PIVOT) or pesky UNION queries (for UNPIVOT). PIVOT and UNPIVOT allow developers to write more concise and readable statements, but I guess that not so many people have been using these features since their release, or they would have found this bug very soon.

Here is the statement I was trying to run:



```sql
WITH Metrics AS (
    SELECT to_date(to_char(BEGIN_TIME,'YYYY-MM-DD HH24'),'YYYY-MM-DD HH24') AS TS,
        AVG(AVERAGE) AS AVERAGE,
        MAX(MAXVAL) AS MAXVAL,
        MIN(MINVAL) AS MINVAL
    FROM DBA_HIST_SYSMETRIC_SUMMARY
    WHERE METRIC_NAME = 'Host CPU Utilization (%)'
    GROUP BY to_date(to_char(BEGIN_TIME,'YYYY-MM-DD HH24'),'YYYY-MM-DD HH24')
)
SELECT TS, aggregate, value
FROM Metrics
UNPIVOT (value FOR aggregate IN (AVERAGE, MAXVAL, MINVAL))
ORDER BY 1
```



The idea behind was to convert the date column into a string without the minute part, in order to convert it back to date and group by hour.

Surprisingly enough, this was the result:

<a href="/wp-content/uploads/2011/03/unpivot11.png"><img class="alignnone size-full wp-image-60" title="Wrong results with UNPIVOT" src="/wp-content/uploads/2011/03/unpivot11.png" alt="Wrong results with UNPIVOT" width="408" height="468" /></a>

The date column was returned with wrong data. Why?

The issue seems to be related to the date datatype, because converting back to date <strong><em>after</em></strong> the UNPIVOT works just fine:



```sql
WITH Metrics AS (
    SELECT to_char(BEGIN_TIME,'YYYY-MM-DD HH24') AS TS,
        AVG(AVERAGE) AS AVERAGE,
        MAX(MAXVAL) AS MAXVAL,
        MIN(MINVAL) AS MINVAL
    FROM DBA_HIST_SYSMETRIC_SUMMARY
    WHERE METRIC_NAME = 'Host CPU Utilization (%)'
    GROUP BY to_char(BEGIN_TIME,'YYYY-MM-DD HH24')
)
SELECT to_date(TS,'YYYY-MM-DD HH24') AS TS, aggregate, value
FROM Metrics
UNPIVOT (value FOR aggregate IN (AVERAGE, MAXVAL, MINVAL))
ORDER BY 1
```



This query, instead, produces the expected results.

<a href="/wp-content/uploads/2011/03/unpivot2.png"><img class="alignnone size-full wp-image-61" title="Correct data with char column" src="/wp-content/uploads/2011/03/unpivot2.png" alt="Correct data with char column" width="408" height="501" /></a>

I raised this issue with Oracle Support who filed it under bug ID <a title="Oracle Support" href="https://support.oracle.com:443/CSP/ui/flash.html#tab=KBHome(page=KBHome&amp;id=()),(page=KBNavigator&amp;id=(from=BOOKMARK&amp;bmDocDsrc=DOCUMENT&amp;bmDocID=9900850.8&amp;bmDocTitle=Bug%209900850%20-%20UNPIVOT%20returns%20corrupt%20data%20for%20columns%20not%20in%20the%20UNPIVOT%20operation&amp;viewingMode=1143&amp;bmDocType=PATCH))" target="_blank">9900850.8</a>. Both 11.2.0.1 and 11.2.0.2 seem to be be affected by this problem, but it's quite unlikely to see it fixed before 12.1.

Time will tell.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (4)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-1198" class="archived-comment"><article><header><strong>Mor</strong> <time datetime="2012-05-31T08:54:32Z">May 31, 2012 at 09:54</time></header><section class="archived-comment-content">Hi,<br><br>Thanks for letting us know about the UNPIVOT+DATE data type bug, I just received similar behavior on 11.2.0.2 where all date columns returned as null after unpivoting.<br><br>According to the bug you posted, this issue is fixed in 11.2.0.3<br>I guess we'll test it sooner or later. until then we'll use the to_char/to_date trick.<br><br>Great work!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1199" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2012-05-31T16:08:24Z">May 31, 2012 at 17:08</time></header><section class="archived-comment-content">I'm glad I could help.<br>Thanks for your feedback and for letting me know about the fix in 11.2.0.3!</section></article></li></ol></li><li id="wordpress-comment-1478" class="archived-comment"><article><header><strong>GMan</strong> <time datetime="2013-02-15T17:31:35Z">February 15, 2013 at 18:31</time></header><section class="archived-comment-content">Thank you for posting this, we have a similar proble with unpivot on 11.2.0.2 where comparing a date from an unpivot with a date from another table.  If we put a trunc or an nvl or even add 0 to either of the dates the compare works otherwise it wont.  Migth be worth trying.</section></article></li><li id="wordpress-comment-31823" class="archived-comment"><article><header><strong>Rogerio Moreira Pereira</strong> <time datetime="2019-12-24T17:15:56Z">December 24, 2019 at 18:15</time></header><section class="archived-comment-content">This issue remains...</section></article></li></ol></details>
</div>
