# Section 9: Distributed Transactions — Scene Script

## Overview

A Manim slide deck that follows one booking of **room 101** through three services (Booking, Payment, Accounting) and shows how we keep them consistent: first inside one database, then with **2PC**, then with a **Saga**, and finally with a **distributed lock + fencing token**.

No real system runs. Every "log line" and "table row" on screen is an animated mobject.

**Sources**

| Topic | DDIA pages |
|---|---|
| Write skew, booking example, phantoms, materializing conflicts | 249–251 |
| Two-phase locking (2PL), predicate / index-range locks | 257–260 |
| The leader and the lock, fencing tokens | 301–304 |
| Atomic commit, 2PC, coordinator failure, XA, in-doubt locks | 353–364 |

Video reference: Hello Interview, *Distributed Transactions Explained: 2 Phase Commit vs Saga Pattern* (https://youtu.be/DOFflggE_0Q).

**Target file:** `ddia/section_9/distributed_transactions.py`
**Class:** `DistributedTransactions(SlideStyleMixin, BaseSlide)`, same skeleton as `section_8/sheet_6_integration_patterns.py` (`config.background_color = "#0D1117"`, one `scene_*` method per scene, `self._next_slide()` between beats, `FadeOut(*self.mobjects)` at the end of each scene).

---

## Visual Language

Keep it consistent across all scenes so students learn the colors once.

| Thing | Color | Icon / shape |
|---|---|---|
| Booking service + `booking_db` | `BLUE` | `ICON_SERVER` + `ICON_DATABASE` |
| Payment service + `payment_db` | `ORANGE` | `ICON_SERVER` + `ICON_DATABASE` |
| Accounting service + `accounting_db` | `PURPLE` | `ICON_SERVER` + `ICON_DATABASE` |
| Coordinator / orchestrator | `TEAL` | `ICON_STRUCTURE` |
| Lock service (Redis) | `YELLOW` | `ICON_LOCK` |
| Success / commit | `GREEN` | `ICON_CHECK` |
| Failure / abort / conflict | `RED` | `ICON_DANGER` |
| Crash | `RED` | `ICON_BOMB` |
| Waiting / blocked / lease | `GREY_B` | `ICON_STOPWATCH` |
| User | `GREY_A` | `make_user_icon` |

**Recurring layouts**

- **Service row**: the three service cards side by side (`make_icon_card`), each with its DB icon under it. Scenes 1, 2, 6, 7, 12 and 13 reuse it.
- **Sequence rows**: one horizontal dashed row per actor (icon + label on the left), time flows **left → right** via the `_tx(t)` mapping, messages are diagonal `Arrow`s between rows with a small `make_label`. Same construction as `scene_q5_monotonic` in `section_4/sheet_4_consistency.py` (`_row`, `_arr`, `_msg`). Scenes 7–10 and 18–19 use it. This matches Figures 9-9, 9-10, 8-4 and 8-5 in the book.
- **Transaction timelines**: for T1/T2 races (Scene 3), use sheet 4's `_client_row` + `_op_box` (a box spanning `[t_call, t_ret]` with `=> result` on the right) + `_db_row` / `_db_marker` for the table state. End with `_verdict_badge`.
- **Architecture nodes**: icon above label, as in `arch_node` from `section_7/project_weather_stations.py`. Use it for the service row.
- **Log panel**: a `_code_box` at the bottom or right side. Lines are added one at a time with `AddTextLetterByLetter` (fast, `time_per_char=0.01`), in the form `SERVICE  message`, with the service name colored.
- **Lock bar**: a thin translucent rectangle drawn on a participant's row from the moment it locks until commit (the shaded area in Figure 9-9). It grows rightward with `GrowFromEdge(bar, LEFT)`.

Reuse `_section_header`, `_flow_node`, `_flow_arrow`, `_code_box`, `make_comparison_table`, `create_rect_glow`, `make_code_text` and `make_icon`. The timeline helpers (`_tx`, `_make_op`, `_client_row`, `_op_box`, `_db_marker`, `_verdict_badge`) live inside `sheet_4_consistency.py`. Copy the ones this deck uses into the new file, the same way sheet 4 copied its style from the weather project. Don't add new helpers unless two or more scenes need them.

---

## Part 0 — Setup

### Scene 0: `scene_title`

- Title: **Distributed Transactions**
- Subtitle: *One booking, three services, no shared commit.*
- Small caption: `DDIA ch. 7 · 8 · 9`
- Beat: fade in title, then subtitle. `_next_slide()`.

### Scene 1: `scene_story`

**Goal:** set up the problem in one picture.

1. A user icon on the left. A speech label: *"Book room 101 for tonight"*.
2. An arrow to the **service row**: Booking → Payment → Accounting, one card each.
3. Under each card, the one thing it does, revealed in order:
   - Booking: *reserve room 101*
   - Payment: *take $120*
   - Accounting: *record revenue*
4. Draw a rounded bracket around all three cards. Label: **All three, or none.**
5. Glow the bracket (`create_rect_glow`, `TEAL`).

Narration: each service owns its own database, so there is no single `COMMIT` that covers all three. That's the whole problem.

### Scene 2: `scene_schema`

**Goal:** show the minimal schema once so later scenes can point at it.

Three `_code_box`es side by side under their service cards:

```
booking_db
  rooms     (room_id PK, booked_by, fence_token)
  bookings  (id PK, room_id, starts_at, ends_at,
             user_id, status)
            status ∈ PENDING | CONFIRMED | CANCELLED
```

```
payment_db
  wallets   (user_id PK, balance CHECK >= 0)
  payments  (id PK, booking_id UNIQUE,
             amount, status)
            status ∈ CHARGED | REFUNDED
```

```
accounting_db
  ledger    (id PK, booking_id, kind, amount)
            kind ∈ REVENUE | REVERSAL
            UNIQUE (booking_id, kind)
            append only
```

Then highlight three things in turn, each with a short caption:

| Highlight | Caption |
|---|---|
| `CHECK >= 0` | this is how Payment can say **no** |
| `booking_id UNIQUE` | a retry of the same step is a no-op |
| `append only` | Accounting never deletes, it reverses |

`booked_by` and `fence_token` stay dimmed with a caption: *used in Part 4*.

### Scene 2b: `scene_prerequisites`

**Goal:** a quick ACID recap before anything breaks.

Four icon cards, one per letter:
- **Atomicity**: all the writes happen, or none of them. This is what we fight for across services.
- **Consistency**: the rules hold before and after, like `CHECK (balance >= 0)`.
- **Isolation**: two transactions running at once don't see each other's half-done work.
- **Durability**: once `COMMIT` returns, the data survives a crash (the write-ahead log).

Roadmap chips: *Part 1 → I on one database* · *Parts 2 and 3 → A across three databases* · *Part 4 → locks across machines*.

---

## Part 1 — One Database First (p. 249–260)

### Scene 3: `scene_write_skew`

**Goal:** show double booking inside a single database under snapshot isolation.

Layout: sheet 4 style. Two `_client_row`s, **T1** (Alice, BLUE) and **T2** (Bob, ORANGE), then a `_db_row` for `bookings` at the bottom. Each statement is an `_op_box` placed on the time axis, and each commit adds a `_db_marker` (`rows: 1`, then `rows: 2`).

| Step | T1 | T2 |
|---|---|---|
| 1 | `BEGIN` (REPEATABLE READ) | |
| 2 | | `BEGIN` (REPEATABLE READ) |
| 3 | `SELECT count(*) … room 101, 12:00–13:00` → **0** | |
| 4 | | same `SELECT` → **0** |
| 5 | `INSERT booking` · `COMMIT` ✓ | |
| 6 | | `INSERT booking` · `COMMIT` ✓ |

- After step 5, `_db_marker` shows `rows: 1 (Alice)`.
- After step 6, it shows `rows: 2`. Both markers flash `RED`. `_verdict_badge("Room 101 booked twice  ✗", RED)`.
- Caption: **Write skew.** Each transaction read, decided and wrote correctly. Together they broke the rule.

Show the book's 3-step pattern as a small `_reveal_rows` list:
1. `SELECT` checks a condition
2. The app decides based on the result
3. `INSERT` changes the result of step 1

### Scene 4: `scene_phantom`

**Goal:** explain why `SELECT … FOR UPDATE` doesn't save us.

1. Replay step 3 with `FOR UPDATE` appended.
2. The query returns **0 rows**. A lock icon (`ICON_LOCK`, YELLOW) drops toward the empty result set and finds nothing to attach to. It fades out.
3. Caption: *You can't lock a row that doesn't exist yet.* That row is a **phantom**.

Then a `make_comparison_table` with three fixes:

| Fix | Idea | Note |
|---|---|---|
| Materialize the conflict | lock the `rooms` row for room 101 first, so there is something to lock | last resort, leaks locking into the data model |
| `SERIALIZABLE` | the database detects the conflict and aborts one | in Postgres this is **SSI**, not 2PL |
| Exclusion constraint | the DB rejects overlapping ranges for the same room | what we'd use in production (`EXCLUDE USING gist`) |

Glow the last row.

### Scene 4b: `scene_materialize_conflicts`

**Goal:** expand the first fix from Scene 4 (p. 251).

1. A `room_slots` grid for room 101, one cell per 15 minutes from 11:00 to 13:45. Caption: *created ahead for the next 6 months, it stores nothing*.
2. T1 (Alice) runs `SELECT … FROM room_slots WHERE room_id = 101 AND slot >= '12:00' AND slot < '13:00' FOR UPDATE`. Four cells turn blue with lock icons.
3. T2 (Bob) wants 12:30–13:30. An orange frame covers its four cells, the two overlapping ones flash RED, and a chip says *T2 waits*.
4. T1 checks bookings, INSERTs, and commits, which releases its locks. T2 takes its cells, re-checks bookings, sees Alice's row, and backs off. Footnote: *run it in READ COMMITTED so T2's re-check sees T1's row*. Under snapshot isolation the re-check would still read the old snapshot.
5. The catch, as three cards:
   - lock size: one row per room serializes every booking of that room, 15-minute slots are 96 rows per room per day
   - concurrency leaks into the data model
   - hard to get right, so it's a last resort. Prefer `SERIALIZABLE` or an exclusion constraint.

### Scene 5: `scene_two_phase_locking`

**Goal:** 2PL in one picture, and set up why 2PC hurts later.

1. Two lock types as cards:
   - **Shared (S)**: many readers at once
   - **Exclusive (X)**: one writer, nobody else
2. A 2×2 compatibility grid (S/X × S/X) where only S+S is green.
3. **The two phases.** A small line chart titled *locks held* over time: it rises while the transaction runs (the *growing* phase), stays flat, then drops to 0 at `COMMIT` (the *shrinking* phase). Put a label on each phase.
4. **Predicate lock** (p. 259): a shaded range on a timeline of room 101, 12:00–13:00. An `INSERT` arrow from another transaction hits the range and stops. Caption: *the lock covers rows that don't exist yet*. Then show the index-range approximation: the shaded area grows to "all of room 101". Caption: *safe because it locks more, not less*.
5. **Deadlock**: two transactions, two rows, crossed "waits for" arrows forming a cycle. The DB picks one, and it turns RED with **aborted, retry**.
6. Callout box (`TEAL` border): **2PL ≠ 2PC.** 2PL gives isolation on one DB. 2PC gives atomic commit across many.

Closing line: *Locks are held until commit.* Keep this line on screen as the scene fades, because Scene 9 brings it back.

---

## Part 2 — Two-Phase Commit (p. 353–364)

### Scene 5b: `scene_single_db_baseline`

**Goal:** show the booking working on **one** database first, so the jump to three databases has something to compare against (p. 354).

1. The same booking as one `BEGIN … COMMIT` on `hotel_db`, which holds all four tables (bookings, wallets, payments, ledger). Caption: *if the CHECK fails, the whole thing rolls back*.
2. **How one database does it:** the write-ahead log fills up record by record: `booking`, `wallet -120`, `payment`, `ledger`, `COMMIT`. The `COMMIT` record glows. Caption: *commit point, the moment the disk finishes writing this one record*.
3. **Crash before vs after:**
   - crash before `COMMIT` is on disk → on restart there is no commit record, so all 4 writes are undone
   - crash after → the commit record is found, so all 4 are kept
   - caption: *one disk, one commit record, one decision*
4. **Now split it:** `hotel_db` splits into `booking_db`, `payment_db` and `accounting_db`, each with its own log ending in `COMMIT ?`. Badge: *three disks, three commit records, which one is the commit point?* Then three lines: each database can only commit its own part · one can say yes while another says no or crashes · nobody is in charge of the final answer. That leads straight into Scene 6.

### Scene 6: `scene_why_not_one_phase`

**Goal:** show why "just send COMMIT to everyone" breaks atomicity.

1. The coordinator (TEAL) on top, the three DBs below.
2. The coordinator sends `COMMIT` to all three at once.
3. Booking ✓ and Accounting ✓ turn green. Payment turns RED with `CHECK violation: balance < 0`.
4. Result strip: *room reserved, revenue recorded, no money taken.*
5. Caption from p. 355: *once committed, a node can't take it back*. A node must only commit once it's **sure** everyone else will.

Three small failure chips under it, from the book's list:
- constraint violation on one node
- a commit request lost in the network
- a node crashes before writing its commit record

### Scene 7: `scene_2pc_happy_path`

**Goal:** recreate Figure 9-9 with our services.

**Sequence rows** (top → bottom): Coordinator, booking_db, payment_db, accounting_db. The log panel sits underneath, full width.

| # | Message | Log line |
|---|---|---|
| 1 | coord → all: writes inside local tx `gid=bk-7f2` | `COORD    begin gid=bk-7f2` |
| 2 | | `BOOKING  INSERT booking CONFIRMED` |
| 3 | | `PAYMENT  wallet -120, INSERT payment` |
| 4 | | `ACCOUNT  INSERT ledger REVENUE 120` |
| 5 | coord → all: **prepare** | |
| 6 | all → coord: **yes** (three green arrows) | `BOOKING/PAYMENT/ACCOUNT  PREPARE TRANSACTION 'bk-7f2' → yes` |
| 7 | coord writes decision to its own disk | `COORD    tx_log bk-7f2 = COMMIT` |
| 8 | coord → all: **commit** | `…  COMMIT PREPARED 'bk-7f2'` |

- At step 7, freeze for a beat and glow the coordinator's disk icon. Label: **commit point**.
- Draw a **lock bar** along each participant lifeline from step 1 to step 8. Label it *locks held*.

Then two "points of no return" cards (p. 358):
1. A participant that votes **yes** gives up the right to abort.
2. Once the coordinator decides, that decision is final. It retries forever.

Optional light touch: the book's wedding analogy as one line, *"I do" = yes vote, minister = coordinator*.

### Scene 8: `scene_2pc_vote_no`

**Goal:** show how an abort goes.

- Same lanes. At prepare time Payment's arrow comes back RED: **no**. Log line: `PAYMENT  CHECK violation, balance 50 < 120`.
- The coordinator logs `tx_log bk-8a1 = ABORT` and sends **abort** to all three.
- Booking and Accounting roll back. Their pending rows fade out of the mini tables.
- Result: *nothing happened anywhere.* GREEN check. That's atomicity doing its job.

### Scene 9: `scene_2pc_coordinator_crash`

**Goal:** recreate Figure 9-10 and make the *in-doubt* pain visible.

1. Replay prepare, where all three vote **yes**.
2. The coordinator gets an `ICON_BOMB` and its lifeline turns dashed grey. Nothing more comes from it.
3. Each participant shows a status chip: **IN DOUBT**, plus a stopwatch that keeps counting (`00:01 … 20:00`, a `DecimalNumber` driven by a `ValueTracker`).
4. The lock bars keep growing to the right, past the edge of the timeline.
5. A new transaction arrives at payment_db: `UPDATE wallets … user u1`. Its arrow stops at the lock bar and a stopwatch appears. Label: **blocked**.
6. Caption (p. 358): *timing out doesn't help, the participant can't know if the others committed.*
7. Beat: "restart payment_db". The DB icon blinks off and on. The chip still says **IN DOUBT** and the lock bar is still there. Caption: *a correct 2PC keeps the lock even across restarts* (p. 363).

Callback: bring back the Scene 5 line *Locks are held until commit.*, now with the extra line *… and commit is waiting on a dead coordinator.*

### Scene 10: `scene_2pc_recovery`

**Goal:** show how recovery works, and how the escape hatch breaks things.

**Beat A: recovery**
- The coordinator comes back and reads its `tx_log`.
  - Case 1: no decision for `bk-7f2`, so it sends **abort** to all.
  - Case 2: `COMMIT` is logged but only booking got it, so it sends **commit** to payment and accounting.
- For case 2, pause on the in-between state first: the booking table shows CONFIRMED while the payment table is still empty. Caption: *atomic commit, but not atomic visibility.*

**Beat B: heuristic decision**
- An admin icon runs `ROLLBACK PREPARED` on payment_db by hand.
- The coordinator later sends commit, and payment answers `does not exist`.
- End state: booking CONFIRMED, ledger REVENUE, **no payment**. Everything flashes RED.
- Caption (p. 363): *"heuristic" is a polite word for "probably broke atomicity".*

### Scene 11: `scene_2pc_cost`

**Goal:** list the practical downsides in one scene.

Use `_reveal_rows` with icons:

| Icon | Point |
|---|---|
| `ICON_DATABASE` | The coordinator is a database too, and its log is critical state |
| `ICON_DANGER` | Not replicated → single point of failure |
| `ICON_SERVER` | App servers that embed a coordinator stop being stateless |
| `ICON_STOPWATCH` | Extra fsyncs + round trips. MySQL distributed tx reported **>10× slower** |
| `ICON_BOMB` | One participant down → the whole transaction fails. It **amplifies failures** |

Footer: *XA / JTA is the standard API for this across Postgres, MySQL, ActiveMQ …*, which links back to the JMS lab.

---

## Part 3 — Saga

### Scene 12: `scene_saga_intro`

**Goal:** show the idea with a steps + compensations table.

1. Put the service row back. Each service now commits **its own local transaction** right away.
2. An orchestrator (TEAL, the booking service) sits on top with a `saga_log` `_code_box`.
3. `make_comparison_table`:

| Step | Service | Action | Compensation |
|---|---|---|---|
| 1 | Booking | `INSERT booking PENDING` | set `CANCELLED` |
| 2 | Payment | charge $120 | refund, set `REFUNDED` |
| 3 | Accounting | ledger `REVENUE` | ledger `REVERSAL` |
| 4 | Booking | set `CONFIRMED` | none, this is the end |

Caption (p. 355): *a compensation is a **new** transaction, not a rollback.*

### Scene 13: `scene_saga_happy_path`

- The orchestrator sends step 1 → a row appears in the booking mini table (PENDING, yellow).
- Step 2 → a payment row appears (CHARGED).
- Step 3 → a ledger row appears (REVENUE).
- Step 4 → the booking row turns CONFIRMED (green).
- Each step appends to `saga_log`: `bk-7f2 step 1 done`, and so on.
- Contrast with 2PC: the rows appear **one by one**, not together, and no lock bars span the whole flow.

### Scene 14: `scene_saga_failures`

**Beat A: payment fails**
- Steps: 1 ✓, 2 ✗ (`balance 50 < 120`).
- A backward arrow (RED, dashed) runs from the orchestrator to Booking: compensation → `CANCELLED`.
- Final tables: booking CANCELLED, no payment, no ledger row.

**Beat B: accounting is down**
- Steps: 1 ✓, 2 ✓, 3 ✗ (accounting card greyed out with `ICON_DANGER`, *unreachable*).
- Two backward arrows run in reverse order: refund payment, then cancel booking.
- Caption: *undo in reverse order.*

### Scene 15: `scene_saga_crash_and_retry`

**Beat A: the orchestrator crashes**
- After step 2 the orchestrator gets `ICON_BOMB`.
- It restarts, reads `saga_log` (`step 2 done`), and continues at step 3. Caption: *the saga log is what lets us resume.*

**Beat B: duplicate message**
- The step 2 message arrives twice (two arrows, the second slightly offset).
- The second one hits `booking_id UNIQUE` and bounces back GREY. Log: `PAYMENT  already charged, no-op`.
- Caption: *every step and every compensation must be idempotent.* This links back to the **Idempotent Receiver** in sheet 6.

### Scene 16: `scene_saga_no_isolation`

**Goal:** show the anomaly and its countermeasure.

1. Freeze mid-saga after step 3.
2. A "reader" (a reporting query, `ICON_CHART`) looks at the tables and sees a **PENDING** booking and a **REVENUE** row. Its report says *+$120 today*.
3. Then step 4 fails and compensations run: a **REVERSAL** row appears. The report is now wrong. Flash it RED.
4. Caption: *Saga = ACD, no I.* Other readers see the middle.
5. **Countermeasure: semantic lock.** A second user tries to book room 101 while the first booking is PENDING. The exclusion constraint (`status <> 'CANCELLED'`) rejects it. Caption: *PENDING acts as our lock.*

### Scene 17: `scene_saga_orchestration_vs_choreography`

Two panels side by side:

- **Orchestration**: the orchestrator in the middle with arrows out to each service. Label: *the Process Manager pattern (sheet 6)*.
- **Choreography**: no center. The services publish and consume events on a Kafka topic strip (`ICON_KAFKA` from `section_7/project_weather_stations.py`) (`booking.created → payment.charged → ledger.recorded`). Label: *events over Kafka (lab 4)*.

A small comparison under them:

| | Orchestration | Choreography |
|---|---|---|
| Where the flow lives | one place | spread across services |
| Easy to follow | yes | harder as steps grow |
| Coupling | services know the orchestrator | services only know events |

Footer: failed messages that can't be retried go to a **Dead Letter Channel** (sheet 6).

---

## Part 4 — Distributed Locks (p. 301–304)

### Scene 18: `scene_lock_without_fencing`

**Goal:** recreate Figure 8-4 with our booking service.

**Setup:** two booking service instances, **A** and **B** (both BLUE, labeled), a **lock service** (YELLOW), and **storage** (`booking_db`, the `rooms` row for 101 with `booked_by = ∅`).

Why a lock here: *imagine the resource can't protect itself, like a file or an external system.* The `rooms.booked_by` column plays that role.

**Sequence rows** (top → bottom): A, Lock service, B, Storage. Same layout as Figure 8-4.

| # | Event |
|---|---|
| 1 | A → lock: `acquire room:101` → **ok, lease 5s** (a lease bar starts draining next to A) |
| 2 | A's icon freezes: greyed, a snowflake or pause glyph, label **GC pause** |
| 3 | The lease bar drains to 0 → *lease expired* |
| 4 | B → lock: `acquire room:101` → **ok** |
| 5 | B → storage: `booked_by = B` ✓ (and B's user was charged) |
| 6 | A unfreezes, still thinks it holds the lock. Thought bubble: *"I still have the lock"* |
| 7 | A → storage: `booked_by = A` ✓ (overwrites B) |

End: the `rooms` row shows `A` while B's user paid. Flash RED. Caption: **B's booking is lost.**

Caption (p. 302): *a node can't trust its own sense of time. The lease expired while it was paused.*

### Scene 19: `scene_lock_with_fencing`

**Goal:** recreate Figure 8-5.

Replay Scene 18 with one change: every grant comes with a **fencing token** that only ever goes up.

| # | Event |
|---|---|
| 1 | A acquires → **token 33** |
| 2 | GC pause, lease expires |
| 3 | B acquires → **token 34** |
| 4 | B writes with 34. Storage remembers `fence_token = 34` ✓ |
| 5 | A wakes and writes with 33. Storage sees `33 < 34` → **rejected** ✗ |

Show the storage-side check as a `make_code_text` box next to the storage icon:

```sql
UPDATE rooms
   SET booked_by = :who, fence_token = :t
 WHERE room_id = 101 AND fence_token < :t
```

Result chips: `B → 1 row` (GREEN), `A → 0 rows` (RED).

Two closing cards:
1. **The check lives in the storage, not the client.** A honestly believes it has the lock.
2. **Where tokens come from:** Redis `INCR` is enough for the demo. In real systems use ZooKeeper (`zxid`) or etcd (revision), which are linearizable and fault tolerant.

Footnote line (p. 304): fencing protects against **mistaken** nodes, not **lying** ones (Byzantine faults are out of scope).

---

## Part 5 — Wrap Up

### Scene 20: `scene_compare`

A `make_comparison_table`:

| | 2PC | Saga |
|---|---|---|
| Atomicity | all or nothing | eventually, via compensations |
| Isolation | yes, readers wait | none, readers see the middle |
| Locks | held until the coordinator decides | only inside each local step |
| One node down | everything blocks | that step retries or compensates |
| Pick it when | few nodes, one team, short transactions | many services, long flows |

Glow each column header in turn: TEAL for 2PC, ORANGE for Saga.

### Scene 21: `scene_closing`

Three takeaway cards, revealed one by one:
1. **Keep it in one database if you can.** Constraints beat protocols.
2. **2PC gives you atomicity and costs you availability.**
3. **Sagas give you availability and cost you isolation.** Design your compensations and idempotency up front.

Footer: the DDIA page ranges and the video link from the Overview.

---

## Build Notes

- Order of `construct()` follows the scene numbers above.
- Copy the class header from sheet 4: `max_duration_before_split_reverse = 8.0` (avoids PyAV malloc failures on long renders).
- Use `self._next_slide(phase=True)` between beats inside a scene and `self._next_slide()` at the end, like the weather project.
- Sequence scenes (7–10, 18–19) share one row builder. Promote sheet 4's inner `_row` / `_arr` / `_msg` to private methods of this class so every scene can use them. Keep them in this file, not in `libs/`.
- Keep each scene under ~1 minute of animation. Use `_next_slide()` between beats so the TA controls the pace live.
- Render check: `manim-slides render ddia/section_9/distributed_transactions.py DistributedTransactions` then `manim-slides DistributedTransactions`.
