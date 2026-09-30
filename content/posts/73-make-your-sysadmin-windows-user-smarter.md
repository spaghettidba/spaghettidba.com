---
title: "Windows authenticated sysadmin, the painless way"
date: "2011-03-10T10:54:00"
slug: "make-your-sysadmin-windows-user-smarter"
source_url: "http://spaghettidba.com/2011/03/10/make-your-sysadmin-windows-user-smarter/"
url: "/2011/03/10/make-your-sysadmin-windows-user-smarter/"
categories: ["SQL Server"]
tags: ["SSMS", "Security", "Windows"]
---

Personally, I hate having a dedicated administrative account, different from the one I normally use to log on to my laptop, read my email, write code and perform all the tasks that do not involve administering a server. A dedicated account means another password to remember, renew periodically and reset whenever I insist typing it wrong (happens quite frequently).

I hate it, but I know I cannot avoid having it. Each user should be granted just the bare minimum privileges he needs, without creating dangerous overlaps, which end up avoiding small annoyances at the price of huge security breaches.

When I was working as a developer only, I was used to having my windows account registered as sysadmin on my dev box and, when I switched to a full time DBA role, it took me a while to understand how important it was to have a different sysadmin user for the production servers.

That said, one of the things that makes the use of dedicated administrative accounts awkward and frustrating is windows authentication in SSMS. While extremely handy when the user that has to log on to the database is the same logged on to windows, integrated security becomes pesky and uncomfortable when the database user is a different one.

No big deal, but launching SSMS as different user brings in some small annoying issues:
<ol>
	<li><strong>SSMS must be opened choosing “Run as…” from the context menu.</strong>
It’s the most common way to run a program as a different user, but I would happily live without this additional step.</li>
	<li><strong>The user’s credentials have to be typed in. </strong>
OK, seems trivial, but I find it annoying. Typically, users with elevated privileges are subject to more stringent password policies, that means longer passwords, no dictionary words, symbols. Having to type such a password once a day is enough for me.</li>
	<li><strong>No drag &amp; drop from other windows: neither files, nor text</strong>
This limit is imposed by windows, that filters the messages between processes in different security contexts.</li>
	<li><strong>Whenever there is more than one instance of SSMS running, it’s impossible to predict which one will open a file on double click</strong>
It’s like russian roulette. Want to play?</li>
	<li><strong>Settings are stored separately. Each modification to program settings has to be made on both profiles.</strong>
Application settings are stored somewhere under the user profile folder, or in the registry. In both cases, each user has different settings, stored in different locations.</li>
	<li><strong>Save and load dialogs point to different folders</strong>
By default, SSMS points to the user’s documents folder.</li>
</ol>
How to overcome these annoyances? A simple solution comes from a small tool released from <a href="http://technet.microsoft.com/en-us/sysinternals/default.aspx">Sysinternals</a> in January 2010.
<h2>Desktops</h2>
There are dozens, maybe hundreds of applications that allow windows users to create virtual desktops, similar to those found in Linux, but <a href="http://technet.microsoft.com/it-it/sysinternals/cc817881">Desktops</a> is different. To say it by Mark Russinvich’s (<a href="http://blogs.technet.com/b/markrussinovich/">blog</a>|<a href="http://twitter.com/#!/markrussinovich">twitter</a>) words:
<blockquote><em>Unlike other virtual desktop utilities that implement their desktops by showing the windows that are active on a desktop and hiding the rest, Sysinternals Desktops uses a Windows desktop object for each desktop. Application windows are bound to a desktop object when they are created, so Windows maintains the connection between windows and desktops and knows which ones to show when you switch a desktop.</em></blockquote>
In other words, Desktops is able to create a whole desktop process and then run new windows bound to that process. This also means that the main desktop process (explorer.exe) can be started in a different security context, simply terminating and restarting it. All the windows started from that moment on will be bound to their originating desktop process, hence to the same security context.

Let’s see how this can be achieved:
<ol>
	<li>Download and install <a href="http://download.sysinternals.com/Files/Desktops.zip">Sysinternals Desktops</a></li>
	<li>Open task manager, find the process named “explorer.exe” and note down its PID</li>
	<li>Create a new desktop and activate it</li>
	<li>Open task manager, find and kill the explorer process that has a PID different from the one you noted down</li>
	<li>From task manager, start a new process: “runas /user:somedomain\someuser explorer.exe”</li>
</ol>
Done! A new explorer process will be started with the credentials you supplied.

