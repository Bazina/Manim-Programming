ab 1: OLAP
Overview
Relational ERDs are sometimes extensively optimized for OLTP (Online Transactional Processing) to avoid problems such as data redundancy and slow writes. On the other hand, OLAP (Online Analytical Processing) systems are optimized for analytical operations that focus on aggregations and groupings on some dimensions or attributes without focusing much on row-level operations. 
Therefore, it is always required, for the purpose of OLAP, to convert relational schemas to star schemas. Star schemas are much more optimized for this purpose compared to 3NF schemas, for instance. 
Therefore, in this assignment, you will be performing an ETL process to convert some normalized relational schema to a star schema. 
Installation
As discussed above, it is required to perform an ETL (Extract, Transform, and Load) process to extract relational data from a MySQL data source, transform relational schema into a star counterpart, and finally load the new star schema and query it using Spark. 
Install MySQL
If you do not have MySQL, refer to this installation guide:
Ubuntu 22.04
Ubuntu 18.04
MacOS

Prepare Source OLTP Database
You will start this exercise by importing a ready to use database into MySQL. In this lab, we will use the TPCH database.
Generate TPCH data with scale-factor = 1, please check this tutorial for how to do that 

Install Apache NiFi
For the ETL part, we will be using Apache NiFi. Check the following to install Apache NiFi for Linux, Mac Os, or Windows. Find these guides for getting started with NiFi on both linux/Mac OS and Windows. And this is what you do after starting.

Note: If you install the latest version 2.2.0, and you should, please note that you should use Java 21. Check this tutorial on how to do this and switch between your current version or 21.


Install Apache Spark
For querying the star schema, we will use Spark as an OLAP engine. To install Spark, please follow the instructions in the following guide: https://spark.apache.org/downloads.html


Requirements
Design Star Schema
Given the following query
select
	n_name,
	s_name,
	sum(l_quantity) as sum_qty,
	sum(l_extendedprice) as sum_base_price,
	sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
	sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
	avg(l_quantity) as avg_qty,
	avg(l_extendedprice) as avg_price,
	avg(l_discount) as avg_disc,
	count(*) as count_order
from
	lineitem,
	orders,
	customers,
	nation,
	partsupp,
	supplier
where
	l_shipdate <= date '1998-12-01' - interval '90' day AND
	l_orderkey = o_orderkey AND
	o_custkey = c_custkey AND
	c_nationkey = n_nationkey AND
	l_ps_id = ps_id AND
	ps_suppkey = s_suppkey
group by
	n_name,
	s_name

It is required to optimize our database to execute it efficiently. This query is joining 6 tables. The estimated number of rows of these tables is as follows
nation		5
supplier 	10,000
customer	150,000
partsupp	300,000
orders		1,500,000
lineitem	6,000,000
You are required to design a star schema that adapts the TPCH schema for OLAP purposes. Check this tutorial for how to design such a schema. This set of slides discusses how to design a star schema for one of MySQL's complex schemas, the Sakila schema. Apply the practices used there to the TPCH  schema. 
Use NiFi for ETL
You are required to use Apache NiFi for migrating data from the source MySQL schema to Parquet files; each table is represented by a Parquet file(s). 

ETL stands for Extract,  Transform, and Load. Extraction is the process of pulling data out of some data sources for the purpose of transformation or migration. Transformation is the phase of changing the data in transit. Transformations include filtration, mapping, reducing, etc. Loading refers to persisting data into some final destination with capabilities not available in the original source.

NiFi is a drag-and-drop tool to build systems that automate the flow of data between software systems. It uses the concept of computational graphs, where the processing is done by building a graph of processing units called Processors. Some of the Processors are source Processors without any input needed. Others are just terminal Processors without output edges going out.
In our case, you need the following:
 A source Processor to fetch data from the MySQL employees schema
A group of Processors to transform the source relational schema to a star schema
A Processor to write output records to Parquet files
The following materials should be useful for you:
this simple tutorial shows how to read data from the MySQL source schema.
this simple tutorial shows how to write data as Parquet
NiFi Processors of possible interest to us:
ExecuteSQL
GenerateTableFetch (Note: Depending on the size of your machine, you may need this processor to extract MySQL records in batches)
ConvertAvroToParquet
PutFile
PutParquet
You can still build the application using other Processors. 
Please note that you need to configure batch processing, fetching rows chunk by chunk (for example 1000 rows at a time),  to avoid out of memory errors due to large data sets being loaded once in NiFi.

Note: You are required to build the transformation from source schema to star schema inside NiFi. You should not use Apache Spark for such processing. Meaning, you should not just transfer the data from MySQL to Parquet in original schema and do the joins using Spark upon query.

Execute the query for the Star and the Relational Schema
You are required to run the query above once on MySQL and again using SparkSQL against the parquet files. Take the average of the running this query 8 times
 
 Deliverables
