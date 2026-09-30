---
title: "An annoying bug in Database Mail Configuration Wizard"
date: "2011-07-15T14:36:15"
slug: "an-annoying-bug-in-database-mail-configuration-wizard"
source_url: "http://spaghettidba.com/2011/07/15/an-annoying-bug-in-database-mail-configuration-wizard/"
url: "/2011/07/15/an-annoying-bug-in-database-mail-configuration-wizard/"
categories: ["SQL Server"]
tags: ["BUG", "database mail"]
---

Looks like a sneaky bug made its way from SQL Server 2005 CTP to SQL Server 2008 R2 SP1 almost unnoticed, or, at least, ignored by Microsoft.

<a href="/wp-content/uploads/2011/07/configuredatabasemail.png"><img class="alignnone size-full wp-image-223" title="ConfigureDatabaseMail" src="/wp-content/uploads/2011/07/configuredatabasemail.png" alt="" width="415" height="307" /></a>

Imagine that you installed a new SQL Server instance  (let’s call it “TEST”) and you want Database Mail configured in the same way as your other instances. No problem: you navigate the object explorer to Database Mail, start the wizard and then realize that you don’t remember the parameters to enter.

<a href="/wp-content/uploads/2011/07/databasemailconfigurationwizard.png"><img class="alignnone size-full wp-image-224" title="DatabaseMailConfigurationWizard" src="/wp-content/uploads/2011/07/databasemailconfigurationwizard.png" alt="" width="604" height="527" /></a>

Not a big deal: you can copy those parameters from the server “PROD” that you configured last year.

You start the wizard on “PROD” and keep this window open to copy the parameter values in the “TEST” dialog.

<a href="/wp-content/uploads/2011/07/databasemailconfigurationwizard2.png"><img class="alignnone size-full wp-image-225" title="DatabaseMailConfigurationWizard2" src="/wp-content/uploads/2011/07/databasemailconfigurationwizard2.png" alt="" width="604" height="527" /></a>

OK, done? You just have to click "Finish" and... whoops!

This is the error you get when you try to apply the settings:

<a href="/wp-content/uploads/2011/07/databasemailerror.png"><img class="alignnone size-full wp-image-226" title="DatabaseMailError" src="/wp-content/uploads/2011/07/databasemailerror.png" alt="" width="604" height="136" /></a>

Wait: you don’t have a “dba_notify” account on server “TEST” yet. This error message was generated on PROD instead.

Looks like MS developers coded this dialog assuming that just one of these was open at a time and probably used an application-scoped global variable to store the Database Mail settings. Not only: the Database Mail Wizard looses its database context and points to a different instance.

I found a Connect item reporting the issue, dating back to July 2005:

<a href="http://connect.microsoft.com/SQLServer/feedback/details/207602/max-of-1-database-mail-wizard-open-at-a-time">http://connect.microsoft.com/SQLServer/feedback/details/207602/max-of-1-database-mail-wizard-open-at-a-time</a>

Here is another one from 2006:

<a href="http://connect.microsoft.com/SQLServer/feedback/details/124958/database-mail-configuration-gui-does-not-appear-to-maintain-database-context">http://connect.microsoft.com/SQLServer/feedback/details/124958/database-mail-configuration-gui-does-not-appear-to-maintain-database-context</a>

I haven’t tried on Denali CTP3 yet, but I would not be surprised if I found it to be still broken.

Until Microsoft decides to fix it, if you want to copy the Database Mail Settings from another server, start the Database Mail Wizard from a separate SSMS instance, or your settings can get totally screwed up.
