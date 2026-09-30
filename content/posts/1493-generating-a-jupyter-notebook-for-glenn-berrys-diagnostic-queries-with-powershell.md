---
title: "Generating a Jupyter Notebook for Glenn Berry's Diagnostic Queries with PowerShell"
date: "2019-03-20T20:35:46"
slug: "generating-a-jupyter-notebook-for-glenn-berrys-diagnostic-queries-with-powershell"
source_url: "http://spaghettidba.com/2019/03/20/generating-a-jupyter-notebook-for-glenn-berrys-diagnostic-queries-with-powershell/"
url: "/2019/03/20/generating-a-jupyter-notebook-for-glenn-berrys-diagnostic-queries-with-powershell/"
categories: ["SQL Server", "Uncategorized"]
tags: ["Azure Data Studio", "Dbatools", "Diagnostic Queries", "Jupyter Notebooks", "PowerShell"]
---

The <a href="https://cloudblogs.microsoft.com/sqlserver/2019/03/18/the-march-release-of-azure-data-studio-is-now-available/">March release of Azure Data Studio</a> now supports Jupyter Notebooks with SQL kernels. This is a very interesting feature that opens new possibilities, especially for presentations and for troubleshooting scenarios.

For presentations, it is fairly obvious what the use case is: you can prepare notebooks to show in your presentations, with code and results combined in a convenient way. It helps when you have to establish a workflow in your demos that the attendees can repeat at home when they download the demos for your presentation.

For troubleshooting scenarios, the interesting feature is the ability to include results inside a Notebook file, so that you can create an empty Notebook, send it to your client and make them run the queries and send it back to you with the results populated. For this particular usage scenario, the first thing that came to my mind is running the diagnostic queries by Glenn Berry in a Notebook.

Obviously, I don't want to create such a Notebook manually by adding all the code cells one by one. Fortunately, PowerShell is my friend and can do the heavy lifting for me.

Unsurprisingly, dbatools comes to the rescue: <a href="https://twitter.com/AndreKamman">André Kamman</a> added a cmdlet that  downloads, parses and executes Glenn Berry's diagnostic queries and added the cmdlet to dbatools. The part that can help me is not a public function available to the user, but I can still go to GitHub and download the internal function <a href="https://github.com/sqlcollaborative/dbatools/blob/development/internal/functions/Invoke-DbaDiagnosticQueryScriptParser.ps1">Invoke-DbaDiagnosticQueryScriptParser</a> for my needs.
The function returns a list of queries that I can use to generate the Jupyter Notebook:

https://gist.github.com/spaghettidba/41691ecaeb4317f7318327f893cd2656

In order to use the script, you need to provide the path to the file that contains the diagnostic queries and the path where the new Jupyter Notebook should be generated. Dbatools includes the latest version of the diagnostic scripts already, so you just need to choose which flavor you want to use. You will find all available scripts in the module directory of dbatools:



```powershell
$dbatoolsPath = Split-Path -parent (Get-Module -ListAvailable dbatools).path
$dbatoolsPath 
Get-ChildItem "$dbatoolsPath\bin\diagnosticquery" | Select-Object Name
```



The script above produces this output:



```text
C:\Program Files\WindowsPowerShell\Modules\dbatools\0.9.777

Name
----
SQLServerDiagnosticQueries_2005_201901.sql
SQLServerDiagnosticQueries_2008R2_201901.sql
SQLServerDiagnosticQueries_2008_201901.sql
SQLServerDiagnosticQueries_2012_201901.sql
SQLServerDiagnosticQueries_2014_201901.sql
SQLServerDiagnosticQueries_2016SP2_201901.sql
SQLServerDiagnosticQueries_2016_201901.sql
SQLServerDiagnosticQueries_2017_201901.sql
SQLServerDiagnosticQueries_2019_201901.sql
SQLServerDiagnosticQueries_AzureSQLDatabase_201901.sql
```



Once you decide which file to use, you can pass it to the script:



