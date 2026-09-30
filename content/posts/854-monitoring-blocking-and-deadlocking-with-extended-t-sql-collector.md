---
title: "Monitoring blocking and deadlocking with Extended T-SQL Collector"
date: "2014-12-12T18:29:25"
slug: "monitoring-blocking-and-deadlocking-with-extended-t-sql-collector"
source_url: "http://spaghettidba.com/2014/12/12/monitoring-blocking-and-deadlocking-with-extended-t-sql-collector/"
url: "/2014/12/12/monitoring-blocking-and-deadlocking-with-extended-t-sql-collector/"
categories: ["SQL Server"]
tags: ["Blocking", "Deadlocks", "Extended Events", "Extended T-SQL Collector", "Monitoring"]
---

Monitoring blocking and deadlocking hasn't always been easy. Sometimes, the tools available in SQL Server are not as friendly as we would like them to be.

Some are very useful for alerting, but don't provide a simple way to capture additional information about the event. For instance, a simple SQLAgent alert for "deadlocks/sec &gt; 0" is enough to shoot an email to the DBAs whenever a deadlock happens, but it doesn't provide a simple way to capture the deadlock graph and include it in the email or save it to a destination table.

Some other methods are very useful for capturing all the information we need, but don't provide a way to fire an alert when the event is captured. For instance, capturing blocked process reports with an Extended Events session is very easy, but firing an alert when the event is captured is not.

In this post I will show you an easy way to combine monitoring and alerting using the cutting edge monitoring technology available in SQL Server: Extended Events.

Extended Events are cool: they can capture events not available otherwise and they impact the monitored server much less than other capture technologies (e.g. SQL Trace). However, as far as alerting is concerned, they are still lacking a piece of the puzzle. In fact Extended Events don't provide a built-in way to fire an alert whenever an event is captured. With SQL Trace we had Event Notifications that did exactly this, using a Service Broker queue.

It would be great if there was a way to capture events with an XE session, store them to a table for later analysis and alert as soon as the event occurs.

The good news is that <strong> a tool that can do that already exists</strong> and even better news is that <strong>it's free and open source</strong>! Its name is <a href="http://extendedtsqlcollector.codeplex.com/">Extended T-SQL Collector</a>.

Extended T-SQL Collector allows you to combine Extended Events and Data Collector, with the addition of alerting for interesting events. All you have to do is <a href="http://extendedtsqlcollector.codeplex.com/">download</a> your copy of Extended T-SQL Collector, install it on your server and then set up a collection set for blocking and deadlocking.

If you ever had the chance to play with Data Collector and tried to create a custom collection set, you probably have noticed that it's not as easy as it should. This part of the Data Collector is missing a Graphical User Interface and requires messing with XML. Nobody likes XML. If you do, be aware that you're in a very small minority.

<H3>Creating the collection set with the GUI</H3>

With Extended T-SQL Collector you can create a collection set to capture blocked processes and deadlocks using the GUI.
Here's how you do it:

<strong>1.</strong> Start the Collectionset Manager and connect it to your instance.

<strong>2.</strong> If the custom collector types provided by Extended T-SQL Collector are not installed, install them

<a href="/wp-content/uploads/2014/12/setup.png"><img class="alignnone size-full wp-image-863" src="/wp-content/uploads/2014/12/setup.png" alt="setup" width="604" height="340" /></a>

<strong>3.</strong> Right click the "Collection Sets" node and select "Add"

<a href="/wp-content/uploads/2014/12/blockingdeadlocking0.png"><img class="alignnone wp-image-855 size-full" src="/wp-content/uploads/2014/12/blockingdeadlocking0.png" alt="BlockingDeadlocking0" width="604" height="340" /></a>

<strong>4.</strong> Fill the information about your Collection Set and hit "Save"

<a href="/wp-content/uploads/2014/12/blockingdeadlocking1.png"><img class="alignnone size-full wp-image-856" src="/wp-content/uploads/2014/12/blockingdeadlocking1.png" alt="BlockingDeadlocking1" width="604" height="340" /></a>

<strong>5.</strong> Right click the Collection Set "Blocking and Deadlocking" and select "Add". Now enter the information for the first collection item (Blocked Processes)

<a href="/wp-content/uploads/2014/12/blockingdeadlocking2.png"><img class="alignnone size-full wp-image-857" src="/wp-content/uploads/2014/12/blockingdeadlocking2.png" alt="BlockingDeadlocking2" width="604" height="340" /></a>

<strong>6.</strong> Click the "Parameters" button and fill the dialog with the information requested. The most important part of this step is providing a definition for the Extended Events session that captures blocked processes. This is the session I am using:



```sql
CREATE EVENT SESSION [blocked_processes] ON SERVER ADD EVENT sqlserver.blocked_process_report
WITH (
	MAX_MEMORY = 2048 KB
	,EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS
	,MAX_DISPATCH_LATENCY = 30 SECONDS
	,MAX_EVENT_SIZE = 0 KB
	,MEMORY_PARTITION_MODE = NONE
	,TRACK_CAUSALITY = OFF
	,STARTUP_STATE = ON
)
```