Smooth, isn’t it? Well, not much, still too complex for me:
<ul>
	<li>The PID from the original explorer process has to be noted down before creating the new desktop: thereafter it will be impossible to determine which desktop belongs to a process</li>
	<li>By default, windows restarts automatically explorer whenever it is killed, making our efforts in vain.</li>
</ul>
In order to work around these problems, I coded a small C# application called <em>RestartExplorer</em> that identifies the explorer process bound to the current desktop and restarts it as a different user.

The code is straightforward and you will find it <a href="http://dl.dropbox.com/u/49603664/BLOG/CODE/RestartExplorer_src.zip">attached to this post</a>. For those not so comfortable with Visual Studio, I also attached a<a href="http://dl.dropbox.com/u/49603664/BLOG/CODE/RestartExplorer_bin.zip"> compiled version</a>.

The core functionality consists of just a few rows of code:



```c
// Create a ProcessStartInfo object to pass credentials
System.Diagnostics.ProcessStartInfo psi = new System.Diagnostics.ProcessStartInfo();
if (!username.Equals(""))
{
    fixed (char* pChars = password.ToCharArray())
    {
        pass = new System.Security.SecureString(pChars, password.Length);
    }
    psi.UserName = user;
    psi.Password = pass;
    if(!domain.Equals(System.Environment.MachineName))
        psi.Domain = domain;
}

//Runs the Explorer process
psi.FileName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "explorer.exe"); // c:\windows\explorer.exe

//This has to be set to false when running as a different user
psi.UseShellExecute = false;
psi.ErrorDialog = true;
psi.LoadUserProfile = true;
psi.WorkingDirectory = "c:\\";

try
{
    //kill current explorer process
    IntPtr hWnd = FindWindow("Progman", null);
    PostMessage(hWnd, /*WM_QUIT*/ 0x12, 0, 0);
    //start a new explorer with the credentials supplied by the user
    System.Diagnostics.Process.Start(psi);
}
catch (Exception e)
{
    throw e;
}
```



Once run, the application simply asks for the credentials of the users that will run explorer.exe bound to the current desktop:

<a href="/wp-content/uploads/2011/03/restartexplorer.png"><img class="alignnone size-full wp-image-75" title="RestartExplorer" alt="" src="/wp-content/uploads/2011/03/restartexplorer.png" width="331" height="225" /></a>

By clicking OK, the explorer process gets terminated and immediately restarted under the specified security context. This creates a brand new desktop process, entirely dedicated to our administrative account.

To switch back to the regular users’ desktop, you just have to press the hotkey combination you set up in Desktops’ control panel or click on the tray icon, thus implementing something very similar to windows’ “quick user switch”, but quicker and more versatile.



<figure id="attachment_76" class="wp-caption alignnone" style="width: 394px; max-width: 100%;">
<a href="/wp-content/uploads/2011/03/desktops.png"><img class="size-full wp-image-76" title="Desktops" alt="" src="/wp-content/uploads/2011/03/desktops.png" width="394" height="250" /></a>
<figcaption class="wp-caption-text">Desktops tray panel</figcaption>
</figure>





<figure id="attachment_77" class="wp-caption alignnone" style="width: 389px; max-width: 100%;">
<a href="/wp-content/uploads/2011/03/desktops_control_panel.png"><img class="size-full wp-image-77" title="Desktops_Control_Panel" alt="" src="/wp-content/uploads/2011/03/desktops_control_panel.png" width="389" height="299" /></a>
<figcaption class="wp-caption-text">Desktops control panel</figcaption>
</figure>



So far we have solved our main issues:
<ol>
	<li><strong>SSMS can be started normally, by double clicking its icon</strong></li>
	<li><strong>No credentials to type</strong></li>
	<li><strong>Drag &amp; drop allowed from any window in this desktop</strong></li>
	<li><strong>SSMS opens the .sql files double clicked in this desktop</strong></li>
</ol>
<h2>Sharing settings</h2>
We still have to find a way to share application settings between different windows accounts.

We spent hours and hours configuring SSMS with our favourite keyboard settings, templates and all the other things that make our lives easier: we don’t want to set up everything from scratch for our administrator user. Is there a way to share the same settings we set up for the regular user?

Of course there is, and, again, it comes from Sysinternals and it is named <a href="http://technet.microsoft.com/en-us/sysinternals/bb896768">Junction</a>.

Junction is a tool that allows creating symbolic links on the NTFS file system. The concept of symbolic links has been present for many years in UNIX operating systems: symlinks are anchors to files or folders residing on different paths in the file system, that are treated as if they were physical files or folders in the path they are linked in.

