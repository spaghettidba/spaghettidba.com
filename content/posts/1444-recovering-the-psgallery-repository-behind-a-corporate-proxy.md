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
