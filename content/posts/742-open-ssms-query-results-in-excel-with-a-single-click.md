---
title: "Open SSMS Query Results in Excel with a Single Click"
date: "2014-01-16T00:58:32"
slug: "open-ssms-query-results-in-excel-with-a-single-click"
source_url: "http://spaghettidba.com/2014/01/16/open-ssms-query-results-in-excel-with-a-single-click/"
url: "/2014/01/16/open-ssms-query-results-in-excel-with-a-single-click/"
categories: ["SQL Server"]
tags: ["Add-in", "Automation", "Excel", "Export", "PowerShell", "SQLServer", "SSMS"]
---

<h1>The problem</h1>
One of the tasks that I often have to complete is manipulate some data in Excel, starting from the query results in SSMS.

Excel is a very convenient tool for one-off reports, quick data manipulation, simple charts.

Unfortunately, SSMS doesn’t ship with a tool to export grid results to Excel quickly.

Excel offers some ways to import data from SQL queries, but none of those offers the rich query tools available in SSMS. A representative example is Microsoft Query: how am I supposed to edit a query in a text editor like this?

<a href="/wp-content/uploads/2014/01/msquery.png"><img class="alignnone size-full wp-image-743" alt="MSQuery" src="/wp-content/uploads/2014/01/msquery.png" width="447" height="215" /></a>

Enough said.

Actually, there are many ways to export data from SQL Server to Excel, including SSIS packages and the Import/Export wizard. Again, all those methods require writing your queries in a separate tool, often with very limited editing capabilities.

PowerQuery offers great support for data exploration, but it is a totally different beast and I don’t see it as an alternative to running SQL queries directly.
<h1>The solution</h1>
How can I edit my queries taking advantage of the query editing features of SSMS, review the results and then format the data directly in Excel?

The answer is SSMS cannot do that, but, fortunately, the good guys at <a href="http://www.ssmsboost.com/AboutUs">Solutions Crew</a> brought you a great tool that can do that and much more.

<a href="http://www.ssmsboost.com/">SSMSBoost</a> is a free add-in that empowers SSMS with many useful features, among which exporting to Excel is just one. I highly suggest that you check out the <a href="http://www.ssmsboost.com/VersionCompare">feature list</a>, because it’s really impressive.

Once SSMSBoost is installed, every time you right click a results grid, a context menu appears that lets you export the grid data to several formats.

No surprises, one of those formats is indeed Excel.

<a href="/wp-content/uploads/2014/01/ssmsboostexportexcel.png"><img class="alignnone size-full wp-image-744" alt="SSMSBoostExportExcel" src="/wp-content/uploads/2014/01/ssmsboostexportexcel.png" width="604" height="296" /></a>

The feature works great, even with relatively big result sets. However, it requires 5 clicks to create the Spreadsheet file and one more click to open it in Excel:

<a href="/wp-content/uploads/2014/01/ssmsboostopenfile.png"><img class="alignnone size-full wp-image-745" alt="SSMSBoostOpenFile" src="/wp-content/uploads/2014/01/ssmsboostopenfile.png" width="333" height="110" /></a>

So, where is the single click I promised in the title of this post?

The good news is that SSMSBoost can be automated combining commands in macros to accomplish complex tasks.

Here’s how to create a one-click “open in Excel” command:

First, open the SSMSBoost settings window clicking the “Extras” button.

<a href="/wp-content/uploads/2014/01/ssmsboostsettingsmenu.png"><img class="alignnone size-full wp-image-746" alt="SSMSBoostSettingsMenu" src="/wp-content/uploads/2014/01/ssmsboostsettingsmenu.png" width="255" height="151" /></a>

In the “Shortcuts &amp; Macros” tab you can edit and add macros to the toolbar or the context menu and even assign a keyboard shortcut.

<a href="/wp-content/uploads/2014/01/ssmsboostsettingswindow.png"><img class="alignnone size-full wp-image-747" alt="SSMSBoostSettingsWindow" src="/wp-content/uploads/2014/01/ssmsboostsettingswindow.png" width="604" height="366" /></a>

Clicking the “definitions” field opens the macro editor

<a href="/wp-content/uploads/2014/01/ssmsboosteditdefinition.png"><img class="alignnone size-full wp-image-748" alt="SSMSBoostEditDefinition" src="/wp-content/uploads/2014/01/ssmsboosteditdefinition.png" width="507" height="373" /></a>

Select “Add” and choose the following command: “SSMSBoost.Connect.GridDataCopyTemplateAllGridsDisk3”. This command corresponds to the “Script all grids as Excel to disk” command in SSMSBoost.

Now save everything with OK and close. You will notice <span style="line-height:1.5em;">a new button </span><span style="line-height:1.5em;">in your toolbar:</span>

<a href="/wp-content/uploads/2014/01/ssmsscripttoexcelbutton.png"><img class="alignnone size-full wp-image-749" alt="SSMSScriptToExcelButton" src="/wp-content/uploads/2014/01/ssmsscripttoexcelbutton.png" width="487" height="168" /></a>

