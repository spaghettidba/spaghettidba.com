---
title: "Concatenating multiple columns across rows"
date: "2011-10-13T17:22:23"
slug: "concatenating-multiple-columns-across-rows"
source_url: "http://spaghettidba.com/2011/10/13/concatenating-multiple-columns-across-rows/"
url: "/2011/10/13/concatenating-multiple-columns-across-rows/"
categories: ["SQL Server", "SQL Server Central", "T-SQL"]
tags: ["FOR XML", "PIVOT", "SQL", "String concatenation", "UNPIVOT"]
---

Today I ran into an interesting question on the forums at SQLServerCentral and I decided to share the solution I provided, because it was fun to code and, hopefully, useful for some of you.

Many experienced T-SQL coders make use of FOR XML PATH(‘’) to build concatenated strings from multiple rows. It’s a nice technique and pretty simple to use.
For instance, if you want to create a list of databases in a single concatenated string, you can run this statement:



```sql
SELECT CAST((
    SELECT name + ',' AS [text()]
    FROM sys.databases
    ORDER BY name
    FOR XML PATH('')
) AS varchar(max))
```



The SELECT statement produces this result:



```text
allDBs
------------------------------------------------------------------
BROKEN,LightHouse,master,model,msdb,tempdb,TEST,test80,TOOLS,WORK,
```




Great! But, what if you had to concatenate multiple columns at the same time? It’s an unusual requirement, but not an impossible one.
Let’s consider this example:



```sql
-- =================================
-- Create a sentences table
-- =================================
DECLARE @Sentences TABLE (
    sentence_id int PRIMARY KEY CLUSTERED,
    sentence_description varchar(50)
)

-- =================================
-- Sentences are broken into rows
-- =================================
DECLARE @Rows TABLE (
    sentence_id int,
    row_id      int,
    Latin       varchar(500),
    English     varchar(500),
    Italian     varchar(500)
)

-- =================================
-- Create three sentences
-- =================================
INSERT INTO @Sentences VALUES(1,'First sentence.')
INSERT INTO @Sentences VALUES(2,'Second Sentence')
INSERT INTO @Sentences VALUES(3,'Third sentence')

-- =================================
-- Create sentences rows from 
-- "De Finibus bonorum et malorum" 
-- by Cicero, AKA "Lorem Ipsum"
-- =================================
INSERT INTO @Rows VALUES(1, 1, 
    'Neque porro quisquam est,',
    'Nor again is there anyone who',
    'Viceversa non vi è nessuno che ama,')
INSERT INTO @Rows VALUES(1, 2, 
    'qui dolorem ipsum quia dolor sit amet,',
    'loves or pursues or desires to obtain pain',
    'insegue, vuol raggiungere il dolore in sé')
INSERT INTO @Rows VALUES(1, 3, 
    'consectetur, adipisci velit, sed quia non numquam',
    'of itself, because it is pain, but because occasionally',
    'perché è dolore ma perché talvolta')
INSERT INTO @Rows VALUES(1, 3, 
    'eius modi tempora incidunt',
    'circumstances occur in which',
    'capitano circostanze tali per cui')
INSERT INTO @Rows VALUES(1, 3, 
    'ut labore et dolore magnam aliquam quaerat voluptatem.',
    'toil and pain can procure him some great pleasure.',
    'con il travaglio e il dolore si cerca qualche grande piacere.') 
INSERT INTO @Rows VALUES(2, 1, 
    'Ut enim ad minima veniam,',
    'To take a trivial example,',
    'Per venire a casi di minima importanza,')
INSERT INTO @Rows VALUES(2, 2, 
    'quis nostrum exercitationem ullam corporis suscipit laboriosam,',
    'which of us ever undertakes laborious physical exercise,',
    'chi di noi intraprende un esercizio fisico faticoso')
INSERT INTO @Rows VALUES(2, 3, 
    'nisi ut aliquid ex ea commodi consequatur?',
    'except to obtain some advantage from it?',
    'se non per ottenere da esso qualche vantaggio?') 
INSERT INTO @Rows VALUES(3, 1, 
    'Quis autem vel eum iure reprehenderit qui in ea voluptate',
    'But who has any right to find fault with a man who chooses to enjoy a pleasure',
    'O chi può biasimare colui che decide di provare un piacere')
INSERT INTO @Rows VALUES(3, 2, 
    'velit esse quam nihil molestiae consequatur,',
    'that has no annoying consequences,',
    'che non porta conseguenze negative,')
INSERT INTO @Rows VALUES(3, 3, 
    'vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?',
    'or one who avoids a pain that produces no resultant pleasure?',
    'o che fugge quel dolore che non produce nessun piacere?')
```



