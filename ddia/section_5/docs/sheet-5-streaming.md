# Sheet 5: Streaming — Solution Guide

## Overview

Sheet 5 covers streaming fundamentals: how data flows from producers to consumers, what happens under overload, how to extend ordering guarantees, and how streaming tools differ in their transmission models.

---

## Background: What Are Data Streams?

Streams are **series of data constructs in transit** from a source to a destination.

```
DB (Source)  →  [D1, D2, D3, … DN]  →  Warehouse (Destination)
```

**Data formats in transit:** JSON/XML, plain text, binary (Protocol Buffers, Thrift, Avro)

**What invokes the stream?**

| Model | Description | Example |
|---|---|---|
| **ETL / Pull** | Destination pulls data from source on a schedule | Apache NiFi pulling from DB |
| **Push** | Source pushes data as events occur | Exporter emitting CDC events |

**Popular streaming tools:**

| Tool | Notes |
|---|---|
| Apache Kafka | Partitioned log — high throughput, replay |
| Apache Flink | Stateful stream processing (Java) |
| Apache Spark Streaming | Micro-batch streaming |
| Apache Storm | Low-latency real-time (Java) |
| Apache NiFi | No-code ETL / data routing |
| Apache Airflow | Workflow orchestration (Python) |
| StreamSets | No-code data pipeline |

**Choosing a tool:** existing org subscriptions → team skill set → language fit → performance benchmarks on your own workload.

---

## Q1: Producer Sends Faster Than Consumer Can Process

### The Problem

When producers outpace consumers, the system must choose a strategy. Three design choices:

---

### Option A — Drop Messages

**What:** Discard excess messages when consumer is overwhelmed.

**When to use:**

| Business Case | Why dropping is acceptable |
|---|---|
| **Client can retry** | Producer resends on next cycle — no data lost permanently |
| **Logging / monitoring** | Missing a few log lines or metrics is tolerable |
| **Heartbeat messages** | Purpose is just "I'm alive" — stale heartbeats have no value |

**Trade-off:** Simplest implementation. Zero memory overhead. Acceptable only when each message has low individual value or is reproducible.

---

### Option B — Buffer / Queue Messages

**What:** Hold excess messages in an in-memory or on-disk queue until the consumer catches up.

**When to use:**

| Business Case | Why buffering is needed |
|---|---|
| **Client cannot retry** | Producer is fire-and-forget (e.g., embedded device, one-shot event) |
| **IoT sensor readings** | Device under high load cannot afford to hold messages and resend |
| **High producer pressure** | Client doesn't have enough memory/CPU to maintain a resend queue |

**Trade-off:** Absorbs bursts. Risk of buffer overflow if consumer is permanently slower — must define eviction policy (drop oldest, drop newest, or block).

---

### Option C — Backpressure

**What:** Signal the producer to slow down — the consumer actively tells the producer to stop or throttle.

**When to use:**

| Business Case | Why backpressure is required |
|---|---|
| **Transactional systems (ATM)** | Every message is critical — cannot drop, cannot lose. Consumer must process each one |
| **Financial data pipelines** | Losing a trade event or payment event is unacceptable |

**Trade-off:** Strongest guarantee — zero data loss. But the producer must support being throttled. End-to-end latency increases under load. Requires protocol support (e.g., TCP flow control, reactive streams).

### Summary Table

| Strategy | Data Loss Risk | Producer Impact | Best For |
|---|---|---|---|
| Drop | High | None | Retryable, low-value messages |
| Buffer | Medium (if overflow) | None (until full) | IoT, fire-and-forget producers |
| Backpressure | None | Throttled | Transactional, critical messages |

---

## Q2: Topic-Level Ordering Guarantee

### Context

Kafka today guarantees ordering **per partition** — messages within a single partition are ordered, but messages across partitions in the same topic are not. The question asks: how would you impose ordering guarantees at the **topic level** (across all partitions)?

Two design approaches:

---

### Approach 1 — Ordered Storage: Merge Sweep

**Idea:** Each producer client writes to its own **temporary private partition**. Periodically, a background process merges all temporary partitions into one **main ordered partition** using timestamps (Merge Sweep).

