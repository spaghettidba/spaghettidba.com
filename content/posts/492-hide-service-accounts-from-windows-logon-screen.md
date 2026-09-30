---
title: "Hide service accounts from Windows logon screen"
date: "2012-04-05T10:34:10"
slug: "hide-service-accounts-from-windows-logon-screen"
source_url: "http://spaghettidba.com/2012/04/05/hide-service-accounts-from-windows-logon-screen/"
url: "/2012/04/05/hide-service-accounts-from-windows-logon-screen/"
categories: ["SQL Server"]
tags: ["Logon", "Users", "Windows", "registry hack"]
---

If you are playing with multiple Virtual Machines and multiple SQL Server instances and features, it's very likely that your virtual machines logon screens are showing all the users you set up for service accounts.

In this case, my Master Data Services playground shows the "MDSAppPoolUser" I set up for the MDS web application:

<a href="/wp-content/uploads/2012/04/logon.png"><img class="alignnone size-full wp-image-493" title="Logon" src="/wp-content/uploads/2012/04/logon.png" alt="" width="581" height="322" /></a>

Needless to say that I will never need to logon as one of those service accounts and I would be happier if the logon screen just hid them.

The good news is that Windows can do that, with a simple registry hack.

The registry key to add is the following:



```text
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList
```



Under the UserList key, you just have to add a REG_DWORD named after each user you want to hide, with a value of 0 (zero):

<a href="/wp-content/uploads/2012/04/specialaccounts1.png"><img class="alignnone size-full wp-image-495" title="SpecialAccounts" src="/wp-content/uploads/2012/04/specialaccounts1.png" alt="" width="604" height="205" /></a>

To verify that the service account user has been hidden from your logon screen, you can select "change user" from the start menu:

<a href="/wp-content/uploads/2012/04/logon2.png"><img class="alignnone size-full wp-image-496" title="Logon2" src="/wp-content/uploads/2012/04/logon2.png" alt="" width="600" height="610" /></a>

That's it! No more service accounts on your logon screen.

If you want to re-enable those account on the logon screen, just change the DWORD value to 1 (one).
