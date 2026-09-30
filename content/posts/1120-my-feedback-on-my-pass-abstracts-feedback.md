---
title: "My Feedback on my PASS Abstracts Feedback"
date: "2016-06-30T23:03:32"
slug: "my-feedback-on-my-pass-abstracts-feedback"
source_url: "http://spaghettidba.com/2016/06/30/my-feedback-on-my-pass-abstracts-feedback/"
url: "/2016/06/30/my-feedback-on-my-pass-abstracts-feedback/"
categories: ["SQL Server"]
tags: ["PASS", "SQLServer", "Summit"]
---

Brent Ozar recently <a href="https://ozar.me/2016/06/feedback-on-my-sqlpass-summit16-abstract-submissions/">published the feedback he got on his abstract submissions for PASS Summit 2016</a> and, as he often does, started a trend which some others followed. I think the feedback is interesting and useful for speakers that plan to improve their own submissions for the years to come, so I decided I will publish my feedback as well.

I did not get selected and, obviously, I would be happier if I got selected instead. This doesn’t mean I have problems with the selection process or the reviewers that implemented it. Instead I’m grateful for the enormous amount of work they did for the community, so a huge thank you goes to the committee.

Every year I see people publicly complain about the selection process or getting mad about being rejected. Folks, get over it: organizers have the right to choose whichever sessions they find more suitable for the Summit. It’s their responsibility to put together the best possible agenda and that doesn’t necessarily include your session.

That said, this is my feedback:
<h1>Responding to Extended Events in near real-time</h1>
<h3><em>Not Accepted: Higher rated session selected.</em></h3>
<strong>Category:</strong> General Session (75 minutes)

<strong>Track:</strong> Enterprise Database Administration &amp; Deployment

<strong>Topic:</strong> Performance Monitoring / Tuning / Extended Events / Waits

<strong>Level:</strong> 300

<strong>Abstract:</strong> Extended Events provide deep insight into SQL Server's behavior and allow us to gather information not available by other means. However, compared to other technologies such as SQL Trace and Event Notifications, a way to react to the events as soon as they happen seems to be lacking.
In this session we will see how the Extended Events streaming API can be used to process events in a near real-time fashion. We will demonstrate how this technology enables new possibilities to solve real world problems, such as capturing and notifying deadlocks or blocking sessions.

<strong>Prerequisites:</strong> Extended Events basics, C# basics, Powershell basics. The amount of coding required is in line with the average DBA skills.

<strong>Goal1</strong>:  Introduce Extended Events and compare them with other monitoring technologies available in SQL Server

<strong>Goal2</strong>:  Introduce the Extended Events streaming API and demonstrate how it can be used to process the events as soon as they occur, without shredding XML.

<strong>Goal3</strong>:  Demonstrate how the Extended Events streaming API can be used to solve real world problems, such as building a monitoring and alerting solution for deadlocks and blocked sessions.
<h3>Comments:</h3>
Needs more specifics in abstract.

A : 4 The abstract digs a little deeper on what's being offered by XEs, and what needs to be done to efficiently capture events in near real-time without bogging down the system

T : 5 The topic matches with the goals - and many people hesitate capturing large amounts of .xel files fearing shredding the xml. This session offers a new approach to capturing the same using streaming APIs, with C#/PowerShell

S : 5 Prereqs are a little steep, but given the outcome - justified, and will interest people.

Level looks ok for the prereqs and goals. Topic is ok. Abstract is good overall. Only issue is the second sentence reads a little oddly.

Abstract: Well written abstract with strong supportive goals. Topic: Great topic!            Subjective: This sounds like a very interesting session. Taking xEvents to the next level. I would attend this session. I think it will be a large draw!
<h3>Feedback on comments:</h3>
“Needs more specifics in abstract”. What kind of specifics is needed in the abstract? A clue would be helpful here.

A/T/S: what do these letters stand for? I suppose they mean Abstract, Topic, Subjective. What do the numbers stand for? A mark maybe? Again, no explanation.

“The second sentence reads a little oddly”. I really don’t understand grammar or language comments. It’s not a conference on the English language and non-native speakers are already disadvantaged enough without being constantly reminded that their language skills can’t compare to Shakespeare’s. Speakers names are stripped away from the sessions, so the reviewers may not be aware that the session comes from a foreigner. If the topic is good and fits what the organizers are looking for, minor grammar/language mistakes can be fixed. BTW, one of the reviewers told me that when multiple sessions are on a tie, language is the tie breaker. Questionable, but understandable.

The feedback itself is not very useful for improving this submission for next year.
<h1>SQL Server Infernals: Worst Practices in Action</h1>
<h3><em>Not Accepted: Other sessions selected based on building a balanced program for track coverage, speaker coverage, topic coverage, and session rating.</em></h3>
<strong>Category:</strong> General Session (75 minutes)

