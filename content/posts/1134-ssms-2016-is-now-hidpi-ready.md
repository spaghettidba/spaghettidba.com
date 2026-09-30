---
title: "SSMS is now High-DPI ready"
date: "2016-08-18T15:15:18"
slug: "ssms-2016-is-now-hidpi-ready"
source_url: "http://spaghettidba.com/2016/08/18/ssms-2016-is-now-hidpi-ready/"
url: "/2016/08/18/ssms-2016-is-now-hidpi-ready/"
categories: ["SQL Server"]
tags: ["4K", "High DPI", "SSMS", "Scaling", "Surface Pro 3", "Windows 10"]
---

One of the most popular posts on this bog describes <a href="/2015/10/14/ssms-in-high-dpi-displays-how-to-stop-the-madness/">how to enable bitmap scaling is SSMS</a> on high DPI displays, which is a sign that more and more people are starting to use 4K displays and are unhappy with SSMS's behaviour at high DPI. The solution described in that post is to enable bitmap scaling, which renders graphic objects correctly, at the price of some blurriness.
<p style="text-align:left;">The good news is that starting with <a href="https://blogs.msdn.microsoft.com/sqlreleaseservices/announcing-sql-server-management-studio-16-3-august-2016-release/">SSMS 16.3</a> high DPI displays are finally first class citizens and SSMS does its best to scale objects properly. By default, SSMS will keep using bitmap scaling: in order to enable DPI scaling you will have to use a manifest file.</p>

<ol>
 	<li style="text-align:left;">Merge this key to your registry:</li>
</ol>



```text
Windows Registry Editor Version 5.00[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\SideBySide]
"PreferExternalManifest"=dword:00000001
```



<ol start="2">
 	<li style="text-align:left;">Save this manifest file to “C:\Program Files (x86)\Microsoft SQL Server\130\Tools\Binn\ManagementStudio\Ssms.exe.manifest” using UTF-8 format:</li>
</ol>



```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0" xmlns:asmv3="urn:schemas-microsoft-com:asm.v3">
    <asmv3:application>
        <asmv3:windowsSettings xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">
            <dpiAware>True</dpiAware>
        </asmv3:windowsSettings>
    </asmv3:application>
    <dependency>
        <dependentAssembly>
            <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls" version="6.0.0.0" processorArchitecture="X86" publicKeyToken="6595b64144ccf1df" language="*" />
        </dependentAssembly>
    </dependency>
    <dependency>
        <dependentAssembly>
            <assemblyIdentity type="win32" name="debuggerproxy.dll" processorArchitecture="X86" version="1.0.0.0"></assemblyIdentity>
        </dependentAssembly>
    </dependency>
</assembly>
```



<p style="text-align:left;">This is a huge improvement over the bitmap scaling solution we had to use up to now: no more blurriness and proper fonts are used in SSMS.</p>
<p style="text-align:left;">For comparison, this is how bitmap scaling renders in SSMS 2014:</p>
<p style="text-align:left;"><a href="/wp-content/uploads/2016/08/ssms20141.png"><img class="alignnone size-full wp-image-1141" src="/wp-content/uploads/2016/08/ssms20141.png" alt="SSMS2014" width="604" height="462" /></a></p>
<p style="text-align:left;">And this is how DPI scaling renders is SSMS 16.3, with scaling set to 200%:</p>
<p style="text-align:left;"><a href="/wp-content/uploads/2016/08/ssms20161.png"><img class="alignnone wp-image-1140 size-full" src="/wp-content/uploads/2016/08/ssms20161.png" alt="SSMS2016" width="604" height="462" /></a></p>
<p style="text-align:left;">As you can see, it's not perfect yet (for instance, I had to change the grid font size to 9pt. in order to have readable fonts).</p>
<p style="text-align:left;">However, the GUI is much more readable now. For instance, look at the difference in object explorer: (click on the image to open fullsize and see the difference)</p>
<p style="text-align:left;"><a href="/wp-content/uploads/2016/08/objexp.png"><img class="alignnone wp-image-1142 size-full" src="/wp-content/uploads/2016/08/objexp.png" alt="objexp" width="604" height="285" /></a></p>
<p style="text-align:left;">Now that your favourite tool is working in high DPI displays, nothing is holding you back from buying one of those fancy 4K laptops!</p>
