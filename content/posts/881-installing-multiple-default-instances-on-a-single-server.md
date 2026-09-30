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
