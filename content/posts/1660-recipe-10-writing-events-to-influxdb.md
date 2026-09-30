---
title: "Recipe 10: Writing Events to InfluxDB"
date: "2022-03-04T14:00:00"
slug: "recipe-10-writing-events-to-influxdb"
source_url: "http://spaghettidba.com/2022/03/04/recipe-10-writing-events-to-influxdb/"
url: "/2022/03/04/recipe-10-writing-events-to-influxdb/"
categories: ["SQL Server"]
tags: ["XESmartTarget"]
---

<!-- wp:paragraph -->
<p>Welcome to the last recipe of this Extended Events cookbook! You will find the first blog post of the series <a href="https://spaghettidba.com/10-dba-recipes-with-xesmarttarget/">here</a> and you can browse all recipes with the <a href="https://spaghettidba.com/tag/xesmarttarget">xesmarttarget tag on this blog</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-problem">The problem</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>The TIG software stack (<a href="https://www.influxdata.com/time-series-platform/telegraf/">Telegraf</a>, <a href="https://www.influxdata.com/products/influxdb/">InfluxDB</a>, <a href="https://grafana.com/">Grafana</a>) is a very powerful combination of software tools that can help you collect, store and analyze data that has a time attribute. In particular, <a href="https://www.influxdata.com/products/influxdb/">InfluxDB </a>is a time series database, built with sharding, partitioning and retention policies in mind. It is absolutely fantastic for storing telemetry data, like performance counters from SQL Server or other software products.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In order to store data in InfluxDB, you can use <a href="https://www.influxdata.com/time-series-platform/telegraf/">Telegraf</a>, a data collection agent that takes care of extracting telemetry data from the object to observe and upload it to the InfluxDB database. Telegraf is built with the concept of plugins: each object to observe has its own plugin and it’s not surprising at all to find a <a href="https://github.com/influxdata/telegraf/tree/master/plugins/inputs/sqlserver">specialized plugin for SQL Server</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Using the SQL Server plugin, you can connect Telegraf to SQLServer, populate an InfluxDB database and visualize the performance metrics using <a href="https://grafana.com/">Grafana</a>. In fact, there are multiple <a href="https://grafana.com/grafana/dashboards/?pg=community&amp;search=sql+server">readily available dashboards designed for the data collected by the Telegraf plugin for SQL Server</a>. You can simply download and install those dashboards or build your custom dashboards to create a complete monitoring solution for SQL Server.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>However, Telegraf is designed to pull data from SQL Server at regular intervals and cannot receive events from Extended Events sessions. Fortunately, there is a way around this limitation, using XESmartTarget and the <a href="https://github.com/spaghettidba/XESmartTarget/wiki/TelegrafAppenderResponse">TelegrafAppenderResponse</a>.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This response type doesn’t work like the other ones: it connects to an Extended Events session and outputs the events it receives on STDOUT, using the <a href="https://docs.influxdata.com/influxdb/cloud/reference/syntax/line-protocol/">Line Protocol</a> format used by Telegraf. It is designed to be used in combination with Telegraf: it’s Telegraf itself that starts XESmartTarget and then listens to its STDOUT to produce the points to upload to InfluxDB.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>It sounds complicated, but it is not. Let me show you how it works with an example.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In this case, we are going to capture the following events to upload them to InfluxDB: errors, timeout, blocking and deadlocking. Let’s do this!</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="the-session">The session</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Of course, we need a session. It is going to contain all the four events that we need:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"sql"} -->
<pre class="wp-block-syntaxhighlighter-code">IF NOT EXISTS (SELECT * FROM sys.server_event_sessions WHERE name = 'Recipe10')

CREATE EVENT SESSION [Recipe10] ON SERVER 
    ADD EVENT sqlserver.blocked_process_report (
        ACTION(
            package0.event_sequence,
            sqlserver.client_app_name, 
            sqlserver.client_hostname, 
            sqlserver.database_name, 
            sqlserver.server_instance_name, 
            sqlserver.server_principal_name, 
            sqlserver.session_id, 
            sqlserver.sql_text
        )
    )
