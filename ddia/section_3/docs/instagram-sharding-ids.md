# Instagram's Sharding & ID Generation

## Context

When a system shards data across multiple databases, the simple `AUTO_INCREMENT` primary key no longer works — each shard would generate overlapping IDs. Instagram needed globally unique, time-sortable, compact IDs without adding extra infrastructure.

This note walks through Instagram's approach and compares it with the alternatives covered in the Lab 2 ID Follow-Up.

**Source:** [Sharding & IDs at Instagram](https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c) (Instagram Engineering, 2012)

---

## Requirements

Instagram set three hard requirements for their ID system:

1. **Time-sortable** — a list of photo IDs can be sorted chronologically without extra data.
2. **64-bit** — smaller indexes, fits natively in most languages, Redis-friendly.
3. **Minimal moving parts** — no new services; leverage existing PostgreSQL infrastructure.

---

## Existing Solutions They Evaluated

| Approach | Example | Pros | Cons |
|---|---|---|---|
| App-generated IDs | MongoDB ObjectId, UUIDs | No coordination needed; timestamp-sortable (ObjectId) | 96–128 bits; random UUIDs have no natural sort |
| Dedicated ID service | Twitter Snowflake | 64-bit, time-sortable, fault-tolerant | Extra service + ZooKeeper coordination |
| DB Ticket Servers | Flickr (odd/even pair) | Well-understood scaling | Write bottleneck risk; multi-DB loses sort guarantee |

Twitter's Snowflake was the closest match, but Instagram wanted to avoid the operational overhead of a separate service.

---

## Instagram's Solution: In-Database Snowflake

Instead of running a dedicated service, Instagram **embedded the ID logic inside PostgreSQL** using PL/pgSQL functions.

### Logical Sharding

- Thousands of **logical shards** mapped to a smaller number of **physical servers**.
- Each logical shard = one PostgreSQL **schema** (namespace).
- Scaling up = moving schemas between physical servers — no re-bucketing.

### ID Bit Layout (64-bit total)

```
┌──────────────────────────┬─────────────┬────────────────┐
│  41 bits: milliseconds   │  13 bits:   │  10 bits:      │
│  since custom epoch      │  shard ID   │  sequence % 1024│
│  (≈ 41 years)            │  (0–8191)   │  per ms/shard  │
└──────────────────────────┴─────────────┴────────────────┘
MSB                                                     LSB
```

| Segment | Bits | Range | Purpose |
|---|---|---|---|
| Timestamp | 41 | ~69 years from epoch | Guarantees time-sortability |
| Shard ID | 13 | 0 – 8,191 logical shards | Embeds routing info in the ID |
| Sequence | 10 | 0 – 1,023 per ms per shard | Handles burst writes within the same millisecond |

**Throughput:** up to **1,024 IDs per shard per millisecond**.

### Worked Example

Given:

- Custom epoch: January 1, 2011
- Current time: September 9, 2011 at 5:00 PM → **1,387,263,000 ms** since epoch
- User ID: 31,341 → shard = `31341 % 2000` = **1,341**
- Sequence counter: next value = 5,001 → `5001 % 1024` = **905**

```
id  = 1387263000 << 23          -- shift timestamp left by (13 + 10) bits
id |= 1341       << 10          -- shift shard ID left by 10 bits
id |= (5001 % 1024)             -- fill lowest 10 bits with sequence
```

### PL/pgSQL Implementation

```sql
CREATE OR REPLACE FUNCTION insta5.next_id(OUT result bigint) AS $$
DECLARE
    our_epoch bigint := 1314220021721;
    seq_id    bigint;
    now_millis bigint;
    shard_id  int := 5;
BEGIN
    SELECT nextval('insta5.table_id_seq') %% 1024 INTO seq_id;
    SELECT FLOOR(EXTRACT(EPOCH FROM clock_timestamp()) * 1000)
           INTO now_millis;
    result := (now_millis - our_epoch) << 23;
    result := result | (shard_id << 10);
    result := result | (seq_id);
END;
$$ LANGUAGE PLPGSQL;
```

Table creation wires it up as the default:

```sql
CREATE TABLE insta5.our_table (
    "id" bigint NOT NULL DEFAULT insta5.next_id(),
    ...
);
```

---

## Comparison With Lab 2 ID Strategies

| Criterion | Auto-Increment | Composite PK | UUID | Instagram Snowflake |
|---|---|---|---|---|
| Size | 8 bytes | ~96 bytes | 36 bytes (CHAR) | **8 bytes (bigint)** |
| Time-sortable | Yes (single DB) | N/A | No (v4) | **Yes (by design)** |
| Distributed safe | No | Good | Best | **Yes — shard-aware** |
| Extra service needed | No | No | No | **No — in-DB function** |
| Shard routing in ID | No | No | No | **Yes (13 bits)** |
| Max IDs/ms/shard | 1 (sequence) | N/A | Unlimited | **1,024** |
| Human-readable | Yes | Moderate | Low | Moderate (decode bits) |

---

## Key Takeaways

1. **Embed shard routing in the ID** — eliminates a lookup step when reading. Given an ID, you can extract the shard and go directly to the right database.
2. **Custom epoch extends lifetime** — starting from 2011 instead of 1970 buys ~69 years before the 41-bit timestamp overflows.
3. **Logical ≠ physical shards** — decoupling allows rebalancing without re-keying data.
4. **No new services** — the entire solution runs inside PostgreSQL, keeping the architecture simple.
5. **Trade-off: 1,024 IDs/ms/shard ceiling** — sufficient for Instagram's write patterns, but bursty workloads on a single shard could hit the limit.

---

## Discussion Questions

1. What happens if a single shard generates more than 1,024 IDs in one millisecond? How would you handle the overflow?
2. Why did Instagram choose a **custom epoch** instead of Unix epoch? What are the implications?
3. How does embedding the shard ID in the primary key help with read queries?
4. Compare Instagram's approach to Twitter's Snowflake. When would you prefer one over the other?
5. If you were designing a similar system today, would you still use PL/pgSQL or move the logic to the application layer? Why?