You are required to deliver the following:
Steps showing generation of TPC data
Steps showing insertion of generated data into MySQL
DDL of the OTLP schema in MySQL
DDL of the Star schema or equivalent of transformation queries in NiFi or parquet schemas.
NiFi ETL graph with a brief description of each processor in the processing graph.
Table of  the 8 runs on MySQL and Spark showing time taken in each of the 16 runs
Report containing the previous deliverables

Notes
You should work in groups of four
You should come prepared for running the whole ETL pipeline during discussion if instructed to. So please get your environment ready for that.
All team members should be ready to answer any question during discussion
Any cheating will be severely penalized.

Parquet

Reasons

I like when humans gives weird reasons for their actions, like HRs saying “Oh, we needed 5 more YOE for this role” after taking final management round.

Or my girlfriend saying, “Oh, he’s just a friend”. Hmm…..🤐

Anyway,

Even google says that Parquet is a columnar storage file format. But that's not entirely true. And I will explain that in this blog. For now…

Apache Parquet is a hybrid of columnar and row(group) storage file format, widely used in big data and analytics ecosystems. It is designed for efficient data storage and retrieval, especially in distributed data processing.

Everyone knows the definition coz parquet is asked in most of the interviews. But have you ever questioned why hybrid? how is it efficient? 🤔

First, let's understand what a parquet file is made of —

Inside a Parquet file

How a parquet file is constructed
Press enter or click to view image in full size

An example of how a parquet file looks like
Row Groups
A row group in Parquet is a block of rows stored together on disk.

Think of each Row Group as a block of rows (say, 10,000).
Each row group contains column chunks for all columns
These row groups can be processed separately and in parallel, making them a perfect fit for spark processing 🤌
Column Chunks
Each column is stored contiguously inside the row group (marked in above image)
Each column chunk contains: Pages (Data, Dictionary, Index), Encoding info, Min/Max stats and Null count
Pages
Now, each column chunk is composed of:

Data Page — contains encoded column values
Dictionary Page — encoded repeated values to reduce size (optional)
Index Page — contains starting row number per page, mil/max value and null count.
For example, In Column A:

Page 1: rows 1–1000, min = 10, max = 50
Page 2: rows 1001–2000, min = 60, max = 100
→ Allows skipping Page 1 if query says value > 55
Footer
Footer is stored at the end of the file (with offset pointer at very end).

It contains schema, metadata, row group info, and statistics.
Allows reading just the footer to know what’s inside the file — great for pruning! 🤓
For example:

Row Group 1: column A min = 10, max = 100
Column encodings: dictionary for A, plain for B
→ Allows Spark to skip entire row groups or choose fast scan strategies.
If you were paying attention, you would have realized that “Pages” and “Footer” stores very similar data. And that's correct, but they store the data at different levels! 😎

Let me give an analogy:

Subscribe to the Medium newsletter
Imagine a book:

Index Page = index at the start of each chapter, telling you where sub-sections are.
Footer = the table of contents, summary, and glossary at the end of the book — telling you about the entire structure
“Spark always uses the Footer, and uses Index Page if available — but it’s often optional or absent unless explicitly enabled”

How Spark Optimizes with Parquet
Spark is deeply integrated with Parquet and uses Parquet’s metadata for performance optimizations.

1. Column Pruning (Projection Pushdown)
Spark reads only the columns needed by the query.
SELECT name FROM people WHERE age > 30
Spark reads only name and age columns from disk — not the entire row
2. Predicate Pushdown (Filter Pushdown)
Spark uses min/max stats per column/page from the Parquet footer to skip unnecessary row groups.
SELECT * FROM sales WHERE year = 2023
If a row group’s min/max for year is [2019, 2022], Spark skips it — no I/O or compute! 💪💪

3. Vectorized Reading
Instead of reading row-by-row, Spark reads batches of rows at a time using CPU-friendly memory structures.
Greatly reduces overhead and improves performance (~10x faster for some queries).
Enabled by default via:
spark.sql.parquet.enableVectorizedReader = true
4. Partition Pruning (at directory level)
If your Parquet data is partitioned (e.g., .../year=2023/month=08/), Spark skips entire directories based on the WHERE clause.
This happens before file scanning. 😏
5. Efficient Compression & Encoding
Parquet supports:

Column-wise compression (Snappy, GZIP, Brotli)
Encoding schemes (Dictionary, RLE, Delta)
Spark:

Uses Snappy by default (balance of speed & compression)
Leverages these to reduce size and accelerate decompression
Benefit: Less disk space, faster reads 😉

End-to-End Optimization Flow
Let’s say you run:

SELECT user_id FROM events WHERE country = 'US' AND date = '2025-01-01'
And the data is stored in:

/events/country=US/date=2025–01–01/part-000.parquet

Here’s how Spark optimizes:

Partition pruning: Skips non-US or non-Jan01 files.
Column pruning: Only reads user_id
Predicate pushdown: Uses footer stats to skip irrelevant row groups/pages
Vectorized read: Reads batches of user_id rows into memory
And that explains why parquet format is the first love of Apache Spark ❣️