,ADD EVENT sqlserver.error_reported (
        ACTION(
            package0.event_sequence,
            sqlserver.client_app_name, 
            sqlserver.client_hostname, 
            sqlserver.database_name, 
            sqlserver.server_instance_name, 
            sqlserver.server_principal_name, 
            sqlserver.session_id
        ) 
        WHERE ([severity] &gt;= (16))
    )
,ADD EVENT sqlserver.rpc_completed (
        ACTION(
            package0.event_sequence,
            sqlserver.client_app_name, 
            sqlserver.client_hostname, 
            sqlserver.database_name, 
            sqlserver.query_hash, 
            sqlserver.server_instance_name, 
            sqlserver.server_principal_name, 
            sqlserver.session_id
        ) 
        WHERE ([result] = (2))
    )
,ADD EVENT sqlserver.sql_batch_completed (
        ACTION(
            package0.event_sequence,
            sqlserver.client_app_name, 
            sqlserver.client_hostname, 
            sqlserver.database_name, 
            sqlserver.query_hash, 
            sqlserver.server_instance_name, 
            sqlserver.server_principal_name, 
            sqlserver.session_id
        ) 
        WHERE ([result] = (2))
    )
,ADD EVENT sqlserver.xml_deadlock_report (
        ACTION(
            package0.event_sequence,
            sqlserver.client_app_name, 
            sqlserver.client_hostname, 
            sqlserver.database_name, 
            sqlserver.server_instance_name, 
            sqlserver.server_principal_name, 
            sqlserver.session_id
        )
);

IF NOT EXISTS (SELECT * FROM sys.dm_xe_sessions WHERE name = 'Recipe10')
    ALTER EVENT SESSION Recipe10 ON SERVER STATE = START;
