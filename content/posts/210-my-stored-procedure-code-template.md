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
