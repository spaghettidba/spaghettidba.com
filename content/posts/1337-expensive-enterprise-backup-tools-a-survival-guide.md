---
title: "Expensive Enterprise Backup Tools – A survival guide"
date: "2017-09-13T11:15:16"
slug: "expensive-enterprise-backup-tools-a-survival-guide"
source_url: "http://spaghettidba.com/2017/09/13/expensive-enterprise-backup-tools-a-survival-guide/"
url: "/2017/09/13/expensive-enterprise-backup-tools-a-survival-guide/"
categories: ["SQL Server"]
tags: ["DPM", "Data Domain", "Networker", "backup"]
---

If you’re working for a big company, chances are that your IT already has a strategy and tools for dealing with backups. Many objects need to backed up (files, emails, virtual machines, databases…) and vendors are happy to provide software solutions for all those needs.

Usually, the first type of object that has to be protected is files: every company, even the smaller ones, have file servers with lots of data that has to be regularly backed up, so the data protection solution found in the majority of companies is typically built around the capabilities and features of backup tools designed and engineered for protecting the file system.

The same tools are probably capable of taking backups of different types of objects, by means of “plug-ins” or “agents” for databases, e-mail servers, virtual machines and so on. Unfortunately, those agents are often delusional and fail to deliver what they promise.

With regard to SQL Server database backups, these are the most common issues:

<strong>1. Naming things wrong</strong>
It’s not surprising that backup tools built for protecting the file system fail to name things properly when it comes down to database backups. What you often find is that transaction log backups are called “incremental backups” or full backups are instead called “snapshots”, according to whichever the naming convention is in the main file system backup process. It’s also not uncommon to find transaction log backups going under the name of “archive log backups”, because this is what they are called like in Oracle. This naming mismatch is potentially dangerous, because it can trick the DBA into choosing the wrong type of backup. The term “DBA” is not used here by accident, which takes us to the next point.

<strong>2. Potentially dangerous separation of duties</strong>
Backup tools are often run and controlled by windows admins, who may or may not be the same persons responsible for taking care of databases. Well, surprise: if you’re taking backups you’re responsible for them, and backups are the main task of the DBA, so… congrats: you’re the DBA now, like it or not.
If your windows admins are not ok with being the DBA, but at the same time are ok with taking backups, make sure that you discuss who gets accountable for data loss when thing go south. Don’t get fooled: you must not be responsible for restores (which, ultimately, is the reason why you take backups) if you don’t have control over the backup process. Period.

<strong>3. One size fits all</strong>
<img class="alignnone size-full wp-image-1356" src="/wp-content/uploads/2017/09/onesize.png" alt="" width="414" height="194" />
Some backup tools won’t allow you to back up individual databases with special schedules and policies, but will try to protect the whole instance as an atomic object, with a “one size fits all” approach. Be careful not to trade safety for simplicity.

<strong>4. Missing backup / restore options</strong>
Most (if not all) third-party backup tools do not offer the same flexibility that you have with native backups, so you will probably miss some of the backup/restore options. I’m not talking about overly exotic options such as KEEP_REPLICATION or NEW_BROKER: in some cases you may not be able to restore with NORECOVERY. Whether this is going to be a problem or not, only you can tell: go and check the possibilities of your data protection tool, because you might need a feature that is unavailable and you might need it when it’s too late.

<strong>5. Dangerous internal workings</strong>
Not all backup tools behind the covers are acting as you would expect. For instance, Microsoft Data Protection Manager (DPM) is unable to take transaction log backups streaming them directly to the backup server, but needs to write the backup set to a file first. I bet you can see what’s wrong with this idea: if your transaction log is growing due to an unexpected spike in activity, the only way to stop if from growing and eventually fill the disk is to take a t-log backup, but the backup itself will have to be written to disk. In the worst case, you won’t have enough disk space to perform the backup, so it will simply fail. In a similarly catastrophic scenario, the transaction log file may try to grow again while the log backup is being taken, resulting in failure to allocate disk space.It is incredibly ironic how you need disk space to perform a backup and you need a backup to release disk space, so I am just going to guess that the developers of DPM were simply trying to be funny when they designed this mechanism.

