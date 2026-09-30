---
title: "Convert a Trace File from SQLServer 2012 to SQLServer 2008R2"
date: "2012-11-07T00:55:45"
slug: "convert-trace-file-sqlserver2012-2008r"
source_url: "http://spaghettidba.com/2012/11/07/convert-trace-file-sqlserver2012-2008r/"
url: "/2012/11/07/convert-trace-file-sqlserver2012-2008r/"
categories: ["SQL Server", "T-SQL"]
tags: ["Ostress", "Profiler", "RML Utilities", "ReadTrace", "SQLServer", "Trace"]
---

Recently I started using RML utilities quite a lot.

ReadTrace and Ostress are awesome tools for benchmarking and baselining and many of the features found there have not been fully implemented in SQLServer 2012, though Distributed Replay was a nice addition.

However, as you may have noticed, <a title="RML Utilities and SQL Server 2012" href="http://www.scarydba.com/2012/10/16/rml-utilities-and-sql-server-2012/">ReadTrace is just unable to read trace files from SQLServer 2012</a>, so you may get stuck with a trace file you wont' abe able to process.

When I first hit this issue, I immediately thought I could use a trace table to store the data and then use Profiler again to write back to a trace file.

The idea wasn't bad, but turns out that Profiler 2012 will always write trace files in the new format, with no way to specify the old one. On the other hand, Profiler2008R2 can't read trace data from a table written by Profiler2012, throwing an ugly exception:

<a href="/wp-content/uploads/2012/11/porfilererror.png"><img class="alignnone size-full wp-image-526" title="PorfilerError" alt="" src="/wp-content/uploads/2012/11/porfilererror.png" height="253" width="492" /></a>

Interesting! So, looks like Profiler stores version information and other metadata somewhere in the trace table, but where exactly?

It might sound funny, but I had to trace Profiler with Profiler in order to know! Looking at the profiler trace, the first thing that Profiler does when trying to open a trace table is this:



```sql
declare @p1 int
set @p1=180150003
declare @p3 int
set @p3=2
declare @p4 int
set @p4=4
declare @p5 int
set @p5=-1
exec sp_cursoropen @p1 output,N'select BinaryData from [dbo].[trace_test] where RowNumber=0',@p3 output,@p4 output,@p5 output
select @p1, @p3, @p4, @p5
```



So, looks like Profiler stores its metadata in the first row (RowNumber = 0), in binary format.

That was the clue I was looking for!

I loaded a trace file in the old format into another trace table and I started to compare the data to find similarities and differences.

I decided to break the binary headers into Dwords and paste the results in WinMerge to hunt the differences:



```sql
-- Break the header row in the trace table into DWords
-- in order to compare easily in WinMerge
SELECT SUBSTRING(data, 8 * (n - 1) + 3, 8) AS dword
	,n AS dwordnum
FROM (
	SELECT CONVERT(VARCHAR(max), CAST(binarydata AS VARBINARY(max)), 1) AS data
	FROM tracetable
	WHERE rownumber = 0
	) AS src
INNER JOIN (
	SELECT DISTINCT ROW_NUMBER() OVER (
			ORDER BY (SELECT NULL)
		) / 8 AS n
	FROM sys.all_columns AS ac
	) AS v
	ON n > 0 AND (n - 1) * 8 <= LEN(data) - 3
ORDER BY 2
```



If you copy/paste the output in WinMerge you can easily spot the difference around the 100th dword:

<a href="/wp-content/uploads/2012/11/winmerge.png"><img class="alignnone size-full wp-image-527" title="WinMerge" alt="" src="/wp-content/uploads/2012/11/winmerge.png" height="354" width="498" /></a>

Hmmmm, seems promising. Can those "11" and "10" possibly represent the trace version? Let's try and see.
Now we should just update that section of the header to let the magic happen:



```sql
-- Use a table variable to cast the trace
-- header from image to varbinary(max)
DECLARE @header TABLE (
	header varbinary(max)
)

-- insert the trace header into the table
INSERT INTO @header
SELECT binarydata
FROM tracetable
WHERE RowNumber = 0

-- update the byte at offset 390 with version 10 (SQLServer 2008)
-- instead of version 11 (SQLServer 2012)
UPDATE @header
SET header .WRITE(0x0A,390,1)

-- write the header back to the trace table
UPDATE tracetable
SET binarydata = (SELECT header FROM @header)
WHERE RowNumber = 0
```



The trace table can now be opened with Profiler2008R2 and written back to a trace file. Hooray!
Yes, I know, using a trace table can take a whole lot of time and consume a lot of disk space when the file is huge (and typically RML traces are), but this is the best I could come up with.
I tried to look into the trace file itself, but I could not find a way to diff the binary contents in an editor. You may be smarter than me a give it a try: in that case, please, post a comment here.

Using this trick, ReadTrace can happily process the trace file and let you perform your benchmarks, at least until Microsoft decides to update RML Utilities to 2012.
<blockquote><em><strong>UPDATE 11/08/2012:</strong></em><strong> <i>The use of a trace table is not necessary: the trace file can be updated in place, using the script found <a title="More on converting Trace Files" href="/2012/11/08/more-on-converting-trace-files/">here</a>.</i></strong></blockquote>