That button allows to export all grids to Excel in a single click.

You're almost there: now you just need something to open the Excel file automatically, without the need for additional clicks.

To accomplish this task, you can use a Powershell script, bound to a custom External Tool.

Open the External Tools editor (Tools, External Tools), click “Add” and type these parameters:

<strong>Title:</strong> Open last XML in Excel

<strong>Command:</strong> C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

<strong>Arguments:</strong> -File %USERPROFILE%\openLastExcel.ps1 -ExecutionPolicy Bypass

<a href="/wp-content/uploads/2014/01/ssmsboosteditdefinition2.png"><img class="alignnone size-full wp-image-750" alt="SSMSBoostEditDefinition2" src="/wp-content/uploads/2014/01/ssmsboosteditdefinition2.png" width="471" height="461" /></a>

Click OK to close the External Tools editor.

This command lets you open the last XML file created in the SSMSBoost output directory, using a small Powershell script that you have to create in your %USERPROFILE% directory.

The script looks like this:



```powershell
## =============================================
## Author:      Gianluca Sartori - @spaghettidba
## Create date: 2014-01-15
## Description: Open the last XML file in the SSMSBoost
##              output dicrectory with Excel
## =============================================

sl $env:UserProfile

# This is the SSMSBoost 2012 settings file
# If you have the 2008 version, change this path
# Sorry, I could not find a registry key to automate it.
$settingsFile = "$env:UserProfile\AppData\Local\Solutions Crew\Ssms2012\SSMSBoostSettings.xml"

# Open the settings file to look up the export directory
$xmldata=[xml](get-content $settingsFile)

$xlsTemplate = $xmldata.SSMSBoostSettings.GridDataCopyTemplates.ChildNodes |
    Where-Object { $_.Name -eq "Excel (MS XML Spreadsheet)" }

$SSMSBoostPath = [System.IO.Path]::GetDirectoryName($xlsTemplate.SavePath)

$SSMSBoostPath = [System.Environment]::ExpandEnvironmentVariables($SSMSBoostPath)

# we filter out files created before (now -1 second)
$startTime = (get-date).addSeconds(-1);

$targetFile = $null;

while($targetFile -eq $null){
    $targetFile = Get-ChildItem -Path $SSMSBoostPath |
        Where-Object { $_.extension -eq '.xml' -and $_.lastWriteTime -gt $startTime } |
        Sort-Object -Property LastWriteTime |
        Select-Object -Last 1;

    # file not found? Wait SSMSBoost to finish exporting
    if($targetFile -eq $null) {
        Start-Sleep -Milliseconds 100
    }
};

$fileToOpen = $targetFile.FullName

# enclose the output file path in quotes if needed
if($fileToOpen -like "* *"){
    $fileToOpen = "`"" + $fileToOpen + "`""
}

# open the file in Excel
# ShellExecute is much safer than messing with COM objects...
$sh = new-object -com 'Shell.Application'
$sh.ShellExecute('excel', "/r " + $fileToOpen, '', 'open', 1)
```



Now you just have to go back to the SSMSBoost settings window and edit the macro you created above.

<a href="/wp-content/uploads/2014/01/ssmsboosteditdefinition3.png"><img class="alignnone size-full wp-image-751" alt="SSMSBoostEditDefinition3" src="/wp-content/uploads/2014/01/ssmsboosteditdefinition3.png" width="507" height="373" /></a>

In the definitions field click … to edit the macro and add a second step. The Command to select is “Tools.ExternalCommand1”.

Save and close everything and now your nice toolbar button will be able to open the export file in Excel automagically. Yay!

<a href="/wp-content/uploads/2014/01/openinexcel.png"><img class="alignnone size-full wp-image-752" alt="OpenInExcel" src="/wp-content/uploads/2014/01/openinexcel.png" width="604" height="436" /></a>
<h1>Troubleshooting</h1>
If nothing happens, you might need to change your Powershell Execution Policy. Remember that SSMS is a 32-bit application and you have to set the Execution Policy for the x86 version of Powershell.

Starting Powershell x86 is not easy in Windows 8/8.1, The <a href="http://technet.microsoft.com/en-us/library/hh847733.aspx">documentation</a> says to look up “Windows Powershell (x86)” in the start menu, but I could not find it.

The easiest way I have found is through another External Tool in SSMS. Start SSMS as an Administrator (otherwise the UAC will prevent you from changing the Execution Policy) and configure an external tool to run Powershell. Once you’re in, type “Set-ExecutionPolicy Remotesigned” and hit return. The external tool in your macro will now run without issues.
<h1>Bottom line</h1>
Nothing compares to SSMS when it comes down to writing queries, but Excel is the best place to format and manipulate data.

Now you have a method to take advantage of the best of both worlds. And it only takes one single click.

Enjoy.
