---
title: "Code signing for mere mortals"
date: "2023-06-10T12:35:26"
slug: "code-signing-for-mere-mortals"
source_url: "http://spaghettidba.com/2023/06/10/code-signing-for-mere-mortals/"
url: "/2023/06/10/code-signing-for-mere-mortals/"
categories: ["Uncategorized"]
tags: ["WorkloadTools", "XESmartTarget", "codesigning"]
---

<!-- wp:paragraph -->
<p>Well, turns out code signing is pretty complex, so I'm writing this blog post as a guide for my future self. I hope he will appreciate, and perhaps some of you may find it useful as well.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">The need for code signing</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>There is a lot of malware out there, we all know it, so you'd better be careful with what you download and install on your computer. Browsers try to help with that and will warn you when you download a suspicious piece of software:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1706,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2023/06/image.png"><img src="/wp-content/uploads/2023/06/image.png" alt="" class="wp-image-1706" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>You will have to be very persistent if you really mean to keep it:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1708,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2023/06/image-1.png"><img src="/wp-content/uploads/2023/06/image-1.png" alt="" class="wp-image-1708" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>If you try to install it, Windows will warn you again that you shouldn't really install random stuff from the Internet:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1710,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2023/06/image-2.png"><img src="/wp-content/uploads/2023/06/image-2.png" alt="" class="wp-image-1710" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>Why does happen with some files and doesn't happen with the Chrome installer or Acrobat reader? Because those setup kits are signed with a certificate from Google and Adobe, released by a certification authority that checks that Google is actually Google and not a disgruntled random guy pretending to be Google.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This means you can sign your code too, you just need to get a code signing certificate from a certification authority and they will be happy to give you one in exchange for money.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Get a Code Signing Certificate</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>There are many certification authorities and I don't have enough experience to recommend one in particular. In my case, I ended up working with <a href="http://digicert.com">DigiCert</a>, because at the time they offered complimentary certificates for MVPs.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>After registering an account, the first thing you have to do is request a new code signing certificate.  The cert authority will perform all required checks, like checking your ID/passport, set up a video call where you sign a form in front of the operator... long story short, they will make sure that you are who you claim you are. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>After the check is done, they will issue a certificate, that you can use to sign your code. Hooray!</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>At this time, you will also get a <strong>private key</strong>, that you will need to perform all the operations on your code signing certificate. The private key is another certificate, that you will have to make sure to keep in a safe place. Starting from June 1st 2023, regulations require that you store your private keys on a <a href="https://knowledge.digicert.com/generalinformation/new-private-key-storage-requirement-for-standard-code-signing-certificates-november-2022.html">hardware token</a> that provides strong encryption or online in an <a href="https://knowledge.digicert.com/solution/digicert-keylocker.html">encrypted key vault</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Either way, make sure you don't lose it.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Sign your code with the Code Signing Certificate</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>In order to sign your code, you will need to install the Windows SDK Signing Tools, which are part of the Windows SDK. You can <a href="https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/">download the appropriate version</a> for your OS from Microsoft.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The tool that you're looking for is called <code>signtool.exe</code> and you can find it in <code>C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe</code></p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>Usage: signtool &lt;command&gt; &#091;options]

  Valid commands:
    sign       --  Sign files using an embedded signature.
    timestamp  --  Timestamp previously-signed files.
    verify     --  Verify embedded or catalog signatures.
    catdb      --  Modify a catalog database.
    remove     --  Remove embedded signature(s) or reduce the size of an
                   embedded signed file.</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>The command that we need is "sign". There are a lot of options for this command and I have a very limited knowledge of what does what. What did the trick for me is this combination of parameters:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>signtool.exe sign 
    /f &lt;path to your cert&gt; 
    /p &lt;password to open the cert&gt; 
    /sha1 &lt;sha1 fingerprint&gt; 
    /t &lt;url of the timestamp server&gt; 
    /d &lt;description of the content&gt; 
    /fd &lt;file digest algorithm&gt;
    &lt;path of the file to sign&gt;</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>In my case, to sign <a href="https://github.com/spaghettidba/XESmartTarget">XESmartTarget</a>, I entered this command:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>signtool sign 
    /f "c:\digicert\codesigning2023.pfx"
    /p "MySuperDuperPassword"
    /sha1 "00AABBCCDDEEFF0011223344556677889900AABB"
    /t "http://timestamp.digicert.com"
    /d "XESmartTarget" 
    /fd sha1
    "c:\temp\XESmartTarget_x64.msi"</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>Every parameter is in a new line for readability, but you command will be on a single line. </p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Looks pretty easy, but I can tell you it's not. Well, not for me at least. In order to produce the above command line, you will need a number of things:</p>
<!-- /wp:paragraph -->

