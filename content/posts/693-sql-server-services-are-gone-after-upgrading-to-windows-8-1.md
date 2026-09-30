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
