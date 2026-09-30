---
title: "Should I check tempdb for corruption?"
date: "2015-03-02T18:04:39"
slug: "should-i-check-tempdb-for-corruption"
source_url: "http://spaghettidba.com/2015/03/02/should-i-check-tempdb-for-corruption/"
url: "/2015/03/02/should-i-check-tempdb-for-corruption/"
categories: ["SQL Server"]
tags: ["CHECKDB", "DBCC CHECKDB", "corruption", "tempdb"]
---

You all know that checking our databases for corruption regularly is a must. But what about tempdb? Do you need to check it as well?

<a href="/wp-content/uploads/2015/03/corrupted1.png"><img class=" wp-image-915 size-full aligncenter" src="/wp-content/uploads/2015/03/corrupted1.png" alt="" width="256" height="256" /></a>

The maintenance plans that come with SQL Server do not run DBCC CHECKDB on tempdb, which is a strong indicator that it’s a special database and something different is happening behind the scenes. If you think that relying on the behavior of a poor tool such as maintenance plans to make assumptions on internals is a bit far-fetched, well, I see your point. However, you can get more clues by running DBCC CHECKDB against your tempdb and see what it outputs:
<code>
DBCC CHECKDB will not check SQL Server catalog or Service Broker consistency because a database snapshot could not be created or because WITH TABLOCK was specified.
</code>
See? Something special is happening here: CHECKDB cannot take a database snapshot to run the consistency checks and has to run as if WITH TABLOCK was specified.

Big deal? It depends. Running CHECKDB WITH TABLOCK means that you revert to the SQL2000 behavior, when table locks were taken to perform the consistency checks. This means that you might impact your workload with blocking. Not good.

Well, tempdb is recreated each time you start the instance and doesn’t contain any data worth worrying about, so you don’t need to check if it got corrupt, right? Again, it depends: tempdb might get so corrupted that it could start to throw errors at the sessions using it. It might also get corrupted to a point that triggers a stop of the instance. Not good.

So, if you check tempdb, you get blocking and if you don’t, you can get errors. What’s a reasonable balance?

Don’t check tempdb in the same schedule you use for checking user databases: find a reasonable maintenance window when any blocking issue is acceptable. Probably once a week is enough.

What should you do if you find corruption in tempdb? Don’t restart the instance right away: it could still survive for some time before problems arise. The whole point of checking tempdb is avoiding unpredicted downtime, so if you cycle the instance as soon as you find corruption, you’re killing the only reason to check it. Plan downtime with your users and cycle the instance when it causes less harm to your business.
Moreover, if something corrupted your tempdb, it has likely corrupted your user databases, so make sure you check everything before shutting down the instance (time to take tail-log backups?).

If your tempdb gets corrupted, restarting the instance won’t be enough to make corruption go away: you will have to stop SQL Server, delete the files manually and the start SQL Server to let it create the new tempdb files.

Even if you don’t mind losing the data stored in tempdb, getting corruption is a sign that something went wrong: make sure you investigate the issue and find the root cause. It could be a problem with the I/O subsystem or a malfunctioning RAM module or something else: fix the root cause before it affects the user databases.

<strong>Call to action:</strong>

Are you checking your tempdb for corruption? If you are not, don’t panic: choose an appropriate schedule and start checking it.
