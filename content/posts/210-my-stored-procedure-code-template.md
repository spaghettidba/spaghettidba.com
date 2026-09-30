---
title: "My stored procedure code template"
date: "2011-07-08T16:51:46"
slug: "my-stored-procedure-code-template"
source_url: "http://spaghettidba.com/2011/07/08/my-stored-procedure-code-template/"
url: "/2011/07/08/my-stored-procedure-code-template/"
categories: ["SQL Server", "SQL Server Central", "T-SQL"]
tags: ["SSMS", "stored procedures", "template"]
---

Do you use code templates in SSMS? I am sure that at least once you happened to click "New stored procedure" in the object explorer context menu.

The default template for this action is a bit disappointing and the only valuable line is "SET NOCOUNT ON". The rest of the code has to be heavily rewritten or deleted. Even if you use the handy keyboard shortcut for "Specify values for template parameters"  (CTRL+SHIFT+M), you end up entering a lot of useless values. For instance, I find it very annoying having to enter stored procedure parameters definitions separately for name, type and default value.

Moreover, one of the questions I see asked over and over in the forums at <a href="www.sqlservercentral.com">SqlServerCentral </a>is how to handle transactions and errors in a stored procedure, something that the default template does not.

Long story short, I'm not very happy with the built-in template, so I decided to code my own:



```sql
-- =============================================
-- Author:      <Author,,Name>
-- Create date: <Create Date,,>
-- Description: <Description,,>
-- =============================================
CREATE PROCEDURE <ProcedureName, sysname, >
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT,
        QUOTED_IDENTIFIER,
        ANSI_NULLS,
        ANSI_PADDING,
        ANSI_WARNINGS,
        ARITHABORT,
        CONCAT_NULL_YIELDS_NULL ON;
    SET NUMERIC_ROUNDABORT OFF;

    DECLARE @localTran bit
    IF @@TRANCOUNT = 0
    BEGIN
        SET @localTran = 1
        BEGIN TRANSACTION LocalTran
    END

    BEGIN TRY

        --Insert code here

        IF @localTran = 1 AND XACT_STATE() = 1
            COMMIT TRAN LocalTran

    END TRY
    BEGIN CATCH

        DECLARE @ErrorMessage NVARCHAR(4000)
        DECLARE @ErrorSeverity INT
        DECLARE @ErrorState INT

        SELECT  @ErrorMessage = ERROR_MESSAGE(),
                @ErrorSeverity = ERROR_SEVERITY(),
                @ErrorState = ERROR_STATE()

        IF @localTran = 1 AND XACT_STATE() <> 0
            ROLLBACK TRAN

        RAISERROR ( @ErrorMessage, @ErrorSeverity, @ErrorState)

    END CATCH

END
```



This template can be saved in the default path and overwrite the kludgy "New Stored Procedure" built-in template.

Some things to keep in mind:
<ul>
	<li>I don't use nested transactions (they're totally pointless IMHO) and I check for an existing transaction instead.</li>
	<li>The stored procedure will commit/rollback the transaction only if it was started inside the procedure.</li>
	<li>I want every stored procedure to throw the errors it catches. If there's another calling procedure, it will take care of the errors in the same way.</li>
</ul>
<div>A couple of words on the template parameters:</div>
<div>
<ul>
	<li>This is your computer: you can safely replace &lt;Author, ,Name&gt; with your real name.</li>
	<li>It would really be nice if there was some kind of way to make SSMS fill &lt;Create Date, ,&gt; with the current date. Unfortunately there's no way. If you are using CVS or some other kind of version control system, this is a nice place for an RCS string such as $Date$</li>
	<li>If you like templates parameters and you heard bad news regarding this feature in the next version of SQL Server (codename Denali), don't worry: <a title="Connect" href="http://connect.microsoft.com/SQLServer/feedback/details/623863">MS fixed it</a>.</li>
