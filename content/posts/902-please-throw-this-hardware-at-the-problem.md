---
title: "Please Throw this Hardware at the Problem"
date: "2015-02-12T20:30:52"
slug: "please-throw-this-hardware-at-the-problem"
source_url: "http://spaghettidba.com/2015/02/12/please-throw-this-hardware-at-the-problem/"
url: "/2015/02/12/please-throw-this-hardware-at-the-problem/"
categories: ["SQL Server"]
tags: ["Performance Tuning", "RAM", "Tuning"]
---

<a href="/wp-content/uploads/2015/02/ram.png"><img class="aligncenter size-full wp-image-903" src="/wp-content/uploads/2015/02/ram.png" alt="ram" width="400" height="273" /></a>

We’re being told over and over that “throwing hardware at the problem” is not the correct solution for performance problems and a 2x faster server will not make our application twice as fast. Quite true, but there’s one thing that we can do very easily without emptying the piggy bank and won’t hurt for sure: buying more RAM.

The price for server-class RAM has dropped so dramatically that today you can buy a 16 GB module for around € 200. Depending on the architecture of your server, you could max out the memory supported by a standard edition (128 GB) with just € 1,600.

Isn’t it a reasonable price for better performance?

Let’s put it in perspective: you decide that throwing hardware at the problem is not right, so you hire a consultant to tune performance. How many days of his work can you buy with € 1,600? Two? One? How much tuning work will he do in one or two days? Do you want him to work on the core issues or fight with memory pressure? RAM is cheap, consultants are not: make them work on what really matters for you.

Does adding RAM always make sense? No: if your server has 4 GB of data and 16 GB of RAM, there’s no need to add more RAM and if you do you won’t see any improvement. On the other hand, if you have 100 GB of data and 32 GB of RAM, you should be upgrading right away. Isn’t your business worth € 1.600? You’re probably paying much more for SQL Server licensing, so why waste your money on a license that has to run on an underpowered machine? RAM is cheap, SQL Server licenses are not: let your license work on a good machine.

Will it make a huge difference? It depends: if the server is already under heavy memory pressure, you will see a big improvement. Even if memory pressure is not the worst issue on your server, you will see a big difference for those queries that access data not used frequently: if you don’t have enough RAM, that data will probably live outside the buffer cache and will have to be read from disk. RAM is cheap, faster disks are incredibly expensive: let the RAM work and the disks sit idle.

That said, what I see in the wild is lots and lots of production servers with 8 GB of RAM or less. Many of those servers have been installed a few years ago, when RAM was pricier than today, but there’s no reason why you shouldn’t upgrade them now. Upgrading the CPU has an impact on the SQL Server licensing, while adding more RAM doesn’t require additional licensing fees. See? RAM is cheap.

On the other hand, we have many servers running on virtual machines at hosting/cloud facilities, where you pay for machine specs. Something has to change here as well: hosting companies are offering too few RAM in their machines and the configurations with more memory are crazily expensive. Dear hosting/cloud companies, open your eyes: RAM is ridiculously cheap!

<strong><span style="text-decoration:underline;">Call to action:</span></strong>

Did I mention that RAM is cheap? Check your servers: are they running on less than € 200 of RAM? It’s time to upgrade <strong>NOW</strong>!