In order to share settings between two users, we could create a symbolic link from the administrator user’s profile folder to the regular user’s profile folder, as represented in this picture:

<a href="/wp-content/uploads/2011/03/singlelink.png"><img class="alignnone size-full wp-image-78" title="singlelink" alt="" src="/wp-content/uploads/2011/03/singlelink.png" width="351" height="329" /></a>

Unfortunately, the profile folder contains a special file, named NTUSER.dat (the user’s registry keys), that cannot be opened concurrently on a desktop operating system.
The only possible solution is linking each subfolder in the profile path:

<a href="/wp-content/uploads/2011/03/multilink.png"><img class="alignnone size-full wp-image-79" title="multilink" alt="" src="/wp-content/uploads/2011/03/multilink.png" width="352" height="332" /></a>

A quick and easy way to accomplish this task is running this script:



```vb
Set fs = createObject(“Scripting.FileSystemObject”)
Set ws = createObject(“WScript.Shell”)

JunctionPath = “d:\Downloads\Junction\Junction.exe”

For each dir in fs.getFolder(“.”).subFolders
	DestPath = “..\AdminUser”
	If NOT Fs.folderExists(DestPath) Then
		Fs.createFolder(DestPath)
	End if
	If NOT Fs.folderExists(DestPath & “\” & dir.name) Then
		call ws.run(JunctionPath & “ “”” & DestPath & “\” & dir.name & “”” “”” & dir.path & “”””, 0, true)
	End if
Next
MsgBox “Profile linked successfully!”, vbInformation
```



Instructions:
<ol>
	<li>Copy the script code and save it as createJunction.vbs in the profile folder the links will point to (For instance, “c:\documents and settings\RegularUser”)</li>
	<li>Update “DestPath“ with the name of the user that will link the profile (For instance, “AdminUser”)</li>
	<li>Update “JunctionPath” with the path to Junction.exe</li>
	<li><span style="text-decoration:underline;">Create a backup copy</span> of the profile we will substitute with the links</li>
	<li>Delete all the folders in the admin profile, but keep all the files (especially NTUSER.dat)</li>
	<li>Go back to the folder where you saved the script and run it</li>
</ol>
For each subfolder in the regular user’s profile, the script will create a junction in the administrator user’s profile folder. This will not be directly visible from explorer: junctions are not different from real folders. Running DIR from the command prompt, instead, will reveal that we are dealing with something completely different:

<a href="/wp-content/uploads/2011/03/cmd2.png"><img class="alignnone size-full wp-image-80" title="Junctions" alt="" src="/wp-content/uploads/2011/03/cmd2.png" width="509" height="347" /></a>

<strong><span style="text-decoration:underline;">WARNING!!  Symbolic links act exactly as normal folders: this means that deleting a folder that is instead a symbolic link, will delete the link’s target folder. In other words, deleting a file from AdminUser’s profile folder, will delete the file from RegularUser’s profile! Be careful!</span></strong>

<strong><span style="text-decoration:underline;">
</span></strong>

What we achieved is a complete sharing of settings between our users. Going back to our original issue list:
<ol>
	<li><strong>Settings are saved in the same path. Every change in the program settings will be automatically saved in the original profile.</strong></li>
	<li><strong>Open and save dialogs point to the same documents folder.</strong></li>
</ol>
Mission accomplished!

However, registry settings will not be shared. There is a tool (<a href="http://www.tenox.tc/out/#regln">RegLN</a>) that allows creating symbolic links in the registry, but, personally, I don’t feel like exploring this possibility, that I find a bit dangerous.

In the end, SSMS settings are saved in the profile folder, which we already have shared. This is enough for me.

<strong>RESOURCES:</strong>
<ul>
	<li><a href="http://www.sqlconsulting.it/spaghettidba/desktops/RestartExplorer_src.zip">RestartExplorer (sources)</a></li>
	<li><a href="http://www.sqlconsulting.it/spaghettidba/desktops/RestartExplorer_bin.zip">RestartExplorer (binaries)</a></li>
	<li><a href="http://technet.microsoft.com/it-it/sysinternals/cc817881">Sysinternals Desktops</a></li>
	<li><a href="http://technet.microsoft.com/en-us/sysinternals/bb896768">Sysinternals Junction</a></li>
	<li><a href="http://www.tenox.tc/out/#regln">RegLN</a></li>
</ul>