```powershell
create-diagnostic-notebook.ps1 `
    -diagnosticScriptPath "C:\Program Files\WindowsPowerShell\Modules\dbatools\0.9.777\bin\diagnosticquery\SQLServerDiagnosticQueries_2019_201901.sql" `
    -notebookOutputPath "diagnostic-notebook.ipynb"
```



What you obtain is a Jupyter Notebook that you can open in Azure Data Studio:

<img class="alignnone size-full wp-image-1494" src="/wp-content/uploads/2019/03/diagnostic-notebook.png" alt="diagnostic-notebook" width="1264" height="952" />

This is nice way to incorporate the code and results in a single file, that you can review offline later.  This also allows you to send the empty notebook to a remote client, ask to run one or more queries and send back the notebook including the results for you to review.

Happy Notebooking!

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (7)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-27162" class="archived-comment"><article><header><strong>Randolph West</strong> <time datetime="2019-04-10T04:18:47Z">April 10, 2019 at 05:18</time></header><section class="archived-comment-content">Neat.</section></article></li><li id="wordpress-comment-28199" class="archived-comment"><article><header><strong>Michael Kirkpatrick</strong> <time datetime="2019-04-17T22:25:30Z">April 17, 2019 at 23:25</time></header><section class="archived-comment-content">I get an error saying "Illegal characters in path"<br>"C:\Program Files\WindowsPowerShell\Modules\dbatools\0.9.777\bin\diagnosticquery\SQLServerDiagnosticQueries_2019_201901.sql"<br><br>Is it the space in Program Files?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-28705" class="archived-comment"><article><header><strong>Jan Sundbye</strong> <time datetime="2019-05-31T12:00:49Z">May 31, 2019 at 13:00</time></header><section class="archived-comment-content">Excellent. Thank you very much.<br><br>It works perfectly with the 2012, 2014, 2016 and 2017 scripts. Unfortunately this is all that comes out of the 2016 SP2 script:<br><br>{<br>    "metadata": {<br>        "kernelspec": {<br>            "name": "SQL",<br>            "display_name": "SQL",<br>            "language": "sql"<br>        },<br>        "language_info": {<br>            "name": "sql",<br>            "version": ""<br>        }<br>    },<br>    "nbformat_minor": 2,<br>    "nbformat": 4,<br>    "cells":<br>[<br>    {<br>        "cell_type":  "markdown",<br>        "source":  "## \n\n"<br>    },<br>    {<br>        "cell_type":  "code",<br>        "source":  ""<br>    }<br>]<br>}}</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-28709" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-05-31T13:02:36Z">May 31, 2019 at 14:02</time></header><section class="archived-comment-content">There seems to be a bug in the format of the 2016 SP2 queries. My code relies on a function in dbatools that parses the diagnostic queries based on some placeholders inside the file. The placeholders are not correct in the 2016 SP2 file.<br>I will contact Glenn and let him know. Thanks!</section></article></li></ol></li></ol></li><li id="wordpress-comment-28706" class="archived-comment"><article><header><strong>Jan Sundbye</strong> <time datetime="2019-05-31T12:08:18Z">May 31, 2019 at 13:08</time></header><section class="archived-comment-content">Michael:<br>Check the path to the diagnostic queries. Either replace the version number in ...\dbatools\\diagnosticquery\.... <br>or download later versions of the scripts and use the path to where you save the downloaded files. As long as you use quotation marks around \ spaces is no problem.</section></article></li><li id="wordpress-comment-32518" class="archived-comment"><article><header><strong>dbaAlek</strong> <time datetime="2020-03-07T01:12:05Z">March 7, 2020 at 02:12</time></header><section class="archived-comment-content">Worked perfectly. Very useful and timely. Nifty scripting! Kudos.</section></article></li><li id="wordpress-comment-32644" class="archived-comment"><article><header><strong>vijred</strong> <time datetime="2020-03-19T03:24:05Z">March 19, 2020 at 04:24</time></header><section class="archived-comment-content">beautiful!</section></article></li></ol></details>
</div>
