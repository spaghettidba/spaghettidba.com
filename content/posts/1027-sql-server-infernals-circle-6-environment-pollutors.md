---
title: "SQL Server Infernals – Circle 6: Environment Pollutors"
date: "2015-07-31T11:35:20"
slug: "sql-server-infernals-circle-6-environment-pollutors"
source_url: "http://spaghettidba.com/2015/07/31/sql-server-infernals-circle-6-environment-pollutors/"
url: "/2015/07/31/sql-server-infernals-circle-6-environment-pollutors/"
categories: ["SQL Server", "SQL Server Infernals"]
tags: ["Development Environment", "Worst Practices", "test environment"]
---

<img class="alignnone size-full wp-image-976" src="/wp-content/uploads/2015/06/infernals1.png" alt="Infernals" width="604" height="158" />

Don’t tell me that you didn’t see it coming: at some point, Developers end up being put to hell by a DBA!

I don’t want to enter the DBA/Developer wars, but some sins committed by Developers really deserve a ticket to the SQL Server hell. In particular, some of those sins are perpetrated when not even a single line of code is written yet and they have to do with the way the development environment is set up.
<h2>What they say in Heaven</h2>
Before starting a software project, the angelic developers set up their environment in the best of all ways, with proper environment isolation and definition. In particular they will have:
<ul>
	<li><strong>Development Environment:</strong> this is the place (ideally a dev’s desktop) where the development work is performed. It should resemble the production environment as much as possible.</li>
</ul>
<ul>
	<li><strong>Test Environment (QA):</strong> This is where the testers ensure the quality of the application, open bugs and review bug fixes. It should be identical to the production environment (in Heaven it is).</li>
</ul>
<ul>
	<li><strong>User Acceptance Test Environment (UAT): </strong>this is where the clients test the quality of third-party applications, request features and file bugs.</li>
</ul>
<ul>
	<li><strong>Staging Environment (Pre-Production): </strong>this environment is used to assemble, test and review newer versions of the database before it is moved into production. The hardware mirrors that of the production environment.</li>
</ul>
<ul>
	<li><strong>Production Environment: </strong>This is where the real database lives. It can be updated from the staging environment, when available, as well as new functionality and bug fixes release from UAT or staging environment.</li>
</ul>
If your organization or the project are small, you probably don’t need all of these environments. In Heaven, where time and money are not a constraint, they have all of them and they’re all identical to production. Heh, Heaven is Heaven after all…
<h2>Environmental sinners will face SQL Server’s judgement</h2>
Setting up your development environment in the wrong way can harm SQL Server (and your software) in many ways, right from the start of the project, throughout its whole lifetime. Let’s see some of the most common sins:



<figure id="attachment_1028" class="wp-caption aligncenter" style="width: 269px; max-width: 100%;">
<a href="/wp-content/uploads/2015/07/polluted.png"><img class="wp-image-1028 size-full" src="/wp-content/uploads/2015/07/polluted.png" alt="polluted" width="269" height="254" /></a>
<figcaption class="wp-caption-text">A notable example of Polluted Database</figcaption>
</figure>


<ol>
	<li><strong>Using the production environment for development</strong>: frankly, I don’t think this sin needs any further explanation. On the other hand, don’t assume that nobody’s doing it, despite we’re in 2015: lots of damned developers’ souls confess this sin while entering the SQL Server hell!</li>
</ol>
<ol start="2">
	<li><strong>Using the test environment for development: </strong>Again, this seems so obvious that there should be no need to discuss it: development is development and test is test. The test environment(s) should be used to test the application, not to see it breaking every minute because you changed something. Developing the code and testing it are two different things and, even if you happen to be in charge of both, this is not a good reason to confuse the two tasks.</li>
</ol>
<ol start="3">
	<li><strong>Using a shared instance for development: </strong>Back in the old days, when I was working as an ASP classic developer in a software house, we had a shared development environment on a central IIS server, where everyone saved their code on a shared folder and just had to hit F5 in Internet Explorer to see the changes immediately in action.
If you think this model is foolish you’re 100% right, but in the 90s’ we didn’t know better. However, while everyone today agrees that it’s a terrible idea for code, you will still find hordes of developers not completely convinced that it’s an equally terrible idea as far as the database is concerned. Having a shared development database greatly simplifies the process of creating a consistent development database, which is a problem only if you have no authoritative source to build it from (which brings us to the next sin).</li>
</ol>
<ol start="4">
	<li><strong>No source control: </strong>Nobody in their right mind would start a software project today without using source control, yet source control for the database is still an esoteric topic, despite the plethora of tools to accomplish this task.</li>
</ol>
<ol start="5">
	<li><strong>Granting sysadmin rights to the application: </strong>If you’re using a local development instance (and you should), you probably are the administrator of that instance. Hey, nothing wrong with that, unless you use windows authentication in your application. In that case, whenever you debug the application in Visual Studio (or whatever you’re using), the application impersonates you (a sysadmin) when hitting the database, so there is no need to grant any permission in order to let the app perform anything on the instance.
So, what happens when you’re done with development and you have to deploy in test (or, worse, production)? Exactly: nothing works, because (hopefully) the application won’t run with sysadmin privileges in production. At that point, extracting the complete lists of permissions needed by the application is an overwhelming task that you could have happily avoided by developing with a non-privileged user in the first place. When using a regular user, each time the application needs additional permissions, you simply have to add a GRANT statement to the deployment script, which also acts as the documentation the DBA will ask for.
If you fail to provide this documentation, two things could happen: a) the DBA may refuse to deploy the database b) you could end up needing sysadmin privileges, which means a dedicated instance, which could in turn bring us back to a).</li>
</ol>
<ol start="6">
	<li><strong>Developing on a different version/edition from production: </strong>if your application is targeting SQL Server 2008 R2, developing on SQL Server 2012 could mean that you will discover incompatible T-SQL features after development. The same can be said for the SQL Server edition: if you are using a Developer Edition for development but you are targeting Standard Edition, you will discover the use of enterprise-only features when it’s too late. You can save yourself all the pain by using in development the same exact SQL Server version and edition you are targeting in production.</li>
</ol>
In the next episodes of SQL Server Infernals I’m afraid I will have to put more developers to hell. If you’re a developer, stay tuned to find out if your soul is a at risk! If you’re a DBA, stay tuned to enjoy seeing more developers damned!
