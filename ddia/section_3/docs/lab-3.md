# Lab 3: Consistency

## Overview

In distributed database systems, failures are inevitable — disks, servers, racks, or
entire data centers can go down. Replication protects against data loss, but
coordinating writes across replicas introduces latency and consistency tradeoffs.

The central question: **how many replicas must acknowledge a read or write before
the client gets a response?** The answer is the system's _consistency level_.

This lab explores tunable consistency using **Apache Cassandra** — a distributed
wide-column store designed for high availability. You will experiment with
replication factors and consistency levels on a 3-node Docker cluster, observing
first-hand how the CAP theorem manifests in practice.

---

## Cluster Architecture

The lab runs a 3-node Cassandra cluster via Docker Compose.

| Component | Role |
|---|---|
| **cassandra-1** | Seed node — bootstrap contact point |
| **cassandra-2** | Regular node — joins via seed |
| **cassandra-3** | Regular node — joins via seed |

All three nodes form a single ring. Data is distributed across nodes using
**consistent hashing**: each row's partition key is hashed to a token, and that
token determines which node(s) own the data.

```
        ┌───────────┐
        │  Node 1   │  ← seed
        │ token 0   │
        └─────┬─────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───┴───┐         ┌───┴───┐
│ Node 2│         │ Node 3│
│token A│         │token B│
└───────┘         └───────┘
```

**Key insight:** With `SimpleStrategy`, Cassandra places replicas on the _next N
nodes_ clockwise on the ring, where N = replication factor.

---

## Installation

### Docker Compose Setup

1. Install Docker.
2. Start the cluster:

```bash
docker-compose -f docker-compose.yml up
```

1. Open a CQL shell on any node:

```bash
docker exec -it <container-id> cqlsh
```

### Useful Docker Commands

| Command | Purpose |
|---|---|
| `docker ps \| grep cassandra` | List running Cassandra containers |
| `docker container pause <id>` | Simulate a node failure (freezes the process) |
| `docker container unpause <id>` | Bring the node back |
| `docker exec -it <id> nodetool status` | Check ring membership and node state |
| `docker exec -it <id> nodetool ring` | View token assignments on the ring |

> **Tip:** Use `nodetool status` frequently — it shows you which nodes are
> Up/Down and how data ownership is distributed. This is essential for
> understanding why a query succeeds or fails at a given consistency level.

---

## Cassandra Data Model Primer

Before running experiments, understand how Cassandra organizes data.

### Primary Key Anatomy

```sql
PRIMARY KEY ((partition_key), clustering_col_1, clustering_col_2)
```

| Component | Purpose |
|---|---|
| **Partition key** | Determines which node(s) store the row (hashed to a token) |
| **Clustering columns** | Sort rows _within_ a partition on disk |

In this lab's schema:

```sql
PRIMARY KEY ((name), category, year, title)
```

- `name` is the **partition key** — all rows with the same `name` live on the same node(s).
- `category`, `year`, `title` are **clustering columns** — they define sort order within that partition.

### Why This Matters

Cassandra can only efficiently query by partition key. A `SELECT` with
`WHERE name = '...'` hits exactly one partition. Without the partition key in
`WHERE`, Cassandra must scan all nodes (a full-cluster scan), which is why it
rejects such queries by default.

**Discussion question:** What happens if you try
`SELECT * FROM books WHERE year = 2020;` without `ALLOW FILTERING`? Why?

---

## Consistency Levels Reference

Cassandra lets you set consistency **per query**. Here are the levels relevant to
this lab:

| Level | Reads require | Writes require | Trade-off |
|---|---|---|---|
| **ONE** | 1 replica responds | 1 replica acknowledges | Fastest, least consistent |
| **TWO** | 2 replicas respond | 2 replicas acknowledge | Middle ground |
| **QUORUM** | ⌊RF/2⌋ + 1 replicas | ⌊RF/2⌋ + 1 replicas | Strong consistency when R + W > RF |
| **ALL** | All RF replicas respond | All RF replicas acknowledge | Slowest, strongest guarantee |
| **ANY** (writes only) | — | At least 1 node (including hints) | Highest availability, weakest durability |

### The Quorum Formula

For a **strong read-after-write guarantee**:

```
R + W > RF
```

where R = read consistency, W = write consistency, RF = replication factor.

| RF | QUORUM value (⌊RF/2⌋ + 1) | Tolerates node failures |
|---|---|---|
| 1 | 1 | 0 |
| 2 | 2 | 0 (both must respond) |
| 3 | 2 | 1 |