<strong>6. Incoherent schedules</strong>
Some backup tools are unable to provide a precise schedule and instead of running the backup operation when due, they add it to a queue that will eventually run everything. This may look like a trivial difference, but it is not: if your RPO is, let’s say, 15 minutes, transaction log backups have to occur every 15 minutes at most, so having transaction log backups executed from a queue would probably mean that some of them will exceed the RPO if at least one of the backups takes longer than usual. Detecting this condition is fairly simple: you just have to look at your backupset table in msdb.

<strong>7. Sysadmin privileges</strong>
All third-party backup applications rely on an API in SQL Server which is called “Virtual Device Interface” (or VDI in short). This API allows SQL Server to treat backup sessions from your data protection tool as devices, and perform backup/restore operations by using these devices as source/destination.
One of the downsides of VDI is that it <a href="https://connect.microsoft.com/SQLServer/feedback/details/775819/backup-and-restore-commands-using-vdi-require-sysadmin-role-membership">requires sysadmin privileges</a> on the SQL Server instance and Administrator privileges on the Windows box. In case you’re wondering, no: it’s not strictly necessary to have sysadmin privileges to back up a database.

<strong>8. VSS backups</strong>
A number of backup tools rely on taking VSS snapshots of the SQL Server databases. SQL Server supports VSS snapshots and has a provider for that. Unfortunately, it’s not impossible to see VSS backups <a href="http://sqlblog.com/blogs/tibor_karaszi/archive/2014/04/09/does-your-3-rd-party-backup-software-ruin-your-sql-server-backup-plan.aspx">interfering with other types of backups</a> and/or failures initializing the VSS provider, which require a reboot to fix.

<strong>9. VM backups</strong>
Some backup vendors are more focused on backing up the whole virtual machine rather than the single database / instance that you want to protect. Taking a whole machine backup is different and you have to make sure that you understand what that means, especially compared to taking full, diff or log backups. For instance, did you know that taking VM backups is based on the snapshot feature of the hypervisor, which in turn runs VSS backups of snapshot-aware software, like SQL Server?

