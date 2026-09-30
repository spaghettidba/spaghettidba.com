---
title: "Collecting Diagnostic data from multiple SQL Server instances with dbatools"
date: "2019-11-24T19:32:00"
slug: "collecting-diagnostic-data-from-multiple-sql-server-instances-with-dbatools"
source_url: "http://spaghettidba.com/2019/11/24/collecting-diagnostic-data-from-multiple-sql-server-instances-with-dbatools/"
url: "/2019/11/24/collecting-diagnostic-data-from-multiple-sql-server-instances-with-dbatools/"
categories: ["SQL Server"]
tags: ["Dbatools", "Diagnostic Queries", "PowerShell", "SQLServer"]
---

<!-- wp:paragraph -->
<p>Keeping their SQL Server instances under
control is a crucial part of the job of a DBA. SQL Server offers a wide variety
of DMVs to query in order to check the health of the instance and establish a
performance baseline.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>My favourite DMV queries are the ones
crafted and maintained by Glenn Berry: the SQL Server Diagnostic Queries. These
queries already pack the right amount of information and can be used to take a
snapshot of the instance’s health and performance.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Piping the results of these queries to a set
of tables at regular intervals can be a good way to keep an eye on the instance.
Automation in SQL Server rhymes with dbatools, so today I will show you how to
automate the execution of the diagnostic queries and the storage of the results
to a centralized database that you can use as a repository for your whole SQL
Server estate.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>The script</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The script I’m using for this can be found on GitHub and you can download it, modify it and adapt it to your needs.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>I won't include it here, there is really no need for that, as you can find it on Github already. So, go, grab it from <a href="https://github.com/spaghettidba/DBA-Scripts/blob/master/Capture-Diagnostic/capture-diagnostic.ps1">this address</a>, save it and open it in your favourite code editor. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Done? Excellent! Let's go through it together.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>The script, explained</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>What I really love about PowerShell is how
simple it is to filter, extend and manipulate tabular data using the pipeline,
in a way that resonates a lot with the experience of T-SQL developers.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The main part of the script is the one that invokes all the diagnostic queries included in the list <code>$queries</code>. This is done by invoking the cmdlet <code>Invoke-DbaDiagnosticQuery</code>, that takes care of using a version of the diagnostic query that matches the version of the target server and selecting the data. As usual with dbatools, the <code>-SqlInstance</code> parameter accepts a list of servers, so you can pass in the list of all the SQL Servers in your infrastructure.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"powershell"} -->
<pre class="wp-block-syntaxhighlighter-code">Invoke-DbaDiagnosticQuery -SqlInstance $SourceServer  -QueryName $queries</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Sometimes the queries do not generate any data, so it is important to filter out the empty result sets.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"powershell"} -->
<pre class="wp-block-syntaxhighlighter-code">Where-Object { $_.Result -ne $null } </pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>In order to store the data collected at
multiple servers and multiple points in time, you need to attach some
additional columns to the result sets before writing them to the destination
tables. This is a very simple task in PowerShell and it can be accomplished by
using the Select-Object cmdlet.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Select-Object accepts a list of columns
taken from the input object and can also add calculated columns using
hashtables with label/expression pairs. The syntax is not the friendliest
possible (in fact, I have to look it up every time I need it), but it gets the
job done. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In this case, you need to add a column for the server name, one for the database name (only for database scoped queries) and one for the snapshot id. I decided to use a timestamp in the <code>yyyyMMdd</code> as the snapshot id. This is what the code to define the properties looks like:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"powershell"} -->
<pre class="wp-block-syntaxhighlighter-code">        $TableName = $_.Name
        $DatabaseName = $_.Database
        $ServerName = $_.SqlInstance

        $snapshotProp = @{
            Label = "snapshot_id"
            Expression = {$SnapshotId}
        }
        $serverProp = @{
            Label = "Server Name"
            Expression = {$ServerName}
        }
        $databaseProp = @{
            Label = "Database Name"
            Expression = {$DatabaseName}
        }</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Now that the hashtables that define the
additional properties are ready, you need to decide whether the input dataset
requires the new properties or not: if a property with the same name is already
present you need to skip adding the new property.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Unfortunately, this has to be done in two different ways, because the dataset produced by the diagnostic queries could be returned as a collection of System.Data.Datarow objects or as a collection of PsCustomObject.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"powershell"} -->
<pre class="wp-block-syntaxhighlighter-code">        if(-not (($_.Result.PSObject.Properties | Select-Object -Expand Name) -contains "Server Name")) {
            if(($_.Result | Get-Member -MemberType NoteProperty -Name "Server Name" | Measure-Object).Count -eq 0) {
                $expr += ' $serverProp, '
            }
        }</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Now comes the interesting part of the
script: the data has to get written to a destination table in a database.
Dbatools has a cmdlet for that called <code>Write-DbaDataTable</code>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Among the abilities of this nifty cmdlet, you can auto create the destination tables based on the data found in the input object, thus making your life much easier. In order to pass all the parameters to this cmdlet, I will use a splat, which improves readability quite a bit.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"powershell"} -->
<pre class="wp-block-syntaxhighlighter-code">        $expr += '*'

        $param = @{
            SqlInstance     = $DestinationServer
            Database        = $DestinationDatabase
            Schema          = $DestinationSchema
            AutoCreateTable = $true
            Table           = $TableName
            InputObject     = Invoke-Expression $expr
        }
        Write-DbaDataTable @param</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>As you can see, you need to pass a
destination server name, a database name, a schema name and a table name. As I
already mentioned, <code>Write-DbaDataTable</code> will take care of creating the target
table. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>One thing to note is how the data is passed
to the cmdlet: the <code>InputObject</code> is the result of an expression, based on the
dynamic select list generated inside the <code>ForeEach-Object</code> cmdlet. This is very
similar to building a dynamic query in T-SQL.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Conclusion</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This script can be downloaded from GitHub
and you can schedule it on a centralized management server in order to collect
diagnostic data across your entire SQL Server estate.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Dbatools is the ultimate toolset for the
dba: if you’re still using the GUI or overly complicated T-SQL scripts to
administer and maintain your SQL Server estate, you’re missing out. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Dbatools is also a great opportunity for me to learn new tricks in Powershell, which is another great productivity tool that can’t be overlooked by DBAs. What are you waiting for? Go to <a href="https://dbatools.io">dbatools.io</a> now and start your journey: you won’t regret it.</p>
<!-- /wp:paragraph -->
