---
title: "Native Client Aliases don't like Trailing Spaces"
date: "2015-05-26T23:13:13"
slug: "native-client-aliases-dont-like-trailing-spaces"
source_url: "http://spaghettidba.com/2015/05/26/native-client-aliases-dont-like-trailing-spaces/"
url: "/2015/05/26/native-client-aliases-dont-like-trailing-spaces/"
categories: ["SQL Server"]
tags: ["Alias", "Configuration Manager", "SQLNCLI", "SQLServer"]
---

I usually don't post small things like this, but today I fought with this obnoxious problem long enough to convince me that it deserved a shout out to the community.

When you create an alias in the SQL Server Configuration Manager, make sure that the alias name contains no spaces, otherwise it won't work as you expect.

In my case, I had a Reporting Services instance with many data sources pointing to a SQL Server instance (let's call it MyServer) and I wanted to redirect connections to a different instance using an alias. So I opened Configuration Manager and created an alias like this:

<a href="/wp-content/uploads/2015/05/alias.png"><img class="alignnone size-full wp-image-965" src="/wp-content/uploads/2015/05/alias.png" alt="alias" width="426" height="480" /></a>

To my great surprise, the alias didn't work and it took quite some time to notice that something was wrong. The server "MyServer" was a perfectly working existing instance of SQL Server, so no connection was dropped: they all just happened to contact the wrong server. If spotting the problem was hard, fixing it turned out to be even harder: why on earth did the alias refuse to work, while all other aliases were working perfectly?

It turned out to be the simplest of all answers: <strong>a trailing space in the alias name</strong>.

Just looking at the alias properties it wasn't too obvious that something was off, but clicking on the alias name field, the cursor appeared slightly more on the right than it should have been:

<a href="/wp-content/uploads/2015/05/alias2.png"><img class="alignnone size-full wp-image-966" src="/wp-content/uploads/2015/05/alias2.png" alt="alias2" width="426" height="480" /></a>

Bottom line is: <strong>always check your assumptions</strong>, because problems like to hide where you won't search for them.
