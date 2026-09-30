---
title: "Recovering the PsGallery Repository behind a Corporate Proxy"
date: "2017-12-19T14:44:45"
slug: "recovering-the-psgallery-repository-behind-a-corporate-proxy"
source_url: "http://spaghettidba.com/2017/12/19/recovering-the-psgallery-repository-behind-a-corporate-proxy/"
url: "/2017/12/19/recovering-the-psgallery-repository-behind-a-corporate-proxy/"
categories: ["PowerShell"]
tags: ["Powershell PsGallery Proxy"]
---

While getting a new workstation is usually nice, reinstalling all your softwares and settings is definitely not the most pleasant thing that comes to my mind. One of the factors that can contribute the most to making the process even less pleasant is working around the corporate proxy.

Many applications live on the assumption that nobody uses proxy servers, thus making online repositories inaccessible for new installations and for automatic updates.

Unfortunately, PsGallery is no exception.

If you run <code>Get-PSRepository</code> on a vanilla installation of Windows 10 behind a corporate proxy, you will get a warning message:



```powershell
WARNING: Unable to find module repositories.
```



After unleashing my Google-Fu, I learned that I had to run the following command to recover the missing PsRepository:



```powershell
Register-PSRepository -Default -Verbose
```



The command works without complaining, with just a warning suggesting that something might have gone wrong:



```powershell
VERBOSE: Performing the operation "Register Module Repository." on target "Module Repository 'PSGallery' () in provider 'PowerShellGet'.".
```



Again, running <code>Get-PSRepository</code> returns an empty result set and the usual warning:



```powershell
WARNING: Unable to find module repositories.
```



The problem here is that the cmdlet <code>Register-PsRepository</code> assumes that you can connect directly to the internet, without using a proxy, so it tries to do so, fails to connect and does not throw a meaningful error messsage. Thank you, <code>Register-PsRepository</code>, much appreciated!

In order to fix it, you need to configure your default proxy settings in your powershell profile. Start powershell and run the following:



```powershell
notepad $PROFILE
```



This will start notepad and open your powershell profile. If the file doesn't exist, Notepad will prompt you to create it.

Add these lines to the profile script:



```powershell
[system.net.webrequest]::defaultwebproxy = new-object system.net.webproxy('http://YourProxyHostNameGoesHere:ProxyPortGoesHere')
[system.net.webrequest]::defaultwebproxy.credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
[system.net.webrequest]::defaultwebproxy.BypassProxyOnLocal = $true
```



Save, close and restart powershell (or execute the profile script with <code>iex $PROFILE</code>).

Now, you can register the default PsRepository with this command:



```powershell
Register-PSRepository -Default
```



If you query the registered repositories, you will now see the default PsRepository:



```powershell
Get-PSRepository

Name                      InstallationPolicy   SourceLocation
----                      ------------------   --------------
PSGallery                 Untrusted            https://www.powershellgallery.com/api/v2/
```



