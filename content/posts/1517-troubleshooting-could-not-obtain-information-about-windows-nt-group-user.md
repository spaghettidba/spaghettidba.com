---
title: "Troubleshooting \"Could not obtain information about Windows NT group/user\""
date: "2019-08-16T15:00:48"
slug: "troubleshooting-could-not-obtain-information-about-windows-nt-group-user"
source_url: "http://spaghettidba.com/2019/08/16/troubleshooting-could-not-obtain-information-about-windows-nt-group-user/"
url: "/2019/08/16/troubleshooting-could-not-obtain-information-about-windows-nt-group-user/"
categories: ["SQL Server"]
tags: []
---

<!-- wp:paragraph -->
<p>This is one of those typical blog posts that I write for my future self, the guy who keeps fixing the same stuff over and over and forgets what he did the next minute.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If you want to query information about a Windows user or group and its access path in SQLServer, you can use the extended stored procedure "xp_logininfo". Here's an example:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">EXEC xp_logininfo 'MyDomain\SomeUser','all';</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>If everything is configured correctly, you will see a list of Windows accounts and the login(s) they are mapped to in SQLServer.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>However, in some cases, the command fails with the infamous error message:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>Could not obtain information about Windows NT group/user 'MyDomain\SomeUser', error code 0x5</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>This happens every time SQLServer tries to query information about the Windows user from Active Directory and receives an error.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Understanding where the error comes from can be tricky, but it can become easier to troubleshoot when you understand what happens behind the scenes and what are the most likely causes.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>The user does not exist</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This is very easy to check: does the user exist in Windows? Did you misspell the name?</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>You can check this from a cmd window, issuing this command:</p>
<!-- /wp:paragraph -->

<!-- wp:preformatted -->
<pre class="wp-block-preformatted">net user SomeUser /domain</pre>
<!-- /wp:preformatted -->

<!-- wp:paragraph -->
<p>If you spelled the user correctly, the command will return information about it, like description, password settings, group membership and so on.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If the user name is incorrect and cannot be found in AD, you will get an error message</p>
<!-- /wp:paragraph -->

<!-- wp:preformatted -->
<pre class="wp-block-preformatted">The user name cannot be found.</pre>
<!-- /wp:preformatted -->

<!-- wp:paragraph -->
<p>Easy peasy: check your spelling and check your AD.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>The service account does not have enough privileges to query AD</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>As I said,  SQL Server needs to query AD to retrieve information about the user: if its service account doesn't have enough privileges, the query will fail.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The most likely cause for this is a misconfiguration of the service account settings in SQL Server. To be more specific, it is very likely that SQL Server is configured to run as a local user who has no access to Active Directory at all. This happens when SQL Server runs as a per-service SID or one of the built-in local accounts (local service or localsystem).</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>It is very easy to check what account is being used to run SQL Server: all you need to do is query sys.dm_server_services.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">SELECT servicename, service_account 
FROM sys.dm_server_services;</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>If you see a local account being returned, go ahead and change your service account to a domain account, using the Configuration Manager.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If you still can't query AD, maybe there is something wrong with the permissions on your AD objects.  Try impersonating the SQL Server service account, open a cmd windows and issue the net user command. </p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>&gt; net user SomeUser /domain
The request will be processed at a domain controller for domain MyDomain

System error 5 has occurred.
Access is denied</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>If you get the "Access is denied" error message, you need to go to your AD and grant read permissions on that user/OU to the service account.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>The service account does not have enough privileges to impersonate the windows user</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This was a bit of a surprise for me. In order to retrieve information about the Windows user, SQL Server needs to impersonate it first and then will contact AD impersonating that user.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In order to impersonate a user, SQL Server needs to run under a service account user that has enough privileges to impersonate another user. This privilege is granted through a local policy.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Open the local security policy MMC (secpol.msc) and expand "Local Policies", "User Rights Assignment". Find the policy named "Impersonate a client after authentication" and double click it. You can verify whether the service account for SQL Server is granted this privilege, directly or through one of its groups.</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1520,"sizeSlug":"large"} -->
<figure class="wp-block-image size-large"><img src="/wp-content/uploads/2019/08/secpol.png" alt="" class="wp-image-1520" /></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>Generally speaking, you don't have to change this, because by default Windows grants this privilege to the "SERVICE" special identity. Any process running as a service is acting as the SERVICE special identity, including SQL Server. If you don't find it listed here, add it back.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Windows permissions can get tricky at times. I hope that this post helps you (and me!) taming the beast.</p>
<!-- /wp:paragraph -->

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (2)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-36707" class="archived-comment"><article><header><strong>Jacques Doubell</strong> <time datetime="2021-09-23T08:18:33Z">September 23, 2021 at 09:18</time></header><section class="archived-comment-content">In my case I was on the work domain when I created the database. I can only open the diagram when I'm connected to the vpn.</section></article></li><li id="wordpress-comment-39077" class="archived-comment"><article><header><strong>Bill McQ</strong> <time datetime="2022-02-16T22:53:40Z">February 16, 2022 at 23:53</time></header><section class="archived-comment-content">Just in case someone else gets stymied by this - we were having an *intermittent* problem with this. It was failing on two different servers, at completely independent times. Turns out that they never entered the subnet into AD Sites and Services. This worked fine for years, but then they moved *some* of the AD services to a new server that wasn't listed in the firewall rules. Unfortunately this was causing SQL database mail jobs to fail, and the SQL error is extremely misleading ("Failed to load SQLCMD library", which is what database mail errors out with no matter what's wrong). I had to run a trace to get the "Could not obtain information" error, which let me to the net user command, which is how I convinced the network people that it wasn't SQL.</section></article></li></ol></details>
</div>