```
Producer A → Temp Partition A ─┐
Producer B → Temp Partition B ─┤─[Merge Sweep by timestamp]─→ Main Ordered Partition
Producer C → Temp Partition C ─┘
```

**Advantages:**
- No multiple connection switches between partition machines during writes
- No inner-partition data shuffling needed to satisfy inter-partition order
- Reads from the main partition are inherently ordered

**Disadvantages:**
- **Single point of failure** — if no replication, all data funnels into one partition; others become dormant
- Merge latency means ordering is eventual, not real-time
- Write throughput limited by merge frequency

---

### Approach 2 — Shuffled Partitions with Global Sequence Number

**Idea:** Producers write to **any partition** as before, but each message gets a **global monotonic sequence number** (timestamp or logical clock). Consumers read across all partitions and sort by sequence number before processing.

```
Producer A → Partition 1 (seq=1, seq=4, seq=7)
Producer B → Partition 2 (seq=2, seq=5, seq=8)
Producer C → Partition 3 (seq=3, seq=6, seq=9)
                 ↓
         Consumer reads all partitions → sorts by seq → ordered view
```

**Advantages:**
- Minimal change to existing write path — "same old code, new layer"
- All partitions remain active — no dormant partitions
- Better write throughput (parallelism preserved)

**Disadvantages:**
- **Shuffling on read** — consumers must read from all partitions and sort
- **Sequence number synchronization** — global counter is a coordination bottleneck; performance hit under high throughput
- Requires atomic sequence number generation (distributed counter or central sequencer)

### Comparison

| | Merge Sweep | Global Sequence |
|---|---|---|
| Write path | Private temp partitions | Any partition (unchanged) |
| Read path | Simple (pre-ordered) | Sort across all partitions |
| Ordering latency | Eventual (merge interval) | Near real-time |
| Failure risk | Single main partition | Distributed (resilient) |
| Code change | Significant (merge logic) | Minimal (sequence layer) |

---

## Q3: Other Streaming Tools — Transmission Models

Three transmission models exist in streaming systems:

| Model | Description |
|---|---|
| **Direct** | Producer sends directly to consumer (point-to-point) |
| **Broker** | Messages pass through a central broker that routes them |
| **Partitioned Log** | Messages written to an append-only log, consumers read at their own offset |

### Tools

| Tool | Transmission Model | Notes |
|---|---|---|
| **ActiveMQ** | Broker | JMS-based, traditional enterprise messaging |
| **RabbitMQ** | Broker | AMQP, flexible routing via exchanges and queues |
| **Amazon Kinesis** | Partitioned Log | AWS-managed Kafka alternative, shards = partitions |
| **Apache Kafka** | Partitioned Log | De facto standard for high-throughput streaming |
| **Apache Flink** | — (processing engine) | Consumes from Kafka/Kinesis; not a transmission system itself |

### When Each Model Fits

| Model | Use When |
|---|---|
| Direct | Low-volume, simple producer-consumer pairs; no persistence needed |
| Broker | Complex routing, fan-out, task queues, request-reply patterns |
| Partitioned Log | High throughput, replay, audit trail, multiple independent consumers |

---

## Key Concepts Reference

| Term | Definition |
|---|---|
| **Backpressure** | Consumer signals producer to slow down; prevents data loss without buffering |
| **Merge Sweep** | Background process that merges multiple partial streams into one ordered log |
| **Global Sequence Number** | Monotonic counter assigned to each message across all partitions |
| **Partitioned Log** | Append-only, ordered log split into partitions; consumers track own offset |
| **Broker** | Intermediary that receives, routes, and delivers messages between producers and consumers |
| **ETL** | Extract-Transform-Load; batch or streaming pipeline moving data between systems |

---

## Deliverables

- [ ] Q1: Three strategies explained with a real business use case for each
- [ ] Q2: Two designs for topic-level ordering with pros/cons for each
- [ ] Q3: At least 3 tools listed with their transmission model

## Notes

- Backpressure requires **end-to-end protocol support** — the producer must be able to receive and respect the throttle signal
- Approach 2 (global sequence) has a well-known distributed systems problem: the global counter itself becomes a bottleneck; solutions include logical clocks (Lamport timestamps) or vector clocks
- Amazon Kinesis shards map directly to Kafka partitions — the concepts transfer