You also have to enter values for the output table (the name of the table that will hold the data in the MDW database), an optional filter to futher limiting the rows you want to save to the database and the comma separated list of the event session fields you want to add to the destination table. In this case, the filter is "duration &lt;= 40000000&quot; to capture the &quot;blocked_process&quot; event just once, because a new event will be fired each time the configuration option &quot;blocked_process_threshold&quot; and its multiples are exceeded.

<a href="/wp-content/uploads/2014/12/blockingdeadlocking3.png"><img class="alignnone size-full wp-image-858" src="/wp-content/uploads/2014/12/blockingdeadlocking3.png" alt="BlockingDeadlocking3" width="604" height="463" /></a>

<strong>7.</strong> Now click the "Alerting" tab and enter the information needed to fire an email every time an event is captured. Extended T-SQL Collector uses Database Mail, so make sure you have a profile that you can use for this purpose. Now hit OK to close this dialog and hit "Save" in the main window.

<a href="/wp-content/uploads/2014/12/blockingdeadlocking4.png"><img class="alignnone size-full wp-image-859" src="/wp-content/uploads/2014/12/blockingdeadlocking4.png" alt="BlockingDeadlocking4" width="604" height="463" /></a>

<strong>8.</strong> Now you need a collection item to collect deadlocks. Right click the collection set on the tree on the left and click "Add". Now fill the information as you did for the collection item for blocked processes and hit "Save"

<a href="/wp-content/uploads/2014/12/blockingdeadlocking5.png"><img class="alignnone size-full wp-image-860" src="/wp-content/uploads/2014/12/blockingdeadlocking5.png" alt="BlockingDeadlocking5" width="604" height="340" /></a>

<strong>9.</strong> Hit "Parameters" and provide all the information needed for the collection item. Again, you need a session definition:



```sql
CREATE EVENT SESSION [deadlocks] ON SERVER
ADD EVENT sqlserver.xml_deadlock_report
WITH (
	MAX_MEMORY = 2048 KB
	,EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS
	,MAX_DISPATCH_LATENCY = 30 SECONDS
	,MAX_EVENT_SIZE = 0 KB
	,MEMORY_PARTITION_MODE = NONE
	,TRACK_CAUSALITY = OFF
	,STARTUP_STATE = ON
)
```



Enter information for  Output Table and Columns list as well.

<a href="/wp-content/uploads/2014/12/blockingdeadlocking6.png"><img class="alignnone size-full wp-image-861" src="/wp-content/uploads/2014/12/blockingdeadlocking6.png" alt="BlockingDeadlocking6" width="604" height="463" /></a>

&nbsp;

<strong>10.</strong> Click the "Alerting" tab and fill the information for the email setup.

<a href="/wp-content/uploads/2014/12/blockingdeadlocking7.png"><img class="alignnone size-full wp-image-862" src="/wp-content/uploads/2014/12/blockingdeadlocking7.png" alt="BlockingDeadlocking7" width="604" height="463" /></a>

<strong>11.</strong> Now just hit OK to close the dialog and save in the main window.

<strong>12.</strong> Hit "Start" in the collection set window to start the collection set.

<H3><B>Creating the collection set with a script</B></H3>

Too complicated? Don't worry, you can permform the same exact process using a script:



