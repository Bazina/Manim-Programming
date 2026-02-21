## what is Reliability (Hardware faults - Software errors - Human errors)?what is Reliability (Hardware faults - Software errors - Human errors)?
Everybody has an intuitive idea of what it means for something to be reliable or unre
liable. For software, typical expectations include:
• The application performs the function that the user expected.
• It can tolerate the user making mistakes or using the software in unexpected
ways.
• Its performance is good enough for the required use case, under the expected
load and data volume.
• The system prevents any unauthorized access and abuse.
If all those things together mean “working correctly,” then we can understand relia
bility as meaning, roughly, “continuing to work correctly, even when things go
wrong.”
The things that can go wrong are called faults, and systems that anticipate faults and
can cope with them are called fault-tolerant or resilient. 

Note that a fault is not the same as a failure [2]. A fault is usually defined as one com
ponent of the system deviating from its spec, whereas a failure is when the system as a
whole stops providing the required service to the user. It is impossible to reduce the
probability of a fault to zero; therefore it is usually best to design fault-tolerance
mechanisms that prevent faults from causing failures. In this book we cover several
techniques for building reliable systems from unreliable parts.

How Important Is Reliability?
Reliability is not just for nuclear power stations and air traffic control software—
more mundane applications are also expected to work reliably. Bugs in business
applications cause lost productivity (and legal risks if figures are reported incor
rectly), and outages of ecommerce sites can have huge costs in terms of lost revenue
and damage to reputation.
Even in “noncritical” applications we have a responsibility to our users. Consider a
parent who stores all their pictures and videos of their children in your photo appli
cation [15]. How would they feel if that database was suddenly corrupted? Would
they know how to restore it from a backup?
There are situations in which we may choose to sacrifice reliability in order to reduce
development cost (e.g., when developing a prototype product for an unproven mar
ket) or operational cost (e.g., for a service with a very narrow profit margin)—but we
should be very conscious of when we are cutting corners. 