GO
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Let’s have a look at the script.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The errors are captured by the error_reported event, with a filter for severe errors (severity &gt; 16).</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The blocked_process_report event takes care of blocking. To make it work, you will have to configure the blocked process threshold configuration option.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Xml_deadlock_report captures all the deadlocks.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The timeouts are captured by rpc_completed and sql_batch_completed events with filter for result = 2 (error). It’s not only timeouts, but a large chunk of these are timeouts.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="xesmarttarget">XESmartTarget</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Now that we have a session, we need to provide the configuration for XESmartTarget.</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"jscript"} -->
<pre class="wp-block-syntaxhighlighter-code">{
    "Target": {
        "ServerName": "$ServerName",
        "SessionName": "Recipe10",
        "FailOnProcessingError": false,
        "Responses": [
            {
                "__type": "TelegrafAppenderResponse",
                "Events": [
                    "error_reported"
                ],
                "OutputMeasurement": "sqlserver_events_errors",
                "OutputTags": [
                    "server_instance_name",
                    "name", 
                    "client_app_name", 
                    "server_principal_name", 
                    "client_hostname", 
                    "database_name",
                    "severity",
                    "error_number"
                ],
                "OutputFields": [
                    "event_sequence",
                    "message"
                ]
            },
            {
                "__type": "TelegrafAppenderResponse",
                "Events": [
                    "sql_batch_completed"
                ],
                "OutputMeasurement": "sqlserver_events_timeouts",
                "OutputTags": [
                    "server_instance_name",
                    "name", 
                    "client_app_name", 
                    "server_principal_name", 
                    "client_hostname", 
                    "database_name"
                ],
                "OutputFields": [
                    "event_sequence",
                    "sql_text AS batch_text",
                    "cpu_time",
                    "duration",
                    "logical_reads",
                    "physical_reads",
                    "writes",
                    "query_hash",
                    "row_count"
                ]
            },
            {
                "__type": "TelegrafAppenderResponse",
                "Events": [
                    "rpc_completed"
                ],
                "OutputMeasurement": "sqlserver_events_timeouts",
                "OutputTags": [
                    "server_instance_name",
                    "name", 
                    "client_app_name", 
                    "server_principal_name", 
                    "client_hostname", 
                    "database_name"
                ],
                "OutputFields": [
                    "event_sequence",
                    "sql_text AS statement",
                    "cpu_time",
                    "duration",
                    "logical_reads",
                    "physical_reads",
                    "writes",
                    "query_hash",
                    "row_count"
                ]
            },
            {
                "__type": "TelegrafAppenderResponse",
                "Events": [
                    "xml_deadlock_report"
                ],
                "OutputMeasurement": "sqlserver_events_deadlocks",
                "OutputTags": [
                    "server_instance_name",
                    "name", 
                    "client_app_name", 
                    "server_principal_name", 
                    "client_hostname", 
                    "database_name"
                ],
                "OutputFields": [
                    "event_sequence",
                    "session_id",
                    "xml_report"
                ]
            },
            {
                "__type": "TelegrafAppenderResponse",
                "Events": [
                    "blocked_process_report"
                ],
                "OutputMeasurement": "sqlserver_events_blocking",
                "OutputTags": [
                    "server_instance_name",
                    "name", 
                    "client_app_name", 
                    "server_principal_name", 
                    "client_hostname", 
                    "database_name"
                ],
                "OutputFields": [
                    "event_sequence",
                    "blocked_process",
                    "duration",
                    "index_id",
                    "lock_mode",
                    "object_id",
                    "resource_owner_type",
                    "transaction_id"
                ]
            }
        ]
    }
}
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>OutputMeasurement indicates the name of the measurement (that’s the equivalent of a table in InfluxDB). OutputTags and OutputFields indicate which “columns” will be added to the measurement. In InfluxDB you don’t have tables and you don’t have columns, but each point (that’s the equivalent of a row) has attributes of two types: tags (these are the key attributes, which are indexed) and fields (these are the value attributes, that contain the data).</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The combination of timestamp + tags must be unique: if you send a point with the same tag values and the same timestamp as an existing point in the measurement, the existing point gets overwritten.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>For instance, you could have a point with timestamp + tags (database name) and fields (data size, log size). Tags are indexed and are used to locate the points and aggregate them, while fields usually contain the numeric attributes that can be plotted on a chart or aggregated before visualizing.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>In this configuration, XESmartTarget is not started directly by you, but it is started by Telegraf, using the execd plugin. Telegraf itself needs its configuration file, which looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code -->
<pre class="wp-block-syntaxhighlighter-code"># Telegraf Configuration
#

# Configuration for telegraf agent
[agent]

  interval = "15s"
  round_interval = true

  metric_batch_size = 5000
  metric_buffer_limit = 15000

  collection_jitter = "0s"

  flush_interval = "10s"
  flush_jitter = "0s"

  ## By default or when set to "0s", precision will be set to the same timestamp order as the collection interval, with the maximum being 1s. (interval = "10s", precision = "1s")
  ## Valid time units are "ns", "us" (or "┬╡s"), "ms", "s".
  precision = "1s"

  ## Log
  debug = true
  quiet = false

  ##  empty string means to log to stderr.
  logfile = "C:\\temp\\telegraf_log.log"

  logfile_rotation_interval = "7d"
  logfile_rotation_max_size = "50MB"
  logfile_rotation_max_archives = 7

  ## Add tag "host" to every collected metric, the host is the machine on which telegraf runs
  ## Override default hostname, if empty use os.Hostname()
  hostname = ""
  ## If set to true, do no set the "host" tag in the telegraf agent.
  omit_hostname = false

