# Sheet 4: Consistency — Solution Guide

## Overview

Sheet 4 covers the theoretical foundations of **consistency** in distributed systems. Questions span isolation vs. ordering semantics, linearizability analysis, FIFO queue correctness, and CAP theorem trade-offs with practical solutions.

---

## Q1: Isolation Guarantees vs. Ordering Guarantees

### Definitions

| Concept | Definition |
|---|---|
| **Isolation Guarantee** | Degree to which concurrent transactions are hidden from each other — each transaction sees a consistent snapshot and is not affected by in-progress transactions |
| **Ordering Guarantee** | Degree to which operations are observed in a consistent, agreed-upon order across all nodes/clients in the system |

### Key Distinction

- **Isolation** is about *inter-transaction visibility* — preventing dirty reads, non-repeatable reads, phantom reads.
- **Ordering** is about *operation sequencing* — ensuring all observers agree on which operation happened "first".

A system can have strong isolation (serializability) but weak ordering (no global clock), or strong ordering (linearizability) but no transaction support at all.

### Visual Example

**Good Isolation:**
```
Transaction 1:   Write A = 2 ──────────── Commit
Transaction 2:   Read A ──────── = 1 ──── Commit
```
Transaction 2 reads the old value (1) before Transaction 1 commits. Correct — no dirty read.

**Bad Isolation:**
```
Transaction 1:   Write A = 2 ──────────── Commit
Transaction 2:   Read A ──── = 2 ──────── Commit
```
Transaction 2 reads the uncommitted value (2). This is a **dirty read** — violates isolation.

---

## Q2: Linearizability — Shared Register History

### Setup

Two shared registers: **R** and **Q**. Three clients: A, B, C.  
Operations: `write(x)` → void, `read()` → int.

### Original History H

```
A: R.write(1)  ─────────────────────── A: R: void
B: R.read()    ──────── B: R: 1
C: R.write(2)  ─────────────────────── C: R: void
B: R.read()    ────────────────── B: R: 1
A: Q.write(3)  ─────────────────────── A: Q: void
C: R.read()    ───────────────────── C: R: 2
                                          Time →
```

### Is H Linearizable? **YES**

**Reasoning:**  
A linearization is a sequential reordering of operations that respects real-time overlap and register semantics.

One valid linearization:
1. `A: R.write(1)` → R = 1
2. `B: R.read()` → 1 ✓ (reads value written by A)
3. `C: R.write(2)` → R = 2
4. `B: R.read()` → 1 ✓ (B's second read overlaps C's write, may see old value)
5. `A: Q.write(3)` → Q = 3
6. `C: R.read()` → 2 ✓ (C sees the value it wrote)

All reads return values consistent with a valid sequential execution → **linearizable**.

### Making H Non-Linearizable

Change C's final `R.read()` to return **1** instead of **2**:

```
A: R.write(1)  ─────────────────────── A: R: void
B: R.read()    ──────── B: R: 2        ← B sees 2 (C's write)
C: R.write(2)  ─────────────────────── C: R: void
B: R.read()    ────────────────── B: R: 2
A: Q.write(3)  ─────────────────────── A: Q: void
C: R.read()    ─────────────────── C: R: 1  ✗ ← regression!
                                          Time →
```