<strong>Track:</strong> Enterprise Database Administration &amp; Deployment

<strong>Topic:</strong> Internals: Storage Engine / Query Engine / Compression

<strong>Level:</strong> 100

<strong>Abstract:</strong> Let’s face it: Best Practices are too many to really know them all and choose which ones should be applied first. Does your telephone ring all the time? Do your users ask for that “quick report” that instead takes ages and keeps changing every time you think it’s done?
Have you ever thought that in dire times avoiding Worst Practices could be a good starting point and you can leave fine tuning for a better future? If the answer is “yes”, then this session is for you: we will discover together how not to torture a SQL Server instance and we will see how to avoid making choices that in the long run could turn out to be not as smart as they looked initially.

<strong>Prerequisites:</strong> Basic database design skills, basic development concepts, basic database administration skills.

<strong>Goal1</strong>: Demonstrate how bad Database Design decisions (irresponsible denormalization, EAV, bad data types, wrong or missing primary keys) can haunt a project through its whole lifetime.

<strong>Goal2</strong>: Illustrate how bad development practices (SQL Injection, RBAR, poor or no testing) can hurt performance, put security at risk and pose serious threats to the success of our projects.

<strong>Goal3</strong>: Enumerate and explain the worst installation and administration practices for SQL Server instances, offering the correct alternatives. Topics covered: HW choice, OS policies, security, ongoing administration, monitoring and tuning.
<h3>Comments:</h3>
Abstract: compelling

Topic: I like goals

Subjective rating: interesting, but level too low

Abstract: The outline and details of this abstract are well written

Topic: This is a great topic

Subjective: I may attend this session

The outline does not seem to clearly describe the contents of the presentation. The level of detail seems low - more detail might help attendees decide on value of attending. The title may not attract the appropriate attendees - it seems a little vague.

Abstract: Abstract is a little muddled. Goals are clearly laid out. Goals seem to contain the entire gamut of SQL Server. Perhaps a more focused area of SQL Server would help.

Topic: Title is cute.

Subjective: Could be a fun session.
<h3>Feedback on comments:</h3>
“Level too low”. Level is intentionally low: it’s meant as an introductory session. What to avoid is exactly that: an introductory topic for beginners. Have you ever noticed that basic introductory sessions pack the room? Should we take it as a clue that attendees want 100-level sessions? Apparently not.

“The outline does not seem to clearly describe the contents”. True, I agree. Next time I submit this session I will include in the abstract more details about the contents. It seems that including those details in the goals is not enough.

“Goals seem to contain the entire gamut of SQL Server”. True. I don’t see how this is a bad thing for an introductory session.

This feedback is much more useful than the other ones.
<h1>The shape of your Workload: Benchmarking and Baselining</h1>
<h3><em>Not Accepted: Higher rated session selected.</em></h3>
<strong>Category:</strong> General Session (75 minutes)

<strong>Track:</strong> Enterprise Database Administration &amp; Deployment

<strong>Topic:</strong> Performance Monitoring / Tuning / Extended Events / Waits

<strong>Level:</strong> 300

<strong>Abstract:</strong> The key to optimizing SQL Server performance is to establish a performance baseline and thoroughly analyze the workload on the server. Collecting a baseline is not enough: it is important to analyze the workload in order to intervene effectively exactly where performance issues lie.
In this session we will describe the techniques and tools to analyze SQL Server performance and we will introduce benchmarking techniques that allow us to rate our tuning efforts. We will also introduce some tools included in SQL Server 2014, such as the Distributed Replay, and several third-party applications that come at little or no cost, but provide the highest benefit.

<strong>Prerequisites:</strong> Basic SQL Server performance tuning techniques (DMVs, Performance Counters), basic monitoring techniques (SQL Trace, Extended Events).

<strong>Goal1</strong>: Introduce SQL Server performance analysis tools (DMVs, Performance Counters, Data Collector) and demonstrate how to use them to collect a baseline.

<strong>Goal2</strong>: Introduce workload analysis techniques, using SQL Server and third party tools, including cache analysis queries, RML Utilities and ClearTrace.

<strong>Goal3</strong>: Demonstrate benchmarking techniques which will allow us to compare performance before and after applying tuning measures, using RML utilities, Distributed Replay and Qure Analyzer.
<h3>Comments:</h3>
Needs more specifics in abstract.

A : 5 The abstract clearly spells out the need for baseling, and benchmarking, to identify performance workload.

T : 5 The topic maps well with the session goals - and makes use of the Dist Replay Controller/Client to replay the prod workload on lower environments, and making use of RML utils and ClearTrace

S : 5 The prereqs are not steep, and the session offers a lot to replay prod workload on lower envs.

Topic is a good and relevant choice that appeals to a distinct attendee pool. Level appears good for the prereqs and goals.

