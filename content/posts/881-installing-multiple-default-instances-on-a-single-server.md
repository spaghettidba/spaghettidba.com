---
title: "Installing multiple default instances on a single server"
date: "2015-01-29T19:17:03"
slug: "installing-multiple-default-instances-on-a-single-server"
source_url: "http://spaghettidba.com/2015/01/29/installing-multiple-default-instances-on-a-single-server/"
url: "/2015/01/29/installing-multiple-default-instances-on-a-single-server/"
categories: ["SQL Server"]
tags: ["Default Instance", "Network", "SQLServer"]
---

As you probably know, SQL Server allows only one default instance per server. The reason is not actually something special to SQL Server, but it has to do with the way TCP/IP endpoints work.

In fact, a SQL Server default instance is nothing special compared to a named instance: it has a specific instance id (MSSQLSERVER) and listens on a well-known TCP port (1433), but it has no other intrinsic property or feature that makes it different from any other instance.

Let's look closely to these properties: the instance id is specific to a SQL Server instance and it has to be unique. In this regard, MSSQLSERVER makes no exception. Similarly, a TCP endpoint must be unique and there can be only one socket listening on a specific endpoint.

Nevertheless, I will show you a way to have multiple "default" instances installed on the same server, even if it might look impossible at a first look.

<strong>Install two instances of SQL Server</strong>

First of all, you need to have two (or more) instances installed on your server. In this example I will use the server "FANGIO" and I will install two named instances: INST01 and INST02.

Here's what my Configuration Manager looks like once the two instances are ready:

<a href="/wp-content/uploads/2015/01/configmanager.png"><img class="alignnone size-full wp-image-882" src="/wp-content/uploads/2015/01/configmanager.png" alt="COnfigManager" width="604" height="159" /></a>

In this case I used two named instances, but it would have worked even if I used a default instance and a named instance. Remember? Default instances are nothing special.

<strong>Provision IP addresses</strong>

Each SQL Server instance must listen on a different TCP endpoint, but this does not mean that each instance has to listen on a different port: a TCP endpoint is made of an IP address and a port. This means that two instances can listen on the same port, as long as the IP addresses are different.

In this case, you just need to add a new IP address to the server, one for each SQL Server instance that you want to listen on port 1433.

<a href="/wp-content/uploads/2015/01/tcpip.png"><img class="alignnone size-full wp-image-883" src="/wp-content/uploads/2015/01/tcpip.png" alt="TCPIP" width="414" height="495" /></a>

<strong>Configure network protocols</strong>

Now that you have multiple IP addresses, you just have to tell SQL Server to listen on that specific address, port 1433.

Open the Configuration Manager and enable TCP/IP:

<a href="/wp-content/uploads/2015/01/networkconfig.png"><img class="alignnone size-full wp-image-884" src="/wp-content/uploads/2015/01/networkconfig.png" alt="NetworkConfig" width="604" height="172" /></a>

Now open the properties applet and disable "Listen All":

<a href="/wp-content/uploads/2015/01/listenall.png"><img class="alignnone size-full wp-image-885" src="/wp-content/uploads/2015/01/listenall.png" alt="ListenAll" width="426" height="480" /></a>

In the IP Addresses tab, configure the IP address and the port:

<a href="/wp-content/uploads/2015/01/networkconfig2.png"><img class="alignnone size-full wp-image-886" src="/wp-content/uploads/2015/01/networkconfig2.png" alt="NetworkConfig2" width="426" height="480" /></a>

In this case I enabled the address 10.0.1.101 for INST01 and I disabled all the remaining addresses. For INST02 I enabled 10.0.1.102.

<strong>Configure DNS</strong>

Now the server has two IP addresses and they both resolve to its network name (FANGIO). In order to let clients connect to the appropriate SQL Server instance, you need to create two separate "A" records in DNS to resolve to each IP address.

In this case I don't have a DNS server (it's my home lab) so I will use the hosts file:

<a href="/wp-content/uploads/2015/01/hosts.png"><img class="alignnone size-full wp-image-887" src="/wp-content/uploads/2015/01/hosts.png" alt="hosts" width="604" height="550" /></a>

&nbsp;

<strong>Final Setup</strong>

Now the example setup looks like this:

<a href="/wp-content/uploads/2015/01/setup.png"><img class="alignnone size-full wp-image-888" src="/wp-content/uploads/2015/01/setup.png" alt="setup" width="505" height="355" /></a>

When a client connects to the default instance on ASCARI, it is connecting to FANGIO\INST01 instead. Similarly, the default instance on VILLENEUVE corresponds to FANGIO\INST02.

<a href="/wp-content/uploads/2015/01/ssms.png"><img class="alignnone size-full wp-image-889" src="/wp-content/uploads/2015/01/ssms.png" alt="ssms" width="411" height="414" /></a>