**Why non-linearizable:**  
B already observed R = 2 (C's write). For C to then read R = 1 means a client observed a *newer* value, then a subsequent read returns an *older* value. This violates the linearizability requirement that once a value is visible, it cannot be un-seen.

---

## Q3: FIFO Queue Linearizability

### History H

```
A: q.enq(x) ────────── A: q: void
B: q.enq(y) ────────── B: q: void
A: q.deq()  ──────── A: q: y
C: q.deq()  ──────── C: q: y
```

### Is H Linearizable? **NO**

**Reason:** The element `y` was enqueued **once** but dequeued **twice**.

This violates the fundamental semantics of a FIFO queue: each enqueued element may only be dequeued once. There is no valid sequential reordering that produces `deq() → y` twice from a single `enq(y)`.

Additionally, `x` was enqueued but never dequeued — in a valid FIFO, x should be dequeued before y (FIFO order).

**Correct linearizable result would be:**
```
A: q.deq() → x    (x was enqueued first by A)
C: q.deq() → y    (y was enqueued second by B)
```

---

## Q4: CAP Trade-off in Read-Your-Writes (RAW)

### Problem

**Read-After-Write** consistency: after a client writes data, it must always read back that same data on subsequent reads.

**Solution analyzed:** Route all reads to the **leader replica** (the node that received the write).

### Which CAP Guarantee Is Lost? **Availability**

**Reasoning:**

| Scenario | Effect |
|---|---|
| Leader is healthy | Reads routed to leader → always sees latest write ✓ |
| Leader crashes / network partition | Leader unreachable → reads cannot be served ✗ |
| Follower takes over (no guarantee of freshness) | May not have the latest write → violates RAW |

By requiring reads to always hit the leader, the system **sacrifices Availability**: if the leader is down, reads fail rather than serving potentially stale data.

### Why Partition Tolerance Is Still Maintained

P does **not** mean "works fine during a partition." It means the system has a deliberate, correct strategy when a partition occurs — rather than deadlocking, corrupting state, or returning silently wrong data.

In practice, **P is always assumed** in distributed systems. Network splits are inevitable; you cannot design them away. CAP is therefore really a binary choice:

> When a partition occurs → choose **Consistency** or **Availability**?

The leader-read solution chooses **C**:

| Partition scenario | What happens |
|---|---|
| Client can reach leader | Read succeeds, always fresh |
| Client cannot reach leader | Read **fails with error** (correct — no stale data served) |
| Follower still running | Follower correctly refuses reads |

Refusing the read IS the partition-tolerant behavior. The system detected the split and responded without corrupting the consistency guarantee. That is P working as intended.

**Violating P** would look like: the system deadlocks, returns unpredictable results, or silently diverges — none of which happen here.

> **CAP Summary:** This solution maintains Consistency (C) and Partition Tolerance (P) but gives up Availability (A) — a **CP system**. P is always assumed; the real trade-off is C vs A when a partition fires.

---

## Q5: Monotonic Reads — Alternative to Sticky Sessions

### Problem

**Monotonic Reads** guarantee: a client never reads data older than what it has previously read. Without sticky sessions (which pin a client to one replica), clients may jump between replicas with different replication lag and observe time-traveling reads.

### Solution: Version Timestamps

**Approach:** Track the version (logical timestamp) of the last read value and attach it to subsequent queries.
Figure 5-4. A user first reads from a fresh replica, then from a stale replica. Time
appears to go backward. To prevent this anomaly, we need monotonic reads

```
Step 1: Client reads from Replica A → gets value at timestamp T=42
Step 2: Client stores T=42 locally
Step 3: Client sends next read with: { query: "...", min_timestamp: 42 }
Step 4: Replica receiving request checks its own timestamp
        - If replica_timestamp >= 42 → serve the read
        - If replica_timestamp < 42  → block/wait until replica catches up
```

**Why this works:**  
The replica either already has data at or beyond T=42 (serves immediately), or it waits for replication to catch up before responding. Either way, the client never reads data older than T=42.

**Advantages over sticky sessions:**

| Property | Sticky Sessions | Version Timestamps |
|---|---|---|
| Load distribution | Pinned to one replica | Any replica can serve |
| Failover | Session breaks if replica dies | Seamlessly route to another |
| Complexity | Simple routing | Requires client-side timestamp tracking |
| Stale read prevention | Yes (same replica) | Yes (timestamp enforcement) |

---

## Key Concepts Reference

| Term | Definition |
|---|---|
| **Linearizability** | Strongest consistency model — reads always return the most recent write, as if there is a single copy of data |
| **Serializability** | Transaction isolation — concurrent transactions appear to execute in some serial order |
| **FIFO Queue semantics** | Elements dequeued in the same order as enqueued; each element dequeued exactly once |
| **Read-After-Write (RAW)** | Client always reads its own most recent writes |
| **Monotonic Reads** | Client never sees data older than what it previously read |
| **Sticky Sessions** | Client pinned to same replica for session duration |
| **CAP Theorem** | Distributed system can guarantee at most 2 of: Consistency, Availability, Partition Tolerance |
| **Leader Replica** | Primary node that receives all writes and coordinates replication |

---

## Deliverables

- [ ] Q1: Written explanation distinguishing isolation from ordering + diagram
- [ ] Q2: Linearizability proof + modified non-linearizable history
- [ ] Q3: Explanation of why FIFO queue history is not linearizable
- [ ] Q4: Identified which CAP guarantee is violated + explanation
- [ ] Q5: Described timestamp-based monotonic reads solution

## Notes

- Linearizability applies to **single operations** on individual objects (registers, queues)
- Serializability applies to **multi-operation transactions**
- These two are orthogonal — a system can have both (strict serializability), neither, or one without the other
- The "staleness window" in the timestamp solution depends on replication lag — in high-lag environments, clients may experience noticeable blocking