> **Tip:** With RF=3 and QUORUM for both reads and writes, you get
> 2 + 2 = 4 > 3, so you are guaranteed to read the latest write. This is the
> most common production configuration.

**Discussion question:** With RF=2 and QUORUM, can you tolerate any node failure?
Why or why not?

---

## Requirements

Experiment with replication factors `1`, `2`, and `3`.

For each replication factor:

- Test read/write behavior when 1 or 2 nodes are down.
- Recreate/alter the keyspace as needed.

You will create a `bookstore` keyspace using `SimpleStrategy` (single datacenter)
with one virtual node per physical node for simplicity.

---

## A) Replication Factor = 1

Create schema and insert data:

```sql
CREATE KEYSPACE bookstore WITH replication =
  {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE bookstore.books (
  name     VARCHAR,
  category VARCHAR,
  year     INT,
  title    VARCHAR,
  PRIMARY KEY ((name), category, year, title)
) WITH CLUSTERING ORDER BY (category ASC, year DESC, title ASC);

INSERT INTO bookstore.books (name, category, year, title)
VALUES ('in to the woods', 'Fiction', 2020, 'In To The Woods');
```

Test in each case:

- Node 1 down
- Node 2 down
- Node 3 down

For each case, state whether changing the consistency level can make a failed query succeed.

> **Tip:** With RF=1, there is exactly one copy of the data. If the node that
> owns the partition is down, no consistency level can save the query — there is
> simply no replica to read from.

**Discussion question:** Is RF=1 ever acceptable in production? Under what circumstances?

---

## B) Replication Factor = 2

Alter keyspace and test:

```sql
ALTER KEYSPACE bookstore WITH REPLICATION =
  {'class': 'SimpleStrategy', 'replication_factor': 2};
```

> **Important:** After altering RF, run `nodetool repair` on each node to
> ensure data is actually replicated to the new replica set. Without repair,
> the extra replicas may not have the data yet.

```sql
CONSISTENCY QUORUM;

SELECT * FROM bookstore.books WHERE name = 'in to the woods';
```

Test in each case:

- Node 1 down
- Node 2 down
- Node 3 down
- Nodes 1 and 2 down
- Nodes 1 and 3 down
- Nodes 2 and 3 down

For each case, state whether changing the consistency level can make a failed query succeed.

> **Tip:** QUORUM with RF=2 means ⌊2/2⌋ + 1 = **2** — both replicas must
> respond. So QUORUM with RF=2 behaves like `ALL`. Try lowering to `ONE` when
> a node is down and observe what happens.

**Discussion question:** If you write at `ONE` and read at `ONE` with RF=2,
can you read stale data? Why?

---

## C) Replication Factor = 3

Alter keyspace and test:

```sql
ALTER KEYSPACE bookstore WITH REPLICATION =
  {'class': 'SimpleStrategy', 'replication_factor': 3};
```

```sql
CONSISTENCY QUORUM;

SELECT * FROM bookstore.books WHERE name = 'in to the woods';
```

Test in each case:

- Node 1 down
- Node 2 down
- Node 3 down
- Nodes 1 and 2 down
- Nodes 1 and 3 down
- Nodes 2 and 3 down

For each case, state whether changing the consistency level can make a failed query succeed.

> **Tip:** RF=3, QUORUM = 2. You can tolerate **1 node down** and still
> satisfy QUORUM. If 2 nodes are down, try `CONSISTENCY ONE` — it will
> succeed if the surviving node has a replica of the partition.

**Discussion question:** With RF=3 and all nodes up, what is the read latency
difference between `ONE` and `ALL`? Why does `ALL` take longer?

---

## D) Read Matrix

After running all experiments, fill this matrix with **Success** / **Failure** for
`SELECT` queries at default `QUORUM` consistency.

| Nodes Down | RF = 1 | RF = 2 | RF = 3 |
|---|---|---|---|
| Node 1 down |  |  |  |
| Node 2 down |  |  |  |
| Node 3 down |  |  |  |
| Nodes 1 and 2 down |  |  |  |
| Nodes 1 and 3 down |  |  |  |
| Nodes 2 and 3 down |  |  |  |

For each **Failure** cell, note which per-request consistency level (if any) would
make the query succeed.

---

## E) Write Matrix