<strong>Why would I want to do this?</strong>

If you had only default instances in your servers, moving databases around for maintenances, upgrades or consolidations would be just a matter of adding a CNAME to your DNS.

With named instances, the only way to redirect connections to a different server is by using a SQLClient alias. Unfortunately, aliases are client-side settings and have to be deployed to each and every client in order to work. Group policies can deploy aliases to multiple machines at once, but policies are not evaluated immediately, while a DNS entry can propagate very quickly.

Another reason to use this setup is the ability to bypass the SQLBrowser: when a named instance is specified, the client has to contact the SQLBrowser service on port 1434 with a small UDP datagram and receive back the list of instances, along with the port they're listening on. When the default instance is specified, there is no need to contact the SQLBrowser, because we already know the port it is listening on (it's 1433, unless it has been changed).

Sometimes the firewall settings for SQLBrowser are tricky to set up, <a href="http://blogs.msdn.com/b/jorgepc/archive/2010/10/05/unexpected-behaviour-setting-up-firewall-rules-with-clustered-sql-server-instances.aspx">especially with clusters</a>. Another thing I recently discovered is that SQLBrower allows attackers to create <a href="http://kurtaubuchon.blogspot.it/2015/01/mc-sqlr-amplification-ms-sql-server.html"><strong>huge </strong>DDOS attacks using a 440x amplification factor</a>.

<strong>Security concerns</strong>

Some setup guides recommend that you change the port SQL Server listens on to something different from 1433, which is a well-known port, more likely to be discovered by attackers. I think that an attacker skilled enough to penetrate your server needs much more resistance than just "hiding" your instance to a non-default port. A quick port scan would immediately reveal any SQL Server instance listening on any port, so this is really a moot point in my opinion.

<strong>Bottom line</strong>

