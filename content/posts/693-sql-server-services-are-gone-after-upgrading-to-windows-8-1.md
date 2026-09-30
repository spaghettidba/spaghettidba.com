---
title: "SQL Server services are gone after upgrading to Windows 8.1"
date: "2013-10-24T17:02:10"
slug: "sql-server-services-are-gone-after-upgrading-to-windows-8-1"
source_url: "http://spaghettidba.com/2013/10/24/sql-server-services-are-gone-after-upgrading-to-windows-8-1/"
url: "/2013/10/24/sql-server-services-are-gone-after-upgrading-to-windows-8-1/"
categories: ["SQL Server"]
tags: ["Configuration Manager", "SQL", "SQL Server services", "SQLServer", "Windows", "Windows 8.1"]
---

Yesterday I upgraded my laptop to Windows 8.1 and everything seemed to have gone smoothly.

I really like the improvements in Windows 8.1 and I think they're worth the hassle of an upgrade if you're still on Windows 8.

As I was saying, everything <strong>seemed</strong> to upgrade smoothly. Unfortunately, today I found out that SQL Server services were gone.

My configuration manager looked like this:

<a href="/wp-content/uploads/2013/10/configman1.png"><img class="alignnone size-full wp-image-694" alt="ConfigMan1" src="/wp-content/uploads/2013/10/configman1.png" width="604" height="171" /></a>

My laptop had an instance of SQL Server 2012 SP1 Developer Edition and the windows upgrade process had deleted all SQL Server services but SQL Server Browser.

I thought that a repair would fix the issue, so I took out my SQL Server iso and ran the setup.

Unfortunately, during the repair process, something went wrong and it complained multiple times about "no mappings between Security IDs and account names" or something similar.

Anyway, the setup completed and the services were back in place, but were totally misconfigured.

<a href="/wp-content/uploads/2013/10/configman11.png"><img class="alignnone size-full wp-image-695" alt="ConfigMan1" src="/wp-content/uploads/2013/10/configman11.png" width="604" height="171" /></a>

SQL Server agent had start mode "disabled" and the service account had been changed to "localsystem" (go figure...)

After changing start mode and service accounts, everything were back to normal.

I hope this post helps others that are facing the same issue.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (5)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-1783" class="archived-comment"><article><header><strong>Andy Gaskins</strong> <time datetime="2013-11-12T18:54:38Z">November 12, 2013 at 19:54</time></header><section class="archived-comment-content">This is exactly what im going through. At first i thought it was the login then i noticed some services were missing. Thanks this helped alot i got the same errors but it ended up working in the end.</section></article></li><li id="wordpress-comment-4155" class="archived-comment"><article><header><strong>Ihor Bobak</strong> <time datetime="2014-03-04T12:56:06Z">March 4, 2014 at 13:56</time></header><section class="archived-comment-content">I can confirm that this relally happens. I have 2 PCs with Win8, after upgdate to 8.1 the SQL Services have disappeared, although all files were on place.</section></article></li><li id="wordpress-comment-8441" class="archived-comment"><article><header><strong>Piquet</strong> <time datetime="2015-09-07T05:39:10Z">September 7, 2015 at 06:39</time></header><section class="archived-comment-content">I just went through this experience AGAIN - after upgrading to Windows 10... <br>Fortunately I found a shorter resolution path than last time: Looking in C:\windows\SysWOW64\ I found a number of SQLServerManagerXX.msc files - right-click &gt; Pin to Start provides me access to the missing config manager (albeit with an unfriendly name...)</section></article></li><li id="wordpress-comment-11522" class="archived-comment"><article><header><strong>windows7bugs</strong> <time datetime="2017-07-08T08:27:24Z">July 8, 2017 at 09:27</time></header><section class="archived-comment-content">Reblogged this on <a href="https://windows7bugs.wordpress.com/2017/07/08/sql-server-services-are-gone-after-upgrading-to-windows-8-1/" rel="nofollow ugc noopener noreferrer">Duh! Microsoft did it again</a>.</section></article></li><li id="wordpress-comment-45506" class="archived-comment"><article><header><strong>Belinda Cruz</strong> <time datetime="2023-07-14T21:49:08Z">July 14, 2023 at 22:49</time></header><section class="archived-comment-content">Nice blog thanks foor posting</section></article></li></ol></details>
</div>