Horray!

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (33)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-12281" class="archived-comment"><article><header><strong>Lorraine</strong> <time datetime="2018-03-06T13:47:04Z">March 6, 2018 at 14:47</time></header><section class="archived-comment-content">Great article, I just spent all morning trying to install the AzureAD module on a Windows 2016 server. This has resolved it as I am going through a proxy server.</section></article></li><li id="wordpress-comment-12330" class="archived-comment"><article><header><strong>Kojo Obeng Antwi</strong> <time datetime="2018-03-22T20:35:45Z">March 22, 2018 at 21:35</time></header><section class="archived-comment-content">Thank you so much. I have been chasing my tail until I found your article. It worked like a charm.</section></article></li><li id="wordpress-comment-12436" class="archived-comment"><article><header><strong>Vishal</strong> <time datetime="2018-04-26T19:53:45Z">April 26, 2018 at 20:53</time></header><section class="archived-comment-content">thanks!</section></article></li><li id="wordpress-comment-12562" class="archived-comment"><article><header><strong>moonwalker</strong> <time datetime="2018-06-06T07:59:18Z">June 6, 2018 at 08:59</time></header><section class="archived-comment-content">Awesome! Many thanks!</section></article></li><li id="wordpress-comment-12665" class="archived-comment"><article><header><strong>Michael</strong> <time datetime="2018-06-20T10:52:17Z">June 20, 2018 at 11:52</time></header><section class="archived-comment-content">Many thanks!</section></article></li><li id="wordpress-comment-12975" class="archived-comment"><article><header><strong>Ho Minh Dat</strong> <time datetime="2018-07-10T21:48:06Z">July 10, 2018 at 22:48</time></header><section class="archived-comment-content">Awesome guide. It worked to me.</section></article></li><li id="wordpress-comment-13055" class="archived-comment"><article><header><strong>Eric</strong> <time datetime="2018-08-28T06:19:16Z">August 28, 2018 at 07:19</time></header><section class="archived-comment-content">You are amazing! Worked perfectly.<br>Thank you.</section></article></li><li id="wordpress-comment-13076" class="archived-comment"><article><header><strong>David Carriere</strong> <time datetime="2018-09-12T13:42:23Z">September 12, 2018 at 14:42</time></header><section class="archived-comment-content">I believe this was the final solution to my 12 step problem to get NUGET working behind a firewall ;-) Thanks!</section></article></li><li id="wordpress-comment-13142" class="archived-comment"><article><header><strong>Ian G</strong> <time datetime="2018-10-10T11:53:46Z">October 10, 2018 at 12:53</time></header><section class="archived-comment-content">back of the net!!</section></article></li><li id="wordpress-comment-13247" class="archived-comment"><article><header><strong>uwin</strong> <time datetime="2018-11-14T16:37:13Z">November 14, 2018 at 17:37</time></header><section class="archived-comment-content">Thanks for the article. It saved my day.</section></article></li><li id="wordpress-comment-27355" class="archived-comment"><article><header><strong>mittens2012 (@mittens2049)</strong> <time datetime="2019-04-11T13:09:08Z">April 11, 2019 at 14:09</time></header><section class="archived-comment-content">How do i know what my proxy settings are?  ON local systems i don't have any enabled, but i am on a corporate AD system which could be using one.. is there any way to tell what it is?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-27468" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-04-12T08:34:22Z">April 12, 2019 at 09:34</time></header><section class="archived-comment-content">This line of powershell tells you what the proxy settings are on the current machine:<br><br>(Get-ItemProperty -Path "Registry::HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings").ProxyServer<br><br>You could run it on the target machine to see what it gives.<br>Hope this helps</section></article></li></ol></li><li id="wordpress-comment-29049" class="archived-comment"><article><header><strong>HannaH</strong> <time datetime="2019-06-28T11:03:13Z">June 28, 2019 at 12:03</time></header><section class="archived-comment-content">thank you so so much, I wasted half a morning on this</section></article></li><li id="wordpress-comment-29488" class="archived-comment"><article><header><strong>AIsmaili</strong> <time datetime="2019-08-07T16:36:27Z">August 7, 2019 at 17:36</time></header><section class="archived-comment-content">OMG! I was looking soooooooo long for this solution, finally I found this site! :D</section></article></li><li id="wordpress-comment-29523" class="archived-comment"><article><header><strong>Johnny</strong> <time datetime="2019-08-14T08:30:44Z">August 14, 2019 at 09:30</time></header><section class="archived-comment-content">Thanks</section></article></li><li id="wordpress-comment-29590" class="archived-comment"><article><header><strong>Steve</strong> <time datetime="2019-08-23T05:17:48Z">August 23, 2019 at 06:17</time></header><section class="archived-comment-content">Thanks, Was banging my head on this one for a while.  I knew it was the web proxy!</section></article></li><li id="wordpress-comment-30338" class="archived-comment"><article><header><strong>Mr DHEERAJ GUNDAVARAM</strong> <time datetime="2019-09-17T14:09:08Z">September 17, 2019 at 15:09</time></header><section class="archived-comment-content">Thanks buddy, this helped a lot. it was a headache for a while.</section></article></li><li id="wordpress-comment-30352" class="archived-comment"><article><header><strong>ramin</strong> <time datetime="2019-09-19T15:14:10Z">September 19, 2019 at 16:14</time></header><section class="archived-comment-content">Thanks mate for sharing this, now raises the questions for the users who are restricted behind the Internet terminal server and not the proxy server, how are they able to get their powershell configured for getting around the terminal server ?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-30356" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-09-19T16:14:25Z">September 19, 2019 at 17:14</time></header><section class="archived-comment-content">I'm sorry,I don't even know what internet terminal server is...</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-30360" class="archived-comment"><article><header><strong>ramin</strong> <time datetime="2019-09-20T08:11:15Z">September 20, 2019 at 09:11</time></header><section class="archived-comment-content">Well, in some IT organizations to consolidate the internal network security (Usaully applied for IT Admins) another layer, shields and prevents the internal clients from directly accessing the proxy server. Instead these clients establish a connection to the Terminal Server (The server is used for application or Internet distribution among internal clients) through the RDP and this Terminal Server is in its turn placed behind the proxy server. Here is the exact scenarion which i am dealing with ;) . Now i am at the point of finding a way to fool the Terminal server in the first place then take care of the proxy server.. Anyway thanks for the response my friend</section></article></li></ol></li></ol></li><li id="wordpress-comment-30411" class="archived-comment"><article><header><strong>Ajith Bhojani</strong> <time datetime="2019-09-27T02:10:14Z">September 27, 2019 at 03:10</time></header><section class="archived-comment-content">Thanks worked like a charm!</section></article></li><li id="wordpress-comment-31481" class="archived-comment"><article><header><strong>wichardhartes</strong> <time datetime="2019-11-28T12:58:30Z">November 28, 2019 at 13:58</time></header><section class="archived-comment-content">At last, an article I can understand! Thanks for explaining it clearly and concisely. <br>No thanks to Microsoft for making it so hard (and difficult to troubleshoot).<br>Yes, I LIVE BEHIND A PROXY!!!!</section></article></li><li id="wordpress-comment-31778" class="archived-comment"><article><header><strong>Karl</strong> <time datetime="2019-12-20T18:46:22Z">December 20, 2019 at 19:46</time></header><section class="archived-comment-content">You need to note:<br><br>After "notepad $PROFILE" you have to close all Powershell Editors or windows and start as administrator the powershell editor again!<br><br>...don't forget save your ps - scripts before!</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-31779" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2019-12-20T19:05:41Z">December 20, 2019 at 20:05</time></header><section class="archived-comment-content">Actually it's enough to re run the profile script, as noted in the article</section></article></li></ol></li><li id="wordpress-comment-33022" class="archived-comment"><article><header><strong>Jack</strong> <time datetime="2020-05-08T08:19:07Z">May 8, 2020 at 09:19</time></header><section class="archived-comment-content">This Article should be the first result on Google search</section></article></li><li id="wordpress-comment-33718" class="archived-comment"><article><header><strong>berks</strong> <time datetime="2020-08-19T12:49:52Z">August 19, 2020 at 13:49</time></header><section class="archived-comment-content">Thank you!!</section></article></li><li id="wordpress-comment-33728" class="archived-comment"><article><header><strong>Ndy</strong> <time datetime="2020-08-20T14:07:13Z">August 20, 2020 at 15:07</time></header><section class="archived-comment-content">Thank you so much guy for sharing this !!! Sharing is caring :)</section></article></li><li id="wordpress-comment-34205" class="archived-comment"><article><header><strong>Keith</strong> <time datetime="2020-10-30T01:31:39Z">October 30, 2020 at 02:31</time></header><section class="archived-comment-content">If the above doesn't work - try running this. MS Disabled TLS1.0 &amp; 1.1 support to their gallery earlier in the year<br><br>[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12<br><br><br><br>May also need to to turn off FIPS Cryptography using the Local Policies<br><br>Can reenable after registering module</section></article></li><li id="wordpress-comment-34403" class="archived-comment"><article><header><strong>JE</strong> <time datetime="2020-11-17T23:13:02Z">November 18, 2020 at 00:13</time></header><section class="archived-comment-content">Thanks so much for sharing this! I'm new to PS and was tearing my hair out trying to figure out why I was getting nothing but angry red errors trying to to do anything regarding repositories from a server sitting behind a proxy.</section></article></li><li id="wordpress-comment-35662" class="archived-comment"><article><header><strong>Phil M</strong> <time datetime="2021-05-20T14:42:34Z">May 20, 2021 at 15:42</time></header><section class="archived-comment-content">Awesome stuff, I have been working on this for a while and this solved my issue downloading Powershell modules within our corporate environment.</section></article></li><li id="wordpress-comment-36896" class="archived-comment"><article><header><strong>sindhuja</strong> <time datetime="2021-10-20T16:11:39Z">October 20, 2021 at 17:11</time></header><section class="archived-comment-content">it worked super  :)</section></article></li><li id="wordpress-comment-41971" class="archived-comment"><article><header><strong>albvar</strong> <time datetime="2022-05-26T22:45:11Z">May 26, 2022 at 23:45</time></header><section class="archived-comment-content">Thank you, since I learned something new, thought I'd share.<br>You do not need to restart powershell, instead call . $profile # to reload the profile script</section></article></li><li id="wordpress-comment-45940" class="archived-comment"><article><header><strong>Guru</strong> <time datetime="2024-02-09T12:55:17Z">February 9, 2024 at 13:55</time></header><section class="archived-comment-content">Thank you so much it resolved my issue :)</section></article></li></ol></details>
</div>
