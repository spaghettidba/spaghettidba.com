---
title: "Life behind a proxy server: downloading content for SSMS Help Viewer"
date: "2019-05-09T17:24:10"
slug: "life-behind-a-proxy-server-downloading-content-for-ssms-help-viewer"
source_url: "http://spaghettidba.com/2019/05/09/life-behind-a-proxy-server-downloading-content-for-ssms-help-viewer/"
url: "/2019/05/09/life-behind-a-proxy-server-downloading-content-for-ssms-help-viewer/"
categories: ["SQL Server"]
tags: ["Help", "Help Library Manager", "SSMS"]
---

<!-- wp:paragraph -->
<p>Life behind a proxy server can be problematic. Not every software out there is tested correctly for proxy interaction and oftentimes the experience for the corporate user is a bit frustrating. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>I blogged about this before, <a href="/2017/12/19/recovering-the-psgallery-repository-behind-a-corporate-proxy/">regarding Powershell Gallery</a> and regarding how to download and install content for the SSMS Help Viewer in <a href="/2014/09/25/installing-sql-server-2014-language-reference-help-from-disk/">SQL Server 2014</a> and <a href="/2016/10/17/installing-sql-server-2016-language-reference-help-from-disk/">SQL Server 2016</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>When I tried to update my post for SQL Server 2017, I got stuck, because my "hack" stopped working with Help Viewer 2.3 and none of the things I tried was working. Bummer.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>The problem:</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Microsoft Help Viewer is unable to dowload the help content from the Microsoft website and if you click the error message on the bottom left of the status bar, it shows an error similar to this: "<code>The web server has reported an error for https://services.mtps.microsoft.com/ServiceAPI/catalogs/Dev15/en-US: ProtocolIError/ProxyAuthenticationRequired</code>"</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>How to fix it:</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>But there had to be a better way to do this and, I fiddled with it until I got it to work. Basically, all you have to do is instruct your applications to use a proxy server, with default authentication.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Discover what proxy server you are using: sometimes the proxy configuration only contains the URL of the autoconfiguration script (the pac file), but you don't know what proxy is effectively in use. To display this information, open a cmd prompt and run this:<br><br><code>netsh winhttp show proxy</code><br><br>You should see an output similar to this:<br><code><br>Current WinHTTP proxy settings:<br><br>    Proxy Server(s) :  http=proxy.mycompany.lan:8090<br>    Bypass List     :  (none)</code><br></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Add the proxy information to the following text fragment and copy it to the clipboard:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"xml"} -->
<pre class="wp-block-syntaxhighlighter-code brush: xml; notranslate">&lt;system.net&gt;
    &lt;settings&gt;
        &lt;ipv6 enabled="true" /&gt;
    &lt;/settings&gt;
    &lt;defaultProxy enabled="true" useDefaultCredentials="true"&gt;
        &lt;proxy bypassonlocal="True" proxyaddress="http://MyProxyServer:MyProxyPort"/&gt;
    &lt;/defaultProxy&gt;
&lt;/system.net&gt;</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Run your favourite text editor <strong>as Administrator</strong> and open the following files in the Help Viewer installation folder (on my computer it's <code>"C:\Program Files (x86)\Microsoft Help Viewer\v2.3"</code>): </p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><li><code>HlpCtntMgr.exe.config</code></li><li><code>HlpViewer.exe.config</code></li></ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>Add the text fragment to both files, <strong>inside the <code>&lt;configuration&gt;</code> tag</strong>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This is enough to let the the Help Viewer UI download and display the list of available content from the Microsoft website. Unfortunately, the actual transfer operation is performed by the BITS service, which has to be intructed to use a proxy server and complains with the following error message: "<code>an error occurred while the bits service was transferring</code>". </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This is done by changing a registry value. The key is the following:<br><code>HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\BITS</code><br>And the value is <code>UseLmCompat</code>, which has to be set to 0.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>You can do this easily by saving the following lines to a text file, save it with the .reg extension and merge it to you registry by double clicking.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code -->
<pre class="wp-block-syntaxhighlighter-code brush: plain; notranslate">Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\BITS]
"UseLmCompat"=dword:00000000</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Restart the BITS service (Background Intelligent Transfer Service).</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Now you can go ahead and update you help library. Enjoy!</p>
<!-- /wp:paragraph -->