[[inputs.execd]]
  command = [
    'powershell',
    '-File',
    'C:\temp\Recipe_10_telegraf_xesmarttarget.ps1',
    '-ServerName',
    'localhost\SQLEXPRESS'
  ]
  signal = "none"
  restart_delay = "2m"
  data_format = "influx"


  [[processors.strings]]
  
  namepass = ["sqlserver_events_*"]
    
    [[processors.strings.replace]]
    
    

    tag = "server_instance_name"
    old = "\\"
    new = ":"

# Configuration for sending metrics to InfluxDB
[[outputs.influxdb]]

  urls = ["https://localhost:8086"]

  # database = ""
  database_tag = "demo"
  exclude_database_tag = false

  skip_database_creation = true

  # retention_policy = ""
  # retention_policy_tag = ""
  # exclude_retention_policy_tag = false

  # write_consistency = "any"

  ## Timeout for HTTP messages.
  timeout = "5s"

  ## HTTP User-Agent
  # user_agent = "telegraf"

  ## HTTP Content-Encoding for write request body, can be set to "gzip" to
  ## compress body or "identity" to apply no encoding.
  content_encoding = "gzip"
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>Save this as c:\temp\telegraf.conf. As you can see from the telegraf configuration file, it has to start a powershell script that in turn takes care of running XESmartTarget. The script is super simple and it looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:syntaxhighlighter/code {"language":"powershell"} -->
<pre class="wp-block-syntaxhighlighter-code">[CmdletBinding()]
Param(
  [Parameter(Mandatory=$True,Position=0)] 
  [string]$ServerName
)

$params = $(
    "--File",
    "$PsScriptRoot\Recipe_10_Telegraf.json",
    "--NoLogo",
    "--Quiet",
    "--GlobalVariables",
    "ServerName=$ServerName"
)


&amp; "C:\Program Files\XESmartTarget\XESmartTarget.exe" $Params

exit 1
</pre>
<!-- /wp:syntaxhighlighter/code -->

<!-- wp:paragraph -->
<p>You can save it as C:\temp\Recipe_10_telegraf_xesmarttarget.ps1 and start Telegraf, using the configuration file provided.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The syntax for that is the following:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>Telegraf.exe --config c:\temp\telegraf.conf</code></pre>
<!-- /wp:code -->

<!-- wp:paragraph -->
<p>Telegraf will not show much on its console window, but under the hood it is starting XESmartTarget and it receives all the events in Line Protocol format from the TelegrafAppenderResponse.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>You can set up a dashboard to display all the data, like this one from <a href="https://qmonitor.quantumdatis.com/">QMonitor</a>, the monitoring solution built by <a href="https://quantumdatis.com/">Quantumdatis</a>. QMonitor is built on top of the TIG stack and uses multiple components, including XESmartTarget, to extract, upload and analyze SQL Server performance data.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>The events dashboard looks like this:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1664,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-34.png"><img src="/wp-content/uploads/2022/02/image-34.png" alt="" class="wp-image-1664" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>If you click one of the events, you can see the details of the event. In this case, the dashboard displays data about deadlocks:</p>
<!-- /wp:paragraph -->

<!-- wp:image {"id":1665,"sizeSlug":"large","linkDestination":"media"} -->
<figure class="wp-block-image size-large"><a href="/wp-content/uploads/2022/02/image-35.png"><img src="/wp-content/uploads/2022/02/image-35.png" alt="" class="wp-image-1665" /></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>All the data on this dashboard comes from the events captured by XESmartTarget and uploaded to InfluxDB by Telegraf.</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 id="recap">Recap</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Thanks to XESmartTarget it is extremely easy to capture events and process them with very little effort. You can perform a great variety of tasks with XEsmartTarget, from writing to a table in the database to the most complex tasks, like aggregating data in memory or sending emails.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>You can review all the posts in the series, browsing the <a href="https://spaghettidba.com/tag/xesmarttarget">XESmartTarget tag</a>. If you have questions on XESmartTarget don’t be shy and send me an email or comment here. Thanks for your attention!</p>
<!-- /wp:paragraph -->
