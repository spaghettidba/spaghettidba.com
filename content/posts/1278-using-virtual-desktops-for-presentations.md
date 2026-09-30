---
title: "Using Virtual Desktops for Presentations"
date: "2017-03-13T17:30:45"
slug: "using-virtual-desktops-for-presentations"
source_url: "http://spaghettidba.com/2017/03/13/using-virtual-desktops-for-presentations/"
url: "/2017/03/13/using-virtual-desktops-for-presentations/"
categories: ["SQL Server", "Uncategorized"]
tags: ["PowerPoint", "Presenting"]
---

Today I was reading <a href="https://twitter.com/sql_williamd">William Durkin</a>'s fine post on <a href="http://www.williamdurkin.com/2017/03/presenting-presentation-mode/">Presentation Mode in SSMS vNext</a> when inspiration struck.

One of the things that really annoys me when presenting is the transition between slides and demos. Usually, I try to improve the process as much as possible by having the least minimum amount of windows open while presenting, so that I don't land on the wrong window. Unfortunately, that is not always easy.

Another thing that I would like to be smoother is the transition itself. The ideal process should be:
<ol>
	<li>Leave the powerpoint slides open at full screen</li>
	<li>Switch immediately to the virtual machine with the demos</li>
	<li>Go back to the slides, to the exact point where I left</li>
</ol>
What I usually do is show the desktop with the WIN+D hotkey, then activate the Virtualbox window with my demos, but this shows my desktop for a moment and I don't really like this extra transition.

I could also use ALT+Tab to switch to the Virtualbox window, but this would briefly show the list of running applications, which is not exactly what I want.

Turns out that Windows 10 has the perfect solution built-in: Virtual Desktops.

Here is the setup described:
<ol>
	<li>If you press WIN+Tab, you will see a "New desktop" button on the bottom right corner. Use it to create three desktops:
<ol>
	<li>desktop 3 for the slides</li>
	<li>desktop 2 for the demos</li>
	<li>desktop 1 for the rest</li>
</ol>
</li>
	<li>Press WIN+Tab, find your virtual machine and move it to <strong>desktop 2. </strong>It is really easy: you just have right click the window you want to send to a different desktop and select which desktop to use.<img class="alignnone size-full wp-image-1324" src="/wp-content/uploads/2017/03/movetodesktop1.png" alt="MoveToDesktop.png" width="1920" height="1080" /></li>
	<li>Open your presentation and start it by pressing F5. Again, hit WIN+Tab, find the fullscreen window of your PowerPoint presentation and move it to <strong>desktop 3</strong>.</li>
	<li>In order to transition from one desktop to another, you can use the hotkey <strong>CTRL+WIN+Arrow</strong>, as shown in this GIF:<img class="alignnone size-full wp-image-1330" src="/wp-content/uploads/2017/03/giphy.gif" alt="giphy" width="480" height="270" /></li>
</ol>
Here it is! Perfectly smooth, a nice transition animation and nothing but your slides and your demos shown to the attendees.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (6)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-10533" class="archived-comment"><article><header><strong>James Anderson</strong> <time datetime="2017-03-14T09:00:40Z">March 14, 2017 at 10:00</time></header><section class="archived-comment-content">Very nice! Have you tested with your clicker to make sure it doesn't get confused by the desktop switching?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-10534" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2017-03-14T09:19:39Z">March 14, 2017 at 10:19</time></header><section class="archived-comment-content">The clicker is just a USB keyboard with 4 keys, so if it works with the 102 keys keyboard, it works with the clicker.</section></article></li></ol></li><li id="wordpress-comment-10542" class="archived-comment"><article><header><strong>Brent Ozar</strong> <time datetime="2017-03-15T13:22:54Z">March 15, 2017 at 14:22</time></header><section class="archived-comment-content">Be careful - when presenting remotely, I've seen people lose their connections when they do very animated stuff like switching desktops. There's so many pixels to draw that the online meeting software just throws up its hands. :-D</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-10543" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2017-03-15T13:51:02Z">March 15, 2017 at 14:51</time></header><section class="archived-comment-content">Ha! I'm an authority in bad connections :-)<br>Thanks for the heads-up. BTW, the transition animation can be disabled:<br><br>Press Win+X and select System.<br><br>Click on advanced system settings.<br><br>On Advanced TAB click on performance settings.<br><br>On Performance Options - Visual Effects, uncheck "Animate windows when minimizing and maximizing".</section></article></li></ol></li><li id="wordpress-comment-10654" class="archived-comment"><article><header><strong>Andrea Uggetti</strong> <time datetime="2017-04-10T15:08:38Z">April 10, 2017 at 16:08</time></header><section class="archived-comment-content">Interesting reading, have you tried remotely with SkypeForBusiness?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-10655" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2017-04-10T15:18:21Z">April 10, 2017 at 16:18</time></header><section class="archived-comment-content">Just tried, with the help of a colleague and I can confirm that it works like a charm</section></article></li></ol></li></ol></details>
</div>