<!-- wp:list {"ordered":true} -->
<ol><!-- wp:list-item -->
<li>The certificate in .pfx format</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>The password of the certificate</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>The sha1 fingerprint</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>The URL of the timestamp server</li>
<!-- /wp:list-item --></ol>
<!-- /wp:list -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Convert your code signing certificate to the .pfx format</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The certification authority will provide the certificate in many possible formats. Not all formats are good for you: you need .pfx because that's the one that works with signtool. Maybe it works with other formats, I don't know, but .pfx worked for me.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In my case, DigiCert provided the certificates either in .p7b, .cer, .crt or .pem format. All these formats are base64 encoded and can be opened with a text editor. If you open a certificate in notepad, you will see something like this:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>-----BEGIN CERTIFICATE-----
NIIG3TCCBFmaAqIBAgIEDZk+BM+4uNO1I19N3Mqg0zANBgfqhkiGrw0BAQsFQDBp
MQewCRYDVaQGEwJVUzeXMBUeA1UBChMNRGlnaULlcnQqIEauYy4xRTA/BbNWBAbT
..................lots of gibberish..................
bNWKqgD+rgfsIhBMsEn0ulSMt0JE7q32PeBeVETFv1nQfnljjVA==
-----END CERTIFICATE-----</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>The .pfx format is different, it is a binary format and cannot be opened with a text editor.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In order to convert your .pem certificate to .pfx format, you will need another tool called openssl. You can download and install for your OS or you can use a winget command: <code>winget install openssl</code>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Once you have openssl, you can use this command to convert your base64 certificate to the .pfx format:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>openssl pkcs12 -inkey c:\digicert\privatekey.pem -in c:\digicert\codesigning.crt -export -out c:\digicert\codesigning.pfx</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>Openssl will prompt for the password of the private key. Did I mention you should not lose it?</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>Enter pass phrase for c:\digicert\privatekey.pem: &lt;-- private key password
Enter Export Password:   &lt;-- this is the password of the exported certificate
Verifying - Enter Export Password: &lt;-- type again</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>The export password is the one that you will need to pass to signtool in the /p parameter.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Convert your private key to .pem format</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>If your private key is not in base64 format, openssl will fail:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>Could not read private key from -inkey file from c:\digicert\privatekey.p12</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>I don't remember exactly how, but my private key is in .p12 format (it's a binary encrypted format): if that is all you have, you will need to convert it first.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Openssl can convert the private key for you:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>openssl pkcs12 -in c:\digicert\privatekey.p12 -out c:\digicert\privatekey.pem -clcerts</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>Now that you have the private key in the .pem format, you can go back to the previous step and generate the .pfx certificate.</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Get the certificate fingerprint</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Your certitification authority should display the certificate sha thumbprint on the certificate order in your personal area. At least, DigiCert does. This information can be displayed as "thumbprint" or "fingerprint" and it's a binary string.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>If you can't find this information on the certificate order, you can extract it from the certificate itself, again using openssl:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>openssl x509 -noout -fingerprint -sha1 -inform pem -in "C:\digicert\codesigning.pem"
</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>The output will look like this:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>sha1 Fingerprint=00:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:00:AA:BB</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>This fingerprint should match the one you have on your certificate order and must be used in the signtool command line without the ":". In this case it becomes <code>00AABBCCDDEEFF0011223344556677889900AABB</code></p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Putting it all together</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Once you have your certificate ready, you can use signtool to sign your artifacts. In order to make this process easier, I created a couple of scripts that I use in Visual Studio builds as post build scripts.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>My Wix setup project has this Post-build Event Command Line:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>call $(ProjectDir)postbuild.bat "!(TargetPath)" "$(TargetDir)$(SolutionName)_$(Platform)$(TargetExt)"</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>postbuild.bat looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>powershell.exe -ExecutionPolicy Bypass -NoProfile -NonInteractive -File %~dp0\SignMsi.ps1 -InputFile %1 -OutputFile %2</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>SignMsi.ps1 is where all the magic happens:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"powershell"} -->
<pre class="wp-block-syntaxhighlighter-code">[CmdletBinding()]
Param(
    [Parameter(Mandatory=$True,Position=1)]
    [string]$InputFile,
    [Parameter(Mandatory=$True,Position=2)]
    [string]$OutputFile
)


if(-not (Test-Path $PSScriptRoot\SignParams.ps1)) 
{
    Write-Warning "No code signing is applied to the .msi file."
    Write-Warning "You need to create a file called SignParams.ps1 and provide signing info."
    Move-Item $InputFile $OutputFile -Force
    exit
}

# read paramters
$signParams = get-content $PSScriptRoot\SignParams.ps1 -Raw
Invoke-Expression $signParams

$params = $(
     'sign'
    ,'/f'
    ,('"' + $certPath + '"')
    ,'/p'
    ,('"' + $certPass + '"')
    ,'/sha1'
    ,$certSha
    ,'/t'
    ,('"' + $certTime + '"')
    ,'/d'
    ,'"XESmartTarget"'
    ,"/fd"
    ,"sha1"
)

&amp; $signTool ($params + $InputFile)

Write-Output "Moving $InputFile --&gt; $OutputFile"
Move-Item $InputFile $OutputFile -Force
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>SignMsi.ps1 looks for a file named SignParams.ps1 in the same folder and if it finds the file if processes the contents and proceeds to sign the artifacts, otherwise it just ignores signing, which can be good for pre-prod or test environments.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The SignParams.ps1 file contains the parameters needed by signtool and it looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"powershell"} -->
<pre class="wp-block-syntaxhighlighter-code">$signTool = "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
$certPath = "c:\digicert\codesigning2023.pfx"
$certPass = "MySuperDuperPassword"
$certSha = "00AABBCCDDEEFF0011223344556677889900AABB"
$certTime = "http://timestamp.digicert.com"</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>This should make your life pretty easy.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Cheers!</p>
<!-- /wp:paragraph -->
