## What is data intensive?
Many applications today are data-intensive, as opposed to compute-intensive. Raw
CPU power is rarely a limiting factor for these applications—bigger problems are
usually **the amount of data, the complexity of data, and the speed at which it is
changing**.
A data-intensive application is typically built from standard building blocks that pro
vide commonly needed functionality. For example, many applications need to:
• Store data so that they, or another application, can find it again later (databases)
• Remember the result of an expensive operation, to speed up reads (caches)
• Allow users to search data by keyword or filter it in various ways (search indexes)
• Send a message to another process, to be handled asynchronously (stream pro
cessing)
• Periodically crunch a large amount of accumulated data (batch processing)

If you are designing a data system or service, a lot of tricky questions arise. How do
you ensure that the data remains correct and complete, even when things go wrong
internally? How do you provide consistently good performance to clients, even when
parts of your system are degraded? How do you scale to handle an increase in load?
What does a good API for the service look like?