SQL Server allows only one default instance to be installed on a machine, but with a few simple steps every instance can be made a "default" instance. The main advantage of such a setup is the ability to redirect client connections to a database instance with a simple change in the DNS configuration.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (23)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-7388" class="archived-comment"><article><header><strong>Magnus</strong> <time datetime="2015-01-29T20:32:33Z">January 29, 2015 at 21:32</time></header><section class="archived-comment-content">Hi, nice post. <br>Do you think this could be a solution to migrate a couple of servers (with only one default instance per server) to one server with Alwayson AG ?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-7389" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-01-29T20:44:06Z">January 29, 2015 at 21:44</time></header><section class="archived-comment-content">It seems to me that you have to consolidate two servers into one. In this case a simple CNAME in your DNS should do the trick.</section></article></li></ol></li><li id="wordpress-comment-7404" class="archived-comment"><article><header><strong>mike good</strong> <time datetime="2015-01-31T20:52:11Z">January 31, 2015 at 21:52</time></header><section class="archived-comment-content">Good article, well done, thank you!  Comes at perfect time for me.</section></article></li><li id="wordpress-comment-7421" class="archived-comment"><article><header><strong>piers7</strong> <time datetime="2015-02-03T09:06:01Z">February 3, 2015 at 10:06</time></header><section class="archived-comment-content">This is how SQL clusters work. Each instance in the cluster has to be bound to a unique IP (so instances can fail over separately) - ergo they are all 'default instances'</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-7422" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-02-03T09:32:19Z">February 3, 2015 at 10:32</time></header><section class="archived-comment-content">Not exactly. You can have named instances in a cluster and you only can have one default instance. Same as a standalone server. <br>The port 1433 can be used for all instances to make them "default" using the same technique. With clusters it's easier because each instance is already bound to its ip address.</section></article></li></ol></li><li id="wordpress-comment-9250" class="archived-comment"><article><header><strong>ig</strong> <time datetime="2016-02-19T07:46:43Z">February 19, 2016 at 08:46</time></header><section class="archived-comment-content">Hello mates, its impressive post regarding educationand completely explained, keep it up all the time.</section></article></li><li id="wordpress-comment-9672" class="archived-comment"><article><header><strong>aroop simon</strong> <time datetime="2016-08-24T14:58:03Z">August 24, 2016 at 15:58</time></header><section class="archived-comment-content">Was about to set this up in a lab and voila i see your post! Saved me one full day !<br>Thanks !</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-9673" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2016-08-24T14:58:40Z">August 24, 2016 at 15:58</time></header><section class="archived-comment-content">Glad I could help!</section></article></li></ol></li><li id="wordpress-comment-9988" class="archived-comment"><article><header><strong>Gustavo Maia</strong> <time datetime="2016-11-21T13:01:46Z">November 21, 2016 at 14:01</time></header><section class="archived-comment-content">Hi! Thanks for this great post!<br><br>Would you know how to set the SPN for these instances for kerberos authentication?<br><br>Cheers!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-10007" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2016-11-23T22:08:39Z">November 23, 2016 at 23:08</time></header><section class="archived-comment-content">Hi Gustavo,<br>Thanks for stopping by. I am sorry, I don't think I investigated this setup under the point of view of kerberos and SPNs.</section></article></li></ol></li><li id="wordpress-comment-11933" class="archived-comment"><article><header><strong>Sean Lewis</strong> <time datetime="2017-10-09T11:11:41Z">October 9, 2017 at 12:11</time></header><section class="archived-comment-content">Thanks, I was trying to do this on a SQL box with a couple of different versions in co-existence but it wasn't working, your article confirmed to me I was on the right track, not sure what I did (or didn't do) first time around but tried again after reading your article and it worked.</section></article></li><li id="wordpress-comment-12292" class="archived-comment"><article><header><strong>Radu</strong> <time datetime="2018-03-14T17:19:44Z">March 14, 2018 at 18:19</time></header><section class="archived-comment-content">Somewhere I think I've done something wrong, although I followed your tutorial 3 times over starting from scratch.<br>When connecting from a "client" to my VM with the 2 SQL Server instances, no matter which IP I use, 10.115.8.198 or 10.115.8.199, they both redirect me to INST01.<br><br>I don't really understand why it's doing such. <br><br>For INST02 I have set up in TCP/IP the 10.115.8.199 IP with 1433 port, but still I'm getting redirected to the original instance that was on 10.115.8.198.<br><br>Can you please point me to where my mistake was made?<br><br>Grazie mille!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12293" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-03-14T17:25:52Z">March 14, 2018 at 18:25</time></header><section class="archived-comment-content">Did you restart the instances?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12294" class="archived-comment"><article><header><strong>Radu</strong> <time datetime="2018-03-14T17:28:59Z">March 14, 2018 at 18:28</time></header><section class="archived-comment-content">Yes, quote a few times.</section></article></li><li id="wordpress-comment-12295" class="archived-comment"><article><header><strong>Radu</strong> <time datetime="2018-03-14T17:40:45Z">March 14, 2018 at 18:40</time></header><section class="archived-comment-content">Do both instances need to have "Listen All" set to "No" in Configuration Manager -&gt; SQL Server Network Configuration?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12296" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-03-14T18:25:45Z">March 14, 2018 at 19:25</time></header><section class="archived-comment-content">Both instances need to have "listen all" set to "no".</section></article></li></ol></li><li id="wordpress-comment-12298" class="archived-comment"><article><header><strong>Radu</strong> <time datetime="2018-03-15T05:52:02Z">March 15, 2018 at 06:52</time></header><section class="archived-comment-content">Well, if I do set both instances to have "Listen All" to "No" then the service associated to my instance fails to start up with "Windows could not start the SQL Server on Local Computer. For more infor, reivew Ssytem Event Log .. and refer to service-specific error code 10049", whereas the error loc says "SQL Server could not spawn FRunCM thread."</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12299" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-03-15T06:02:08Z">March 15, 2018 at 07:02</time></header><section class="archived-comment-content">Did you enable the individual IP addresses?</section></article></li></ol></li><li id="wordpress-comment-12300" class="archived-comment"><article><header><strong>Radu</strong> <time datetime="2018-03-15T08:10:12Z">March 15, 2018 at 09:10</time></header><section class="archived-comment-content">Yes, IP's are enabled in Configuration Manager for both instances. I guess I'll have to keep digging..</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12301" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-03-15T08:14:11Z">March 15, 2018 at 09:14</time></header><section class="archived-comment-content">Honestly, I have no idea. If you need assistance with that, hit me up on Zoom</section></article></li></ol></li><li id="wordpress-comment-12302" class="archived-comment"><article><header><strong>Radu</strong> <time datetime="2018-03-15T14:06:19Z">March 15, 2018 at 15:06</time></header><section class="archived-comment-content">I finally managed to set both instances's "Listen All" to "No". The issue seemed to be where I was restarting the instances from Windows-&gt;Services instead of from Configuration Manager. When I stopped both instances from "Configuration Manager / SQL Server Services", redid the configuration and started them again from Configuration Manager, it worked!<br><br>Even so, without your tutorial I would have been lost! Grazie mille ancora!!!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-12303" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2018-03-15T14:07:47Z">March 15, 2018 at 15:07</time></header><section class="archived-comment-content">Excellent! Glad I could help</section></article></li></ol></li></ol></li></ol></li><li id="wordpress-comment-35318" class="archived-comment"><article><header><strong>Burn</strong> <time datetime="2021-03-12T20:54:36Z">March 12, 2021 at 21:54</time></header><section class="archived-comment-content">Still very helpfull... Thank you</section></article></li></ol></details>
</div>