</ul>
<div>EDIT: 2011-07-08 18:10 Mladen Prajdic (<a title="Blog" href="http://weblogs.sqlteam.com/mladenp/">blog</a>|<a title="Twitter" href="http://twitter.com/#!/MladenPrajdic">twitter</a>) just pointed out that it had no "SET XACT_ABORT ON" at the top. Fixed!</div>
</div>

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (9)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-12" class="archived-comment"><article><header><strong>robert matthew cook</strong> <time datetime="2011-07-08T18:39:35Z">July 8, 2011 at 19:39</time></header><section class="archived-comment-content">great script, thanks for posting it<br><br>in addition to the set options you have listed, i have used as a template the ones for indexed views<br><br>SET QUOTED_IDENTIFIER, ANSI_NULLS, ANSI_PADDING, ANSI_WARNINGS, ARITHABORT, CONCAT_NULL_YIELDS_NULL ON;<br>SET NUMERIC_ROUNDABORT OFF;<br><br>http://msdn.microsoft.com/en-us/library/ms175088.aspx</section></article></li><li id="wordpress-comment-13" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2011-07-09T20:38:11Z">July 9, 2011 at 21:38</time></header><section class="archived-comment-content">Thank you, Robert! I'll edit the template to incorporate your valuable suggestions.<br>2011-07-11 14.19 Done!</section></article></li><li id="wordpress-comment-1306" class="archived-comment"><article><header><strong>jack</strong> <time datetime="2012-09-21T21:13:33Z">September 21, 2012 at 22:13</time></header><section class="archived-comment-content">you don't need to use @@trancount at all - xact_state() has everything you need<br>plus on entry you need to check if (xact_state() &lt; 0) raiserror('uncommitable tran found', 16, 1) and you need to output the error message using raiserror(@msg, 0, 1) to make sure all the errors caught by every catch block in the stack shows up - world of pain otherwise<br>and your throw code needs some work - google it</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-1307" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2012-09-22T15:18:27Z">September 22, 2012 at 16:18</time></header><section class="archived-comment-content">Thanks for your input, Jack.<br>You're right - what @@trancount does is completely covered by XACT_STATE(), you can use any of those. <br>Early detection of doomed transactions is a good suggestion. They would be caught anyway by the CATCH block, but I agree that checking for XACT_STATE on entry would save some work.<br>Raising errors with severity 0 isn't any different from using PRINT and doesn't cause falling into the catch block of the calling procedure, I don't see how that coud help. Maybe I'm missing something, if you have a link to your blog or to someone else's code to clrify this suggestion, I'm interested in taking a look.<br>On this particular subject, please consider that some (older) libraries such as ADO are unable to handle more than one error message and raising multiple errors would make the app ignore any transformation on the message you can do at higher levels in the call stack.<br>I don't uderstand exactly what kind of work would this throw code require, other than updating to SQL2012's throw command. Again, suggestions and references are welcome on this subject.<br>Cheers</section></article></li></ol></li><li id="wordpress-comment-7837" class="archived-comment"><article><header><strong>knightwisp</strong> <time datetime="2015-05-20T09:01:35Z">May 20, 2015 at 10:01</time></header><section class="archived-comment-content">Nice template.The problem with TRY..CATCH I'm having is that there can occur an UNCOMMITABLE STATE within the CATCH block which prevents write operations, including error logging, until the transaction is rolled back. That presents a problem from a nested procedure that didn't start the transaction and shouldn't roll it back. The issue with an example is presented in this SO question: http://stackoverflow.com/questions/30333429/uncommitable-transaction-prevents-error-logging-in-nested-transaction</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-7838" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2015-05-20T09:07:51Z">May 20, 2015 at 10:07</time></header><section class="archived-comment-content">The problem with the prodedure you posted on SO is that the error code and message are tested AFTER attempting the ROLLBACK. If you test the error message before attempting the rollback, the original message should be preserved. <br>As far as logging it, the only options you have with uncommittable transactions is the use of table variables or logging to ERRORLOG (it's a file, no transaction processing here).</section></article></li></ol></li><li id="wordpress-comment-10100" class="archived-comment"><article><header><strong>Adrian Sugden</strong> <time datetime="2016-12-16T13:55:22Z">December 16, 2016 at 14:55</time></header><section class="archived-comment-content">Great template. <br>Only comment I have is that it doesn't look possible to run any code outside of a local transaction (LocalTran).<br>Even if you set @localTran = 0 its still beginning LocalTran which means it has to be committed or rolled back.<br>I realise everything in SQL Server runs within an implicit transaction, but if you just wanted to run something say a SELECT do you care if it's in a transaction or not?</section></article><ol class="archived-comment-replies"><li id="wordpress-comment-10101" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2016-12-16T14:05:20Z">December 16, 2016 at 15:05</time></header><section class="archived-comment-content">Hi Adrian,<br><br>You don't need a transaction if all you're doing in the procedure is execute a SELECT statement. However, code tends to change over time and it's better to have the transaction thing sorted right from the start rather than having to remember that when the code needs to be changed and you introduce something that writes to a bunch of tables.<br>At least, this is how I see it.<br><br>Regarding setting @localTran to avoid starting the transaction, that's not what the code is supposed to do. A transaction is started if is hasn't already been started, that's it.<br><br>Hope this helps<br>Gianluca</section></article></li></ol></li><li id="wordpress-comment-43709" class="archived-comment"><article><header><strong>Ethan R</strong> <time datetime="2022-11-20T01:48:30Z">November 20, 2022 at 02:48</time></header><section class="archived-comment-content">Great reeading</section></article></li></ol></details>
</div>
