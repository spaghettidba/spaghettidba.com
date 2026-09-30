---
title: "Typing the Backtick key on non-US Keyboards"
date: "2011-09-19T22:47:20"
slug: "typing-the-backtick-key-on-non-us-keyboards"
source_url: "http://spaghettidba.com/2011/09/19/typing-the-backtick-key-on-non-us-keyboards/"
url: "/2011/09/19/typing-the-backtick-key-on-non-us-keyboards/"
categories: ["SQL Server"]
tags: ["Backtick", "Italian keyboard", "PowerShell", "keyboard layout", "numeric pad"]
---

You may be surprised to know that not all keyboard layouts include the backtick key, and if you happen to live in a country with such a layout and want to do some PowerShell coding, you’re in big trouble.

For many years all major programming languages took this layout mismatch into consideration and avoided the use of US-only keys in the language definition. Now, with PowerShell, serious issues arise for those that want to wrap their code on multiple lines and reach for the backtick key, staring hopelessly at an Italian keyboard.

See? No backtick.

<a href="/wp-content/uploads/2011/09/italian.png"><img class="alignnone size-full wp-image-330" title="Italian" src="/wp-content/uploads/2011/09/italian.png" alt="" width="549" height="189" /></a>

The only way to type a key not present in your keyboard layout is using the numeric pad with the ALT key, so that, for instance, backtick becomes ALT+Numpad9+Numpad6.

This method is painful enough itself, but quickly becomes a nightmare when working on a laptop, where probably there’s no hardware numeric pad. This way, backtick becomes NumLock+ALT+Numpad9+Numpad6+NumLock.

OMG! 5 keys instead of 1! No way: <strong><em>we need to find a workaround!</em></strong>

If I can’t type the backtick directly, I can always build a small application that types that key for me. Even better, I could unleash my google-fu and find a ready-made one, such as <a href="http://orlando.mvps.org/SendKeysMore.asp">Independent SendKeys</a>.

This small application is able to send keystrokes to any application running on Windows, found by window title. When a blank window title is specified, the SendKeys interacts with the current active window and can send the backtick keystroke. When invoked with no arguments, it displays a help window, which allowed me to come out with this syntax:

sendkeys.exe 0 2 "" "`"

Now I just need to associate this command with one of the keys on my keyboard.

Some fancy keyboards come with special keys to open the web browser or the e-mail client, such as this one:

<a href="/wp-content/uploads/2011/09/shortcutkeys.jpg"><img class="alignnone size-full wp-image-331" title="shortcutKeys" src="/wp-content/uploads/2011/09/shortcutkeys.jpg" alt="" width="409" height="197" /></a>

I have always found those keys nearly useless and I would happily barter one for the backtick key. The good news is that it can be done, even without  one of those special keys on the keyboard

To change the behaviour of one of those keys, you just have to open the registry and navigate to HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\AppKey. Typically, you should find 4 or 5 subkeys, that identify what Windows will do when one of those keys gets pressed.

<a href="/wp-content/uploads/2011/09/regedit.png"><img class="alignnone size-full wp-image-332" title="regedit" src="/wp-content/uploads/2011/09/regedit.png" alt="" width="604" height="255" /></a>

In this case, I chose to replace the e-mail key with backtick, using the SendKeys application. It’s very easy: you just have to rename the “Association” REG_SZ into “_Association” (you can leave it there in case you decide to restore the original behaviour) and add a new string value ShellExecute = 0 2 “” “`”

With this registry hack in place, whenever you press the e-mail key, SendKeys types a backtick on the active window. Mission accomplished? Not completely: the e-mail key is not easy to use, because it was not meant for typing and you will probably find it slightly out of reach.

To type the backtick more easily, you need to immolate one of the other keys and make it act as if it was the e-mail key. In my case, the perfect candidate for the sacrifice is the ScrollLock key, which I don’t remember having used in 20 years. I’m sure I won’t miss it.

To teach Windows to swap the keys I would need to apply another registry hack, but it’s too complicated to use and explain, especially because there’s a nice little application that can do that for me.

<a href="http://www.randyrants.com/2008/12/sharpkeys_30.html">SharpKeys</a> is an application that can remap the keyboard and make a key act as if another key was pressed instead. It does not need to run in background or start with windows, because it’s just a user friendly interface for a registry hack. Once the hack is active, you can even uninstall it if you like.

<a href="/wp-content/uploads/2011/09/sharpkeys1.png"><img class="alignnone size-full wp-image-341" title="SharpKeys" src="/wp-content/uploads/2011/09/sharpkeys1.png" alt="" width="604" height="455" /></a>

In this screen capture, I set the ScrollLock key to act as the e-mail key. As you can see, SharpKeys always assumes you are using the US layout and displays the key accordingly, but the important thing is that it can recognize the correct scancode and remap it to the e-mail key.

The nice thing about this hack is that you can use it even if you don’t have the mapped key in your keyboard. In fact, on my laptop there’s no e-mail key at all.

After rempapping the keys, Windows will start typing backticks whenever you press the  ScrollLock key.

Now you can focus on Powershell itself, not on memorizing ASCII codes!
<blockquote><strong>EDIT 20/09/2011: </strong>In the first version of this post I suggested remapping the e-mail key to the § symbol (which is probably the most useless key on my keyboard), but, actually that would have mapped the <strong>WHOLE</strong> key, thus loosing the ability to type the "ù" char. That's why I changed this post and decided to remap the ScrollLock key instead. My apologies to those who followed my advice and lost their "ù".</blockquote>
<blockquote><strong>EDIT 21/03/2019: </strong>The <a href="https://support.microsoft.com/en-us/help/823010/the-microsoft-keyboard-layout-creator">Microsoft Keyboard Layout Creator</a> can help you create a custom keyboard layout that contains the backtick character mapped to any key combination you find appropriate. Go give it a try.</blockquote>
&nbsp;

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (1)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-34481" class="archived-comment"><article><header><strong>Replacement Laptop Keys</strong> <time datetime="2020-11-27T04:08:46Z">November 27, 2020 at 05:08</time></header><section class="archived-comment-content">Thanks for sharing such an informative article on backtick keys with us.</section></article></li></ol></details>
</div>
