---
title: "Verdasys Digital Guardian and SQL Server"
date: "2014-02-03T20:15:25"
slug: "verdasys-digital-guardian-and-sql-server-setup"
source_url: "http://spaghettidba.com/2014/02/03/verdasys-digital-guardian-and-sql-server-setup/"
url: "/2014/02/03/verdasys-digital-guardian-and-sql-server-setup/"
categories: ["SQL Server"]
tags: ["SQLServer", "Security"]
---

I'm writing this post as a reminder for myself and possibly to help out the poor souls that may suffer the same fate as me.

There's a software out there called "<a href="https://www.verdasys.com/products/index.html">Digital Guardian</a>" which is a data loss protection tool. Your computer may be running this software without you knowing: your system administrators may have installed it in order to prevent users from performing operations that don't comply to corporate policies and may lead to data loss incidents.

For instance, Digital Guardian can prevent users from writing to USB pendrives and walk out of the office with a copy of the data in their pocket. Actually, this is just one of the policies than can be enforced by Digital Guardian: it's a complete data protection framework that offers many powerful features.

The bad news is Digital Guardian relies on an agent daemon that runs very deep in the operating system and modifies the OS behaviour based on the policies defined by the system administrators. Most of the time, the user is notified of the tool's intervention with explicit messages, stating that the operation is not permitted by corporate policies.

Sometimes (here comes the painful part) things randomly fail without any meaningful indication that Digital Guardian is responsible of the failure. Instead of getting sensible policy violation messages, you may get generic error messages that won't be anywhere easy to troubleshoot. Sometimes, errors are not even due to policy violations, but are caused by the modifications in  the OS behaviour introduced by Digital Guardian itself.

For instance, when installing SQL Server, you may be presented this error message:

<a href="/wp-content/uploads/2014/02/dg_setup_error.png"><img class="size-full wp-image-781 alignnone" alt="DG_setup_error" src="/wp-content/uploads/2014/02/dg_setup_error.png" width="604" height="192" /></a>

Is the error message "No more data is available" anywhere helpful? Not really.

I spent countless hours trying to understand what went wrong and I finally understood the cause of the failure when a coworker pointed out that Digital Guardian was running on that particular server.

<strong>What happened here?</strong>

Digital Guardian clumsily tries to hide itself. If you look for it in the installed programs applet in Control Panel you won't find it. It also tries to hide itself in the registry, so when you enumerate the registry key "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Digital Guardian Agent" you will get an error.

In one of the early stages, SQL Server's setup verifies what software is installed in the machine and when it encounters Digital Guardian's registry key, it fails miserably.

The only way to get past the error is to <strong>disable Digital Guardian</strong>.

<strong>Are you comfortable with running SQL Server on a machine with such a tool installed?</strong>

OK, you managed to install SQL Server by disabling Digital Guardian: now what?
<ul>
	<li>What if SQL Server crashes?</li>
	<li>What if everything turns horribly slow?</li>
	<li>What if you get data corruption?</li>
	<li>What if...?</li>
</ul>
Tools that interact with the OS at such low level scare the hell out of me. Anything that you install and run on a machine with such a tool becomes completely unreliable in my opinion. SQL Server was not intended to run against a modified OS and it was not tested to run like that.

SQL Server has its own security tools. They may not be perfect, but it's how the product was intended to work and, frankly, they're largely sufficient for 99% of the use cases. Probably, enabling TDE is better than preventing everyone from writing to USB drives.

If you think SQL Server security features are not enough for you, go on and activate one of those pesky tools. But let me ask: are you sure that you fall in that 1% ?
