## What is scalability? - Describe performance - Coping with load
Even if a system is working reliably today, that doesn’t mean it will necessarily work reliably in the future. One common reason for degradation is increased load: perhaps the system has grown from 10,000 concurrent users to 100,000 concurrent users. scalability means considering questions like “If the system grows in a particular way, what are our options for coping with the growth?” and “How can we add computing resources to handle the additional load?”

### Describing Load
First, we need to succinctly describe the current load on the system; only then can we
discuss growth questions (what happens if our load doubles?). Load can be described
with a few numbers which we call load parameters. The best choice of parameters
depends on the architecture of your system: it may be requests per second to a web
server, the ratio of reads to writes in a database, the number of simultaneously active
users in a chat room, the hit rate on a cache, or something else. Perhaps the average
case is what matters for you, or perhaps your bottleneck is dominated by a small
number of extreme cases.

### Describing Performance
Once you have described the load on your system, you can investigate what happens
when the load increases. You can look at it in two ways:
• When you increase a load parameter and keep the system resources (CPU, memory, network bandwidth, etc.) unchanged, how is the performance of your system
affected?
• When you increase a load parameter, how much do you need to increase the
resources if you want to keep performance unchanged?
Both questions require performance numbers, so let’s look briefly at describing the
performance of a system.
In a batch processing system such as Hadoop, we usually care about throughput—the
number of records we can process per second, or the total time it takes to run a job
on a dataset of a certain size. In online systems, what’s usually more important is the
service’s response time—that is, the time between a client sending a request and
receiving a response.

### Approaches for Coping with Load
Now that we have discussed the parameters for describing load and metrics for measuring performance, we can start discussing scalability in earnest: how do we maintain
good performance even when our load parameters increase by some amount?
An architecture that is appropriate for one level of load is unlikely to cope with 10
times that load. If you are working on a fast-growing service, it is therefore likely that
you will need to rethink your architecture on every order of magnitude load increase
—or perhaps even more often than that.
People often talk of a dichotomy between scaling up (vertical scaling, moving to a
more powerful machine) and scaling out (horizontal scaling, distributing the load
across multiple smaller machines). Distributing load across multiple machines is also
known as a shared-nothing architecture. A system that can run on a single machine is
often simpler, but high-end machines can become very expensive, so very intensive
workloads often can’t avoid scaling out. In reality, good architectures usually involve
a pragmatic mixture of approaches: for example, using several fairly powerful
machines can still be simpler and cheaper than a large number of small virtual
machines.
Some systems are elastic, meaning that they can automatically add computing resources when they detect a load increase, whereas other systems are scaled manually (a
human analyzes the capacity and decides to add more machines to the system). An
elastic system can be useful if load is highly unpredictable, but manually scaled systems are simpler and may have fewer operational surprises
While distributing stateless services across multiple machines is fairly straightfor
ward, taking stateful data systems from a single node to a distributed setup can intro
duce a lot of additional complexity. For this reason, common wisdom until recently
was to keep your database on a single node (scale up) until scaling cost or high
availability requirements forced you to make it distributed.
As the tools and abstractions for distributed systems get better, this common wisdom
may change, at least for some kinds of applications. It is conceivable that distributed
data systems will become the default in the future, even for use cases that don’t handle large volumes of data or traffic. Over the course of the rest of this book we will
cover many kinds of distributed data systems, and discuss how they fare not just in
terms of scalability, but also ease of use and maintainability.
The architecture of systems that operate at large scale is usually highly specific to the
application—there is no such thing as a generic, one-size-fits-all scalable architecture
(informally known as magic scaling sauce). The problem may be the volume of reads,
the volume of writes, the volume of data to store, the complexity of the data, the
response time requirements, the access patterns, or (usually) some mixture of all of
these plus many more issues.
For example, a system that is designed to handle 100,000 requests per second, each
1 kB in size, looks very different from a system that is designed for 3 requests per
minute, each 2 GB in size—even though the two systems have the same data through
put.
An architecture that scales well for a particular application is built around assumptions of which operations will be common and which will be rare—the load parameters. If those assumptions turn out to be wrong, the engineering effort for scaling is at
best wasted, and at worst counterproductive. In an early-stage startup or an unproven product it’s usually more important to be able to iterate quickly on product features than it is to scale to some hypothetical future load.
Even though they are specific to a particular application, scalable architectures are
nevertheless usually built from general-purpose building blocks, arranged in familiar
patterns. In this book we discuss those building blocks and patterns.