<strong>10. Interfere with other features</strong>
Oftentimes, these enterprise-grade super-expensive backup tools live on the assumption that they’re the only one tool you will ever use, and refuse to play nicely with other SQL Server features. For instance, they will happily try to back up transaction log for databases that are part of log shipping (see point #3), ending up with broken log chains.

<strong>11. Agents</strong>
All backup tools that take advantage of the VDI API require that you install an agent application locally on the SQL Server machine. While having an agent running on the windows machine is not overly concerning per se, on the other hand this means that the agent itself will have to be patched and upgraded from time to time, often requiring that you restart the machine to apply changes.
This also means that you might run into bugs in the agent that could prevent taking backups until you patch/upgrade the agent itself.

<strong>12. Illogical choices</strong>
Some data protection tools will force illogical policies and schedules on you for no reason whatsoever. For instance, EMC Networker cannot take transaction log backups of master and model (which must/should be in simple recovery anyway), so when you schedule transaction log backups for all databases on the instance, it won’t skip them, but take a full backup instead. Both databases are usually quite small, but still, taking a full backup every 15 or 5 minutes is less than ideal.

<strong>13. Not designed with availability in mind</strong>
Backing up the file system is very different from backing up SQL Server databases, as one might expect. One of the key differences is that with SQL Server databases you don’t have to deal with RPO and RTO only, but the way that you back up your databases can have a serious impact on the availability of the databases itself. To put that simply: if you don’t take transaction log backups, nothing truncates your logs, so it keeps growing and growing until space runs out either on the log file (and the database stops working) or on the disk (and the whole instance stops working). Backup operations are critical for RDBMSs: if something or somebody commits to performing backups every x minutes, that commitment MUST be fulfilled. For the record, many backup tools that offer the “one size fits all” approach will try to take full and transaction logs on the same schedule, so they will simply skip transaction log backups while taking full backups. This means that you might be exceeding your RPO, with no clear indication of that happening.

<strong>14. No support for SQL Server compression or encryption</strong>
A number of backup tools offer their own compression and encryption features (again, because the file system does not offer those), so they will try in each and every possible way to push their shiny-enterprise-expensive features instead of what you already have.
Compression helps keeping the backup and restore times under control, by keeping the size of the backup sets small: this means that the number of bytes that travels across the network will be smaller. Nowadays, the majority of backup solutions supports Data Domain or equivalent solutions: smart storage appliances that offer powerful compression and deduplication features to avoid storing the same information multiple times. These dedupe features can be incredibly effective and reduce immensely the amount of disk space needed for storing backups. Some data domains offer deduplication inside the appliance itself: data has to travel the network and reach the data domain, which takes care of breaking the file in blocks, calculate a hash on the blocks and store only the blocks whose hash was not found inside the data domain. This behavior is already clever enough, but some data domains improved it even further, with host deduplication (DDBoost, to name the most prominent product). Basically, what happens with host deduplication is that the hash of the blocks is calculated on the host and not on the data domain: in this way, all the duplicate blocks do not need to travel across the network, hence reducing the amount of time needed for backup operations.
<img class="alignnone size-full wp-image-1357" src="/wp-content/uploads/2017/09/ddboos5t.png" alt="" width="537" height="214" />
These dedupe technologies are incredibly useful and also allow backup admins to show to their boss all those shiny charts that depict how cleverly the data domain is reducing disk usage across the board. This is going to be so amazing that the backup admin will not allow you to deteriorate his exceptional dedupe stats by using any backup option that prevents deduplication from happening. The two main enemies of Data Domain efficiency are compression and encryption in the source data. Compression of similar uncompressed files does not produce similar compressed files, so chances of deduplication are much slimmer. Encryption of backups is non-deterministic, which means that two backup sets of the same exact database will be completely different, bringing down deduplication rates close to zero.
While the need for encryption is probably something that your backup admins could live with, they will try in every possible way to make you get rid of backup compression. Letting the data domain take care of compression and deduplication can be acceptable in many cases, but it must not be a hard rule, because of its possible impact on RTO.
The real issue with deduplication can be dramatically evident at restore time: the advantage of deduplication will be lost, because <a href="https://dba.stackexchange.com/questions/126154/sql-server-backups-on-datadomain">all the blocks that make up your backups will have to travel across the network</a>.
Long story short: at backup time, deduplication can be extremely effective, but, at restore time, backup compression can be much more desirable and can make the difference between meeting and not meeting your RTO.

<strong>15. No separation of duties</strong>
What often happens with general-purpose backup tools is that management of a single object type is not possible. A number of tools will allow you to be a backup admin on the whole infrastructure or nothing, without the ability to manage database backups only. This may or may not be a problem, depending on how dangerous your windows admins consider your ability to manage the backup schedules of Exchange servers and file servers.
Some tools offer the possibility to create separate tenants and assign resources and schedules to particular tenants, each with its own set of administrators. This feature often comes with limitations, such as the inability to share resources throughout multiple tenants: if tape drives can be assigned to a single tenant and the company only owns a single tape drive, this option obviously goes out of the table.

<strong>16. No management tools</strong>
Often, the management tools offered by these backup vendors are simply ridiculous. Some use web applications with java applets or similar outdated/insecure technologies. Some offer command line tools but no GUI tools, some the other way around. The main takeaway is: make sure that your backup vendor gives you the tools that you need, which <strong>must</strong> include a command line or anything that can be automated.

<strong>17. Ridiculous RPO/RTO</strong>
The developers of some backup tools (DPM, I’m looking at you) decided that forcing a minimum schedule frequency of 15 minutes was a great idea. Well, in case you’re wondering, it’s not.
Other tools manage the internal metadata so dreadfully that loading the list of available backup sets can take forever, hence making restores excruciating exercises, that often fall outside of the requested RTO.
Make sure that tool you are using is able to deliver the RPO and RTO you agreed upon with the owners of the data.

<strong>Bottom line is</strong>: don’t let your backup vendor impose the policies for backups and restores. Your stakeholders are the owners of the data and everyone else is not entitled to dictate RPOs and RTOs. Make sure that your backup admins understand that your primary task is to perform restores (not backups!) and that the tool they are using with Exchange might not be the best choice for you. Talk to your backup admins, find the best solution together and test it across the board, with or without the use of third party tools, because, yes, native SQL Server backups can be the best choice for you.
