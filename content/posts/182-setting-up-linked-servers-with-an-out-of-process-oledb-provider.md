---
title: "Setting up linked servers with an out-of-process OLEDB provider"
date: "2011-06-09T10:25:12"
slug: "setting-up-linked-servers-with-an-out-of-process-oledb-provider"
source_url: "http://spaghettidba.com/2011/06/09/setting-up-linked-servers-with-an-out-of-process-oledb-provider/"
url: "/2011/06/09/setting-up-linked-servers-with-an-out-of-process-oledb-provider/"
categories: ["SQL Server", "SQL Server Central"]
tags: ["Linked Servers", "OLEDB"]
---

A new article on SQLServerCentral today:<strong> <a href="http://www.sqlservercentral.com/articles/Linked+Servers/73794/">Setting up linked servers with an out-of-process OLEDB provider</a>.</strong>

I had to struggle to find the appropriate security settings to make a commercial OLEDB provider work with out-of-process load and I want to share the results of my research with you.

It took 50 hours of Microsoft paid support to partially solve the issue and a huge time spent on Google and MSDN to find a complete resolution. I hope this can help those that will have to face the same issue some day.
