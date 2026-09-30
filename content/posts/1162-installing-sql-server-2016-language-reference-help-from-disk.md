---
title: "Installing SQL Server 2016 Language Reference Help from disk"
date: "2016-10-17T14:35:49"
slug: "installing-sql-server-2016-language-reference-help-from-disk"
source_url: "http://spaghettidba.com/2016/10/17/installing-sql-server-2016-language-reference-help-from-disk/"
url: "/2016/10/17/installing-sql-server-2016-language-reference-help-from-disk/"
categories: ["SQL Server"]
tags: ["Help", "Help Library Manager", "SQL", "SQLServer", "SSMS", "T-SQL"]
---

A couple of years ago I blogged about <a href="/2014/09/25/installing-sql-server-2014-language-reference-help-from-disk/">Installing the SQL Server 2014 Language Reference Help from disk</a>.

With SQL Server 2016 things changed significantly: we have the new Help Viewer 2.2, which is shipped with the Management Studio setup kit.

However, despite all the changes in the way help works and is shipped, I am still unable to download and install help content from the web, so I resorted to using the <a href="/2014/09/25/installing-sql-server-2014-language-reference-help-from-disk/">same trick that I used for SQL Server 2014</a>.

This time the URLs and the files to download are different:
<ol>
<ol>
 	<li>Point your browser to <a href="http://services.mtps.microsoft.com/ServiceAPI/catalogs/sql2016/en-us">http://services.mtps.microsoft.com/ServiceAPI/catalogs/sql2016/en-us</a></li>
 	<li>Download the Language Reference Files:
<ul>
 	<li><a href="http://packages.mtps.microsoft.com/sql_2016_branding_en-us(1bd6e667-f159-ac3b-f0a5-964c04ca5a13).cab">Cabinet File 1</a></li>
 	<li><a href="http://packages.mtps.microsoft.com/v2sql_shared_language_reference_b4621_sql_130_en-us_1(83748a56-8810-751f-d453-00c5accc862d).cab">Cabinet File 2</a></li>
 	<li><a href="http://packages.mtps.microsoft.com/v2sql_shared_language_reference_b4621_sql_130_en-us_2(ccc38276-b744-93bd-9008-fe79b294ff41).cab">Cabinet File 3</a></li>
</ul>
If you're a PowerShell person, these three lines will do:</li>
</ol>
</ol>



```xml
Invoke-WebRequest -Uri "http://packages.mtps.microsoft.com/sql_2016_branding_en-us(1bd6e667-f159-ac3b-f0a5-964c04ca5a13).cab" `
	-OutFile "sql_2016_branding_en-us(1bd6e667-f159-ac3b-f0a5-964c04ca5a13).cab"
Invoke-WebRequest -Uri "http://packages.mtps.microsoft.com/v2sql_shared_language_reference_b4621_sql_130_en-us_1(83748a56-8810-751f-d453-00c5accc862d).cab" `
	-OutFile "v2sql_shared_language_reference_b4621_sql_130_en-us_1(83748a56-8810-751f-d453-00c5accc862d).cab"
Invoke-WebRequest -Uri "http://packages.mtps.microsoft.com/v2sql_shared_language_reference_b4621_sql_130_en-us_2(ccc38276-b744-93bd-9008-fe79b294ff41).cab" `
	-OutFile "v2sql_shared_language_reference_b4621_sql_130_en-us_2(ccc38276-b744-93bd-9008-fe79b294ff41).cab"
```



<ol>
<ol>
<ol start="3">
 	<li>Create a text file name HelpContentSetup.msha in the same folder as the .cab files and paste the following html:</li>
</ol>
</ol>
</ol>



```xml
<html xmlns="http://www.w3.org/1999/xhtml">
<head />
<body class="vendor-book">
    <div class="details">
        <span class="vendor">Microsoft</span>
        <span class="locale">en-us</span>
        <span class="product">SQL Server 2016</span>
        <span class="name">Microsoft SQL Server Language Reference</span>
    </div>
    <div class="package-list">
        <div class="package">
            <span class="name">SQL_2016_Branding_en-US</span>
            <span class="deployed">False</span>
            <a class="current-link" href="sql_2016_branding_en-us(1bd6e667-f159-ac3b-f0a5-964c04ca5a13).cab">sql_2016_branding_en-us(1bd6e667-f159-ac3b-f0a5-964c04ca5a13).cab</a>
        </div>
        <div class="package">
            <span class="name">v2SQL_Shared_Language_Reference_B4621_SQL_130_en-us_1</span>
            <span class="deployed">False</span>
            <a class="current-link" href="v2sql_shared_language_reference_b4621_sql_130_en-us_1(83748a56-8810-751f-d453-00c5accc862d).cab">v2sql_shared_language_reference_b4621_sql_130_en-us_1(83748a56-8810-751f-d453-00c5accc862d).cab</a>
        </div>
        <div class="package">
            <span class="name">v2SQL_Shared_Language_Reference_B4621_SQL_130_en-us_2</span>
            <span class="deployed">False</span>
            <a class="current-link" href="v2sql_shared_language_reference_b4621_sql_130_en-us_2(ccc38276-b744-93bd-9008-fe79b294ff41).cab">v2sql_shared_language_reference_b4621_sql_130_en-us_2(ccc38276-b744-93bd-9008-fe79b294ff41).cab</a>
        </div>
    </div>
</body>
</html>
```



<ol>
<ol>
<ol start="3">
 	<li>First, set the Help Viewer to open help from the local sources:
<img class="alignnone wp-image-1197 size-full" src="/wp-content/uploads/2016/10/1-viewer.png" alt="1-viewer" width="559" height="209" /></li>
 	<li>Then select the "Add and Remove Help Content" command:
<img class="alignnone size-full wp-image-1198" src="/wp-content/uploads/2016/10/2-addremove.png" alt="2-addremove" width="343" height="175" /></li>
 	<li>This command opens the Help Viewer and asks for the content to add.
Browse to the file you created in step 3.
Click "Add" on all the items you wish to add to the library. In this case you will have only 1 item.
When done, click the "Update" button.
<a href="/wp-content/uploads/2016/10/3-addcontent.png"><img class="alignnone wp-image-1199 size-full" src="/wp-content/uploads/2016/10/3-addcontent.png" alt="3-addcontent" width="830" height="500" /></a></li>
 	<li>Unfortunately, during the installation phase of the library item, something crashes and the installation won't proceed until you tell it to ignore or report the error.
<a href="/wp-content/uploads/2016/10/4-crash.png"><img class="alignnone wp-image-1200 size-full" src="/wp-content/uploads/2016/10/4-crash.png" alt="4-crash" width="830" height="500" /></a></li>
 	<li>Despite the crash, everything works as expected and you will find the topic installed in your help library:
<a href="/wp-content/uploads/2016/10/5-installed.png"><img class="alignnone wp-image-1201 size-full" src="/wp-content/uploads/2016/10/5-installed.png" alt="5-installed" width="830" height="500" /></a></li>
</ol>
</ol>
</ol>
Here it is, nice and easy. Hope it works for you too.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (1)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-9869" class="archived-comment"><article><header><strong>Alberto Federico Turelli</strong> <time datetime="2016-10-23T08:27:35Z">October 23, 2016 at 09:27</time></header><section class="archived-comment-content">Yet another nice tutorial, @spaghettidba!<br>I planned to follow everything step by step, but I ended up skipping item 3 (setting Help Preference) because SSDT installation reset SSMS settings. I got no crash, though, and now everything works like a charm.<br><br>Thanks!<br><br>Alberto</section></article></li></ol></details>
</div>