```sql
-- Enable editing advanced configuration options
EXEC sp_configure 'advanced', 1
RECONFIGURE
GO

-- Set the blocked process threshold
EXEC sp_configure 'blocked process threshold (s)', 20
RECONFIGURE
GO

BEGIN TRANSACTION
BEGIN TRY

DECLARE @collection_set_id_1 int
DECLARE @collection_set_uid_2 uniqueidentifier
EXEC [msdb].[dbo].[sp_syscollector_create_collection_set]
    @name=N'Blocking and Deadlocking',
    @collection_mode=0,
    @description=N'Collects Blocked Process Reports and Deadlocks using Extended Events',
    @logging_level=1,
    @days_until_expiration=30,
    @schedule_name=N'CollectorSchedule_Every_5min',
    @collection_set_id=@collection_set_id_1 OUTPUT,
    @collection_set_uid= '19AE101D-B30F-4447-8233-1314AEF0A02F'

DECLARE @collector_type_uid_3 uniqueidentifier

SELECT @collector_type_uid_3 = collector_type_uid
FROM [msdb].[dbo].[syscollector_collector_types]
WHERE name = N'Extended XE Reader Collector Type';

DECLARE @collection_item_id_4 int
EXEC [msdb].[dbo].[sp_syscollector_create_collection_item]
    @name=N'Blocked Processes',
    @parameters=N'
<ns:ExtendedXEReaderCollector xmlns:ns="DataCollectorType">
    <Session>
        <Name>blocked_processes</Name>
        <OutputTable>blocked_processes</OutputTable>
        <Definition>
        CREATE EVENT SESSION [blocked_processes] ON SERVER ADD EVENT sqlserver.blocked_process_report
        WITH (
            MAX_MEMORY = 2048 KB
            ,EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS
            ,MAX_DISPATCH_LATENCY = 30 SECONDS
            ,MAX_EVENT_SIZE = 0 KB
            ,MEMORY_PARTITION_MODE = NONE
            ,TRACK_CAUSALITY = OFF
            ,STARTUP_STATE = ON
            )
        </Definition>
        <Filter>duration &lt;= 40000000</Filter>
        <ColumnsList>blocked_process</ColumnsList>
    </Session>
    <Alert Enabled="true" WriteToERRORLOG="false" WriteToWindowsLog="false">
        <Sender>MailProfile</Sender>
        <Recipient>dba@localhost.localdomain</Recipient>
        <Subject>Blocked process detected</Subject>
        <Importance>High</Importance>
        <ColumnsList>blocked_process</ColumnsList>
        <Filter>duration &lt;= 40000000</Filter>
        <Mode>Atomic</Mode>
        <Delay>60</Delay>
    </Alert>
</ns:ExtendedXEReaderCollector>',
    @collection_item_id=@collection_item_id_4 OUTPUT,
    @frequency=60,
    @collection_set_id=@collection_set_id_1,
    @collector_type_uid=@collector_type_uid_3

Declare @collection_item_id_6 int
EXEC [msdb].[dbo].[sp_syscollector_create_collection_item] @name=N'Collect deadlocks', @parameters=N'
<ns:ExtendedXEReaderCollector xmlns:ns="DataCollectorType">
    <Session>
        <Name>deadlocks</Name>
        <OutputTable>deadlocks</OutputTable>
        <Definition>
        CREATE EVENT SESSION [deadlocks] ON SERVER
        ADD EVENT sqlserver.xml_deadlock_report
        WITH (
            MAX_MEMORY = 2048 KB
            ,EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS
            ,MAX_DISPATCH_LATENCY = 30 SECONDS
            ,MAX_EVENT_SIZE = 0 KB
            ,MEMORY_PARTITION_MODE = NONE
            ,TRACK_CAUSALITY = OFF
            ,STARTUP_STATE = ON
            )
        </Definition>
        <ColumnsList>xml_report</ColumnsList>
    </Session>
    <Alert Enabled="true" WriteToERRORLOG="false" WriteToWindowsLog="false">
        <Sender>MailProfile</Sender>
        <Recipient>dba@localhost.localdomain</Recipient>
        <Subject>Deadlock detected</Subject>
        <Importance>High</Importance>
        <ColumnsList>xml_report</ColumnsList>
        <Mode>Atomic</Mode>
        <Delay>60</Delay>
    </Alert>
</ns:ExtendedXEReaderCollector>',
    @collection_item_id=@collection_item_id_6 OUTPUT,
    @frequency=60,
    @collection_set_id=@collection_set_id_1,
    @collector_type_uid=@collector_type_uid_3

COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    DECLARE @ErrorMessage NVARCHAR(4000);
    DECLARE @ErrorSeverity INT;
    DECLARE @ErrorState INT;
    DECLARE @ErrorNumber INT;
    DECLARE @ErrorLine INT;
    DECLARE @ErrorProcedure NVARCHAR(200);
    SELECT @ErrorLine = ERROR_LINE(),
           @ErrorSeverity = ERROR_SEVERITY(),
           @ErrorState = ERROR_STATE(),
           @ErrorNumber = ERROR_NUMBER(),
           @ErrorMessage = ERROR_MESSAGE(),
           @ErrorProcedure = ISNULL(ERROR_PROCEDURE(), '-');
    RAISERROR (14684, @ErrorSeverity, 1 , @ErrorNumber, @ErrorSeverity, @ErrorState, @ErrorProcedure, @ErrorLine, @ErrorMessage);

END CATCH;

GO
```



<H3>Getting Alerts</H3>

Now that your session is running, you can be notified via email whenever blocking or deadlocking occurs.

This is a sample of the email you will receive, containing the colums you selected in the setup.

<a href="/wp-content/uploads/2014/12/deadlockemail.png"><img class="alignnone size-full wp-image-864" src="/wp-content/uploads/2014/12/deadlockemail.png" alt="deadlockemail" width="604" height="517" /></a>

You can also use the Collectionset Manager UI to query the information captured from the MDW database. You just need to right click a collection item and select "Query" from the context menu. Select a table from the dropdown  and adjust the date/time range with the sliders:

<a href="/wp-content/uploads/2014/12/deadlock_query.png"><img class="alignnone size-full wp-image-865" src="/wp-content/uploads/2014/12/deadlock_query.png" alt="deadlock_query" width="604" height="540" /></a>

<H3>Bottom line</H3>

Extended T-SQL Collector makes monitoring and alerting easy. It uses Extended Events to capture information from your server and alert you when problematic events arise.

Go download your copy! What are you waiting for?
