---
title: "Installing SQL Server 2014 Language Reference Help from disk"
date: "2014-09-25T17:24:19"
slug: "installing-sql-server-2014-language-reference-help-from-disk"
source_url: "http://spaghettidba.com/2014/09/25/installing-sql-server-2014-language-reference-help-from-disk/"
url: "/2014/09/25/installing-sql-server-2014-language-reference-help-from-disk/"
categories: ["SQL Server", "T-SQL"]
tags: ["BOL", "Help", "SQL", "SQL Server 2014", "SQLServer", "SSMS"]
---

Some weeks ago I had to wipe my machine and reinstall everything from scratch, SQL Server included.

For some reason that I still don't understand, SQL Server Management Studio installed fine, but I couldn't install Books Online from the online help repository. Unfortunately, installing from offline is not an option with SQL Server 2014, because the installation media doesn't include the Language Reference documentation.

The issue is well known: <a href="https://twitter.com/AaronBertrand">Aaron Bertrand</a> <a href="http://sqlblog.com/blogs/aaron_bertrand/archive/2014/04/23/yes-you-can-install-sql-server-2014-books-online-locally.aspx">blogged about it back in april</a> when SQL Server 2014 came out and he updated his post in august when the documentation was finally completely published. He also <a href="http://blogs.sqlsentry.com/aaronbertrand/updated-sql-2014-books-online/">blogged about it at SQLSentry</a>.

However, I couldn't get that method to work: the Help Library Manager kept firing errors as soon as I clicked the "Install from Online" link. The error message was "<em>An exception has occurred. See the event log for details.</em>"

Needless to say that the event log had no interesting information to add.

If you are experiencing the same issue, <strong>here is a method to install the language reference from disk</strong> without downloading the help content from the Help Library Manager:

1 . Open a web browser and point it to the following url: <a href="http://services.mtps.microsoft.com/ServiceAPI/products/dd433097/dn632688/books/dn754848/en-us">http://services.mtps.microsoft.com/ServiceAPI/products/dd433097/dn632688/books/dn754848/en-us</a>

2. Download the individual .cab files listed in that page to a location in your disk (e.g. c:\temp\langref\)

3. Create a text file name HelpContentSetup.msha in the same folder as the .cab files and paste the following html:



```xml
<html xmlns="http://www.w3.org/1999/xhtml">
<head />
<body class="vendor-book">
    <div class="details">
        <span class="vendor">Microsoft</span>
        <span class="locale">en-us</span>
        <span class="product">SQL Server 2014</span>
        <span class="name">Microsoft SQL Server Language Reference</span>
    </div>
    <div class="package-list">
        <div class="package">
            <span class="name">SQL_Server_2014_Books_Online_B4164_SQL_120_en-us_1</span>
            <span class="deployed">False</span>
            <a class="current-link" href="sql_server_2014_books_online_b4164_sql_120_en-us_1(0b10b277-ad40-ef9d-0d66-22173fb3e568).cab">sql_server_2014_books_online_b4164_sql_120_en-us_1(0b10b277-ad40-ef9d-0d66-22173fb3e568).cab</a>
        </div>
        <div class="package">
            <span class="name">SQL_Server_2014_Microsoft_SQL_Server_Language_Reference_B4246_SQL_120_en-us_1</span>
            <span class="deployed">False</span>
            <a class="current-link" href="sql_server_2014_microsoft_sql_server_language_reference_b4246_sql_120_en-us_1(5c1ad741-d0e3-a4a8-d9c0-057e2ddfa6e1).cab">sql_server_2014_microsoft_sql_server_language_reference_b4246_sql_120_en-us_1(5c1ad741-d0e3-a4a8-d9c0-057e2ddfa6e1).cab</a>
        </div>
        <div class="package">
            <span class="name">SQL_Server_2014_Microsoft_SQL_Server_Language_Reference_B4246_SQL_120_en-us_2</span>
            <span class="deployed">False</span>
            <a class="current-link" href="sql_server_2014_microsoft_sql_server_language_reference_b4246_sql_120_en-us_2(24815f90-9e36-db87-887b-cf20727e5e73).cab">sql_server_2014_microsoft_sql_server_language_reference_b4246_sql_120_en-us_2(24815f90-9e36-db87-887b-cf20727e5e73).cab</a>
        </div>
    </div>
</body>
</html>
```



4 . Open the Help Library Manager and select "Install content from disk"

5. Browse to the .msha you just created and click Next

<a href="/wp-content/uploads/2014/09/langref1.png"><img class="alignnone wp-image-839 size-full" src="/wp-content/uploads/2014/09/langref1.png" alt="langref1" width="561" height="378" /></a>

6. The SQL Server 2014 node will appear. Click the Add link

<a href="/wp-content/uploads/2014/09/langref2.png"><img class="alignnone wp-image-840 size-full" src="/wp-content/uploads/2014/09/langref2.png" alt="langref2" width="561" height="378" /></a>

7. Click the Update button and let the installation start

<a href="/wp-content/uploads/2014/09/langref3.png"><img class="alignnone wp-image-841 size-full" src="/wp-content/uploads/2014/09/langref3.png" alt="langref3" width="561" height="378" /></a>

8. Installation will start and process the cab files

<a href="/wp-content/uploads/2014/09/langref4.png"><img class="alignnone wp-image-842 size-full" src="/wp-content/uploads/2014/09/langref4.png" alt="langref4" width="561" height="378" /></a>

9. Installation finished!

<a href="/wp-content/uploads/2014/09/langref5.png"><img class="alignnone wp-image-843 size-full" src="/wp-content/uploads/2014/09/langref5.png" alt="langref5" width="561" height="378" /></a>

9. To check whether everything is fine, click on the "remove content" link and you should see the documentation.

<a href="/wp-content/uploads/2014/09/langref6.png"><img class="alignnone wp-image-844 size-full" src="/wp-content/uploads/2014/09/langref6.png" alt="langref6" width="561" height="378" /></a>

Done! It was easy after all, wasn't it?

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (4)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-7060" class="archived-comment"><article><header><strong>retracement</strong> <time datetime="2014-12-02T09:59:35Z">December 2, 2014 at 10:59</time></header><section class="archived-comment-content">Hey Gianluca! Thanks for this post. I confess to having the same annoyance for a while now and whilst I'd also seen Aaron's post, I hadn't managed to get that to work and resorted to using BOL via Google-Fu. Thanks for this fix, works a treat!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-7061" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2014-12-02T10:19:17Z">December 2, 2014 at 11:19</time></header><section class="archived-comment-content">You're welcome, kind sir :-) I'm glad it worked for you.</section></article></li></ol></li><li id="wordpress-comment-8976" class="archived-comment"><article><header><strong>IT-Pro</strong> <time datetime="2015-12-10T04:48:49Z">December 10, 2015 at 05:48</time></header><section class="archived-comment-content">Thank you. it was so helpful. I had more libraries, then I've changed the XML file (text file that you mentioned) as my desire and it's worked.</section></article></li><li id="wordpress-comment-10588" class="archived-comment"><article><header><strong>Gus</strong> <time datetime="2017-03-26T00:20:41Z">March 26, 2017 at 01:20</time></header><section class="archived-comment-content">If some one wants to be updated with most recent technologies therefor hhe must be visit <br>this web site and be up to date daily.</section></article></li></ol></details>
</div>
