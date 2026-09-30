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

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (3)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-4119" class="archived-comment"><article><header><strong>Bill Ledingham</strong> <time datetime="2014-03-02T20:21:47Z">March 2, 2014 at 21:21</time></header><section class="archived-comment-content">Hi Gianluca, thank you for mentioning us in your blog. I’m sorry that you ran into some issues regarding our product. While Digital Guardian is designed to protect sensitive information within an organization, it is certainly not our intent to get in the way of people doing their jobs. The policies and rules within Digital Guardian are highly configurable – occasionally an organization may have a rule in place that creates unintended behavior, i.e., it blocks an action without providing the user with a clear prompt as to why the action has been prevented. You should be able to log a ticket internally and your security contact can work with our support organization to resolve this situation. I’m also happy to address any questions you might have about the product and, in particular, how it is used to augment the SQL Server security tools. Please feel free to email me at the address I provided.</section></article></li><li id="wordpress-comment-4709" class="archived-comment"><article><header><strong>Jim Peterson</strong> <time datetime="2014-03-17T14:49:00Z">March 17, 2014 at 15:49</time></header><section class="archived-comment-content">I have also run into strange errors that are caused by the Digital Guardian application. This included system hangs, and USB communication errors. We are attempting to communicate with some instrumentation over the USB interface using the Agilent VISA control library, and have zoomed in on the dgapi.dll as being the culprit. Verdasys should provide better tools to help track down errors that are being induced by the Digital Guardian app. Wasting large amounts of time &amp; resources chasing these errors can be just as damaging as the potential data loss that this app is trying to prevent.</section></article></li><li id="wordpress-comment-10606" class="archived-comment"><article><header><strong>Sergey Lublinsky</strong> <time datetime="2017-03-29T20:28:47Z">March 29, 2017 at 21:28</time></header><section class="archived-comment-content">We just migrated 500 computers to different domain and 40 computers died after migration because of older version of DG was installed on those computers. :-)</section></article></li></ol></details>
</div>