Abstract is ok. Some word choices make the sentences difficult to follow (ie. 'intervene effectively exactly').

Abstract: Well written abstract with strong, supportive goals. Enough information is provided from which an attendee can make an informed decision on whether or not to attend this session.

Topic: Excellent topic. Likely a 200 level session, not 300.

Subjective: Great session which should draw in attendees. This is a skill every database professional needs.
<h3>Feedback on comments:</h3>
“Needs more specifics in abstract” and “enough information is provided” in the same feedback. Not very helpful.

“Some word choices make the sentences difficult to follow”. I’ve already said what I think about language comments.

Reading the comments, you would think it made the cut, but it didn’t. What can I say? Competition is tough: there are lots of great speakers with lots of great sessions.

“Likely a 200 level session, not 300”. I disagree: I’ve never seen anyone less than experienced fiddling with RML Utilities or distributed replay.
<h1>General feedback</h1>
The comments I received this time are less helpful than the ones I got last year on the same exact sessions. Yep: I submitted the same sessions last year and I got very useful comments that I used to improve my submissions this year. Unfortunately, it will be hard to improve next year.

The level discussion is completely subjective. I was under the impression that here in Europe we tend to rate sessions lower than Americans do, so a 200 session in Europe could easily be a 300 session in USA. Maybe my impression was wrong. However, it’s interesting to see how the session that I proposed with level 100 was deemed to be underrated and the one that I proposed with level 300 was deemed to be overrated. Levels are part of the session: the speaker chooses which level to go for and I would have a really hard time as a reviewer arguing against that decision without having seen the session.

Regarding the reason for rejection, I am not completely sure it can be helpful for improving next year’s submissions. For instance, my session on Extended Events got “<em>Higher rated session selected</em>” as the reason for rejection, but looking at the schedule there is no other session on Extended Events (which is quite surprising) and no other session on monitoring (which is even more surprising and maybe a bit disappointing). This means that the higher rated session does not have to be on the same topic, which makes the other reason for rejection (<em>Other sessions selected based on building a balanced program for track coverage, speaker coverage, topic coverage, and session rating) </em>difficult to decipher.
<h1>Lessons learned</h1>
<ol>
 	<li><strong>You’re selling the abstract, not the session
</strong>The reviewers are evaluating your abstract, not your session. All your efforts should be pushed towards perfecting your abstract. Craft it as your masterpiece. Start well in advance, don’t wait for the last minute.</li>
 	<li><strong>Take as many shots as you can
</strong>Looking at the selection process from the outside it’s really hard to tell how it works, so submitting multiple abstracts can increase your chances of scoring a session. Maybe that session that you don’t like is exactly what the committee is looking for. Again, you’re selling only the abstract and if you get selected you have several months to improve the session.</li>
 	<li><strong>There’s a review service offered by PASS. Use it.
</strong>There is no guarantee that it is going to be the best feedback you will get, but it’s some feedback at least.</li>
 	<li><strong>You have friends in your #sqlfamily:</strong> <strong>ask for advice</strong>.
If you don’t trust the feedback that you get from the PASS review service, trust your friends. If you’re submitting for PASS Summit, chances are that you already have spoken at SQLSaturdays or other community events (if not, maybe you should think twice before submitting: PASS Summit is not for inexperienced speakers). In this case, you got in touch with the community leaders in your chapter, who probably keep scoring sessions at Summit year after year: ask them to review your sessions. I am sure that they will have precious suggestions for you.</li>
 	<li><strong>If you’re not an English native speaker, ask a native speaker to proofread it
</strong>Sure, your English is great. Sure, the reviewers have something to say about native speakers’ English as well. Sure, language should not be the focus of the reviewers. However, see lesson learned #1.</li>
 	<li><strong>Speaker/Abstract separation is a joke
</strong>If you read <a href="https://ozar.me/2016/06/feedback-on-my-sqlpass-summit16-abstract-submissions/">Brent’s feedback</a>, one thing emerges quite clearly: in many cases, the reviewers know exactly whose abstract they are reviewing. This might be because they already have seen the session somewhere else or because the abstract contains some “distinctive features” (sp_AskXXX anyone?). This means that some speakers have an advantage over the average Joe, but rightly so: those speakers are awesome and well known for being awesome. I’m not saying that the “Top Guns” can submit their grocery list: what I’m saying is that they are not selling only their abstracts. Now that Brent has published his abstracts, I wonder what would happen next year if somebody submitted one of his sessions… :-)</li>
</ol>
<h1>Bottom line</h1>
Being selected for speaking at the PASS Summit is damn hard. I hope that sharing my feedback will help you improving your submission next year. I also hope that you will find my advice useful, if you dare accepting advice from somebody who never managed to score a session himself.
