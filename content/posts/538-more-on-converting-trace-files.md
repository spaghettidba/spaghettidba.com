---
title: "More on converting Trace Files"
date: "2012-11-08T13:48:37"
slug: "more-on-converting-trace-files"
source_url: "http://spaghettidba.com/2012/11/08/more-on-converting-trace-files/"
url: "/2012/11/08/more-on-converting-trace-files/"
categories: ["SQL Server"]
tags: ["Ostress", "Profiler", "RML Utilities", "ReadTrace", "SQLServer", "Trace"]
---

Yesterday I posted a <a title="Convert a Trace File from SQLServer 2012 to SQLServer2008R2" href="/2012/11/07/convert-trace-file-sqlserver2012-2008r/">method to convert trace files</a> from SQL Server 2012 to SQL Server 2008R2 using a trace table.

As already mentioned in that post, having to load the whole file into a trace table has many shortcomings:
<ul>
	<li>The trace file can be huge and loading it into a trace table could take forever</li>
	<li>The trace data will consume even more space when loaded into a SQL Server table</li>
	<li>The table has to be written back to disk in order to obtain the converted file</li>
	<li>You need to have Profiler 2008 in order to write a trace in the "old" format</li>
	<li>You need to have a SQL Server 2008 instance to dump the trace table back to the file, as Profiler 2008 won't connect to a SQL Server 2012</li>
</ul>
That said, it would really be useful if the file could be updated in place, changing just the version byte...

No worries: <em><strong>PowerShell to the rescue!</strong></em>



```powershell
## =============================================
## Author:      Gianluca Sartori - @spaghettidba
## Create date: 2012-11-07
## Description: Changes the version information
##              in the header of a SQL Server trace
## =============================================
cls

# Enter your filename here
$fileName = "somefile.trc"

# The version information we want to write: 0x0A = 10 = SQLServer 2008
[Byte[]] $versionData = 0x0A
# The offset of the version information in the file
$offset = 390

[System.IO.FileMode] $open = [System.IO.FileMode]::OpenOrCreate
$stream = New-Object System.IO.FileStream -ArgumentList $fileName, $open
$stream.Seek($offset, [System.IO.SeekOrigin]::Begin);
$stream.Write($versionData, 0, $versionData.Length);
$stream.Close()
```



This script overwrites the version byte in the trace file, which lies at offset 390, changing it from 11 to 10.

This way, even a huge 100 GB trace file can be converted in milliseconds, ready to be consumed by ReadTrace or Profiler.

Enjoy!

<strong>P.S.:</strong> I haven't tried, but I guess it could work with previous versions. However, tracing is deprecated in SQL Server 2012 and I guess it doesn't introduce many differences from the SQL Server 2008 trace file format. The same cannot be said for SQL Server 2005 and I suppose that the file wouldn't open anyway in Profiler. Unfortunately, I don't have a SQL Server 2005 around to test.