The setup code creates two tables: Sentences and Rows. The first one is the master table, that contains the sentence_id and a description. The second one contains the actual sentences, broken into rows and organized with languages in columns.

For the purposes of this test, I inserted in the Rows table an excerpt of Cicero’s “<em>De Finibus bonorum et malorum</em>”, also known as “<em>Lorem Ipsum</em>”, the printing and typesetting industry’s standard <a href="http://www.lipsum.com/">dummy text</a> since the 1500s. 

Here’s how the input data looks like:

<a href="/wp-content/uploads/2011/10/loremipsum.png"><img src="/wp-content/uploads/2011/10/loremipsum.png" alt="" title="LoremIpsum" width="588" height="696" class="alignnone size-full wp-image-356" /></a>


What we want to do is concatenate all the rows for each sentence, keeping the languages separated. It could be accomplished very easily concatenating each column separately in a subquery, but what if the input data comes from a rather expensive query? You don't want to run the statement for each language, do you?

Let’s see how this can be done in a single scan:



```sql
SELECT sentence_id, sentence_description, Latin, English, Italian
FROM (
    SELECT Sentences.sentence_id, sentence_description, language_name, string 
    FROM   @Sentences AS Sentences
    OUTER APPLY (
        SELECT *
        FROM (
			-- =================================
			-- Create a Languages inline query
			-- =================================
                      SELECT 'Latin'
            UNION ALL SELECT 'English'
            UNION ALL SELECT 'Italian'
        ) Languages (language_name)
        CROSS APPLY (
			-- =================================
			-- Concatenate all the rows for 
			-- the current sentence and language
			-- from an UNPIVOTed version of the
			-- original rows table
			-- =================================
            SELECT sentence_id, string = (
                SELECT string + ' ' AS [data()] 
                FROM @Rows AS src
                UNPIVOT ( string FOR language_name IN (Latin, English, Italian) ) AS u
                WHERE sentence_id = Sentences.sentence_id
                    AND language_name = Languages.language_name
                ORDER BY row_id
                FOR XML PATH('')
            )
        ) AS ca
    ) AS oa
) AS src
-- =================================
-- Re-transform rows to columns
-- =================================
PIVOT ( MIN(string) FOR language_name IN ([Latin],[English],[Italian])) AS p
```




If you don’t like PIVOT and UNPIVOT, you can always use CASE expressions to create a crosstab.
Here’s the final result:

<a href="/wp-content/uploads/2011/10/loremipsum2.png"><img src="/wp-content/uploads/2011/10/loremipsum2.png" alt="" title="LoremIpsum2" width="604" height="426" class="alignnone size-full wp-image-357" /></a>

With a little of PIVOT, UNPIVOT and FOR XML you can achieve really surprising results, you just need to unleash your creativity.

<div class="archived-comments-container">
<details class="archived-comments"><summary>Archived WordPress comments (2)</summary><p class="archived-comments-note">Historical comments from the original site; this archive is read-only.</p><ol class="archived-comments-list"><li id="wordpress-comment-943" class="archived-comment"><article><header><strong>lukaseder</strong> <time datetime="2011-10-19T18:36:28Z">October 19, 2011 at 19:36</time></header><section class="archived-comment-content">That really is creative. Very nicely explained!<br>I wonder though, if someone reading this SQL statement will easily understand what's going on... :-)</section></article></li><li id="wordpress-comment-944" class="archived-comment"><article><header><strong>spaghettidba</strong> <time datetime="2011-10-19T21:41:45Z">October 19, 2011 at 22:41</time></header><section class="archived-comment-content">Thanks. On readability... well,that's what comments and formatting are for. :-)</section></article></li></ol></details>
</div>