Repeat the RF = 1, 2, 3 experiments for `INSERT` statements and record results
at default `QUORUM` consistency.

| Nodes Down | RF = 1 | RF = 2 | RF = 3 |
|---|---|---|---|
| Node 1 down |  |  |  |
| Node 2 down |  |  |  |
| Node 3 down |  |  |  |
| Nodes 1 and 2 down |  |  |  |
| Nodes 1 and 3 down |  |  |  |
| Nodes 2 and 3 down |  |  |  |

For each **Failure** cell, note which per-request consistency level (if any) would
make the query succeed.

> **Tip for writes:** Cassandra supports `CONSISTENCY ANY` for writes, which
> accepts a _hinted handoff_ — the coordinator stores a hint and replays it
> when the target node recovers. The write "succeeds" but the data is not
> yet on any replica. This is the weakest durability guarantee.

---

## Cassandra Tips & Tricks

### 1. `nodetool` Is Your Best Friend

| Command | What it tells you |
|---|---|
| `nodetool status` | Which nodes are Up/Down, data ownership % |
| `nodetool ring` | Token ranges assigned to each node |
| `nodetool repair` | Forces data sync across replicas (run after altering RF) |
| `nodetool getendpoints <ks> <table> <key>` | Which nodes own a specific partition key |
| `nodetool describecluster` | Cluster name, snitch, schema versions |

### 2. Tracing Queries

Enable tracing to see exactly which nodes participate in a query:

```sql
TRACING ON;
SELECT * FROM bookstore.books WHERE name = 'in to the woods';
TRACING OFF;
```

The trace output shows coordinator → replica communication, read-repair triggers,
and per-replica latency. This helps you understand _why_ a query failed or was slow.

### 3. Read Repair

When Cassandra reads from multiple replicas (e.g., at QUORUM), it compares
responses. If replicas disagree, it triggers a **read repair** — the
coordinator sends the most recent version to out-of-date replicas in the
background. This is why reads at higher consistency levels are self-healing.

### 4. Hinted Handoff

When a write's target replica is down, the coordinator stores a **hint** — a
record of the write — and replays it when the node recovers. Hints expire
after 3 hours by default. If the node is down longer, you need `nodetool repair`
to bring it up to date.

### 5. Tombstones and Deletes

Cassandra does not delete data immediately. It writes a **tombstone** marker
that suppresses the old value. Tombstones are purged during compaction after
`gc_grace_seconds` (default: 10 days). If you see "tombstone threshold exceeded"
warnings, your data model may have too many deletes.

### 6. Avoid These Common Mistakes

| Mistake | Why it's bad |
|---|---|
| Using `ALLOW FILTERING` in production | Forces full-cluster scan — O(all data) |
| Treating Cassandra like a relational DB | No JOINs, no ad-hoc WHERE clauses |
| Not running `repair` after RF changes | New replicas may be empty |
| Reusing `CONSISTENCY ALL` everywhere | One down node blocks all queries |
| Ignoring partition size | Partitions > 100 MB cause performance issues |

---

## Replication Strategies Reference

| Strategy | Use case | How replicas are placed |
|---|---|---|
| **SimpleStrategy** | Single datacenter (this lab) | Next N nodes clockwise on ring |
| **NetworkTopologyStrategy** | Multi-datacenter production | Specify RF per datacenter; rack-aware placement |

> **Production rule of thumb:** Always use `NetworkTopologyStrategy`, even with
> one datacenter — it makes future expansion painless.

---

## Key Technologies

| Technology | Role |
|---|---|
| **Apache Cassandra** | Distributed wide-column store with tunable consistency |
| **CQL (Cassandra Query Language)** | SQL-like language for Cassandra DDL and DML |
| **Docker / Docker Compose** | Container orchestration for the 3-node cluster |
| **nodetool** | CLI for Cassandra cluster management and diagnostics |
| **Consistent Hashing** | Data distribution strategy across the ring |
| **Quorum** | Consistency mechanism — majority of replicas must agree |

---

## Deliverables

Submit all of the following:

1. A running 3-node Cassandra cluster on Docker.
2. Screenshots showing terminal output for every test case.
3. Read matrix (D) and Write matrix (E) fully filled.
4. A report containing all results, screenshots, and answers to all discussion questions.

---

## Notes

- Change at least one column value between inserts to avoid confusing new writes with old query results.
- Work in groups of three.
- All team members should be ready to answer any question during discussion.
- Any cheating will be severely penalized.
