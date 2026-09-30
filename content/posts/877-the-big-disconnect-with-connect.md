---
title: "The big disconnect with Connect"
date: "2015-01-07T19:58:35"
slug: "the-big-disconnect-with-connect"
source_url: "http://spaghettidba.com/2015/01/07/the-big-disconnect-with-connect/"
url: "/2015/01/07/the-big-disconnect-with-connect/"
categories: ["SQL Server"]
tags: ["Connect", "Microsoft"]
---

<a href="/wp-content/uploads/2015/01/connect-logo-new.png"><img class="  wp-image-878 alignleft" src="/wp-content/uploads/2015/01/connect-logo-new.png" alt="Connect-logo-New" width="223" height="64" /></a>A couple of years ago I blogged about a <a href="/2013/03/19/data-collector-clustering-woes/">bug on the Data Collector</a> that I couldn't resolve but with an ugly workaround. At the end of that post, I stated that I wouldn't have bothered filing the bug on <a href="http://connect.microsoft.com">Connect</a>, due to prior discouraging results. Well, despite what I wrote there, I took the time to open a bug on Connect (the item can be found <a href="https://connect.microsoft.com/SQLServer/feedback/details/934530/data-collector-uses-the-wrong-instance-name-in-a-clustered-instance">here</a>), which was promptly closed as "won't fix".

Nothing new under the sun: "won't fix" is the most likely answer on Connect, no matter how well you document your issue and how easy is the bug to reproduce. I really am sorry to say that, but it's a widespread feeling that Connect has become totally pointless, if it ever had a point. The common feeling about Connect is that bugs are usually closed as "won't fix" or "by design" without any further communication, while suggestions are completely disregarded.

How did we get here? Why is Microsoft spending money on a service that generates frustration on users? Where does this idiosyncrasy come from?

If I had to give Microsoft advice on how to improve Connect, I would focus on one simple point:

<strong>Improve feedback</strong>

One of the things I see over and over on Connect is the lack of communication between users and support engineers. Once the item is closed, it's closed (with few notable exceptions). You can ask for more information, add details to the item, do anything you can think of, but the engineers will stop responding. Period.

This means that there is no way to steer the engineer's understanding of the bug: if (s)he read it wrong, (s)he won't read it again.

I can understand that anybody with a Microsoft account can create bugs on Connect without having to pay for the time spent on the problem by the engineers: this can easily lead to a very low signal/noise rate, which is not sustainable. In other words, the support engineers seem to be flooded by an overwhelming amount of inaccurate submissions, which makes mining for noteworthy bugs an equally overwhelming task.

However, I think that the current workflow for closing bugs is too abrupt and a more reasonable workflow would at least require responding to the <strong>first</strong> comment received after the item is marked for closure.

<strong>How is CSS different?</strong>

In this particular case, I decided to conduct a small experiment and I opened the same exact bug with CSS. Needless to say that the outcome was totally different.

The bug was recognized as a bug, but this is not the main point: the biggest difference was the amount and the quality of communication with the support engineer. When you file a bug with CSS, a support engineer is assigned to your case and you can communicate with him/her directly by email. If the engineer needs more information on the case, (s)he will probably call you on the phone and ask for clarification. In our case, we also have a TAM (Technical Account Manager) that gets CC'ed to all emails between us and CSS.

Where does the difference lay? Just one: <strong>money</strong>.

If you want to contact the CSS, you have to pay for support. If the bug turns out to be a documented behavior instead, you pay for the time spent by the engineers working on it. This is totally absent from Connect, where everyone can file bugs without having to pay attention to what they do: there will be nothing to pay at the end of the day.

<strong>Is Connect really pointless?</strong>

One thing I discovered with my experiment may surprise you: <strong>CSS reads Connect items </strong>and if there is one matching your case, they will take it into account. This is really good news in my opinion and sheds a totally new light over Connect.

Another thing I discovered is that there is much more information behind a Connect item than it's visible to users. When the engineers process items, they produce comments that are attached to the different workflow steps involved in the triage. Unfortunately, this is invisible to the end users, that are left with the minimal information that the engineers decide to share.

However, the important lesson learned from this experiment is that Connect may be frustrating for end users, but it is far from pointless: the information gathered while triaging bugs contributes to the quality of the paid support and, ultimately, to the quality of SQL Server itself. What still is unsatisfactory is the feedback to Connect users, that are getting more and more discouraged to file new items.

<strong>An appeal to Microsoft</strong>

Dear Microsoft, please, please, please improve the feedback on Connect: more feedback means less frustration for users that submit legitimate and reasonable bugs. Less frustration means more sensible feedback from your users, which in turn helps your CSS and improves the quality of SQL Server. Not everybody can open cases with CSS: this doesn't mean that they are not contributing positevely to your product (and you know it), so please reward them with a better communication.
