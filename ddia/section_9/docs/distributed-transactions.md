# Section 9: Distributed Transactions — Scene Script

## Overview

A Manim slide deck that follows one booking of **room 101** through three services (Booking, Payment, Accounting) and shows how we keep them consistent: first inside one database, then with **2PC**, then with a **Saga**, and finally with a **distributed lock + fencing token**.

Every "log line" and "table row" on screen is an animated mobject, but each one mirrors the live demo in `~/TA/DDIA/distributed-transactions-demo` (Spring Boot services on one MySQL server). Scenes that have a matching script show a `demo/0X-….sh` tag under the header, so the class can run the same thing right after the slide.

**Demo facts the deck follows**

| Topic | In the demo |
|---|---|
| Databases | MySQL, one server, `bookingdb`, `paymentdb`, `accountingdb` |
| 2PC | MySQL XA: `XA START · XA END · XA PREPARE · XA COMMIT / XA ROLLBACK`, `XA RECOVER`. The coordinator is `booking-service`, its log is `bookingdb.tx_log` (`PREPARING`, `COMMIT`, `ABORT`) |
| Transaction ids | 2PC `bk-xxxxxxxx`, saga `sg-xxxxxxxx`, stored in every row's `transaction_id` |
| Lock service | the `lock_lease` table, `token = token + 1` on every grant, never reset by expiry |
| Users | user 1 has 500.00, user 2 has 50.00 (the real NO vote) |

| Script | Scene(s) |
|---|---|
| `01-write-skew.sh` | 3 |
| `02-materialized.sh` | 4b |
| `03-serializable.sh` | 4 (the SERIALIZABLE row) |
| `04-fencing.sh` | 19 |
| `05-2pc.sh` | 7, 8 |
| `06-2pc-in-doubt.sh` | 9, 10 |
| `07-saga.sh` | 12–15 |

**Sources**

| Topic | DDIA pages |
|---|---|
| Write skew, booking example, phantoms, materializing conflicts | 249–251 |
| Two-phase locking (2PL), one slide: 2PL ≠ 2PC | 257 |
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
| Booking service + `bookingdb` | `BLUE` | `ICON_SERVER` + `ICON_DATABASE` |
| Payment service + `paymentdb` | `ORANGE` | `ICON_SERVER` + `ICON_DATABASE` |
| Accounting service + `accountingdb` | `PURPLE` | `ICON_SERVER` + `ICON_DATABASE` |
| Coordinator / orchestrator | `TEAL` | `ICON_STRUCTURE` |
| Lock service (`lock_lease` table) | `YELLOW` | `ICON_LOCK` |
| Success / commit | `GREEN` | `ICON_CHECK` |
| Failure / abort / conflict | `RED` | `ICON_DANGER` |
| Crash | `RED` | `ICON_BOMB` |
| Waiting / blocked / lease | `GREY_B` | `ICON_STOPWATCH` |
| User | `GREY_A` | `make_user_icon` |

**Recurring layouts**

- **Tables**: `_table` (in this file), not `make_comparison_table`. Each row is one monospaced line with columns padded to a fixed width, so columns are left-aligned and every cell sits on the same baseline.
- **Small text**: `make_label` is wrapped to render at 4× size and scale down. Pango spreads letters too far apart at small sizes, which made labels look flat and stretched.

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

**Goal:** show the schema from `demo/sql/00-schema.sql` once, so later scenes can point at it.

Subtitle: *MySQL · one server · three databases*. Three schema cards side by side, one row per column, tags right-aligned:

```
bookingdb
  rooms     room_id PK · name · fence_token (dimmed)
  bookings  id PK · room_id, user_id · starts_at, ends_at
            status ∈ PENDING · CONFIRMED · CANCELLED
            transaction_id (bk- / sg-) · fence_token (dimmed)
  + room_slot_lock · lock_lease · tx_log · saga_log
```

```
paymentdb
  wallets   user_id PK · balance CHECK (balance >= 0)
  payments  id PK · booking_id UNIQUE · transaction_id · user_id, amount
            status ∈ CHARGED · REFUNDED
```

```
accountingdb
  ledger    id PK · booking_id · transaction_id · amount
            kind ∈ REVENUE · REVERSAL
            UNIQUE (booking_id, kind) · append only
```

Then highlight, each with a chip under its card:

| Highlight | Caption |
|---|---|
| `CHECK >= 0` | Payment can say **no** |
| `booking_id UNIQUE` | a retry is a no-op |
| `append only` | undo = add a REVERSAL |
| `transaction_id` | every row carries the global tx id |

`fence_token` and the support tables are dimmed: *later*.

### Scene 2b: `scene_prerequisites`

**Goal:** a quick ACID recap before anything breaks.

Four icon cards, one per letter:
- **Atomicity**: all the writes happen, or none of them. This is what we fight for across services.
- **Consistency**: the rules hold before and after, like `CHECK (balance >= 0)`.
- **Isolation**: two transactions running at once don't see each other's half-done work.
- **Durability**: once `COMMIT` returns, the data survives a crash (the write-ahead log).

Roadmap chips: *Isolation on one database* · *Atomicity across three databases* · *Locks across machines*.

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
4. MySQL caveat (yellow note): at REPEATABLE READ, InnoDB's `FOR UPDATE` also locks the index gap (a next-key lock), so on MySQL it does block the phantom. That is the same mechanism `SERIALIZABLE` uses in `03-serializable.sh`.

Then a `make_comparison_table` with three fixes:

| Fix | Idea | Note |
|---|---|---|
| Materialize the conflict | lock `room_slot_lock` rows first | `02-materialized.sh`, last resort |
| `SERIALIZABLE` | InnoDB locks the gap, one aborts, retry | `03-serializable.sh` (glowing row) |
| Exclusion constraint | the DB rejects overlapping ranges | Postgres only, MySQL has none |

Glow the last row.

### Scene 4b: `scene_materialize_conflicts`

**Goal:** expand the first fix from Scene 4 (p. 251), exactly as `02-materialized.sh` runs it.

1. A `room_slot_lock` grid for room 101, one cell per 15 minutes from 11:00 to 13:45. Caption: *seeded for today and tomorrow (192 rows per room), it stores nothing*.
2. T1 runs `SELECT slot_start FROM room_slot_lock WHERE room_id = 101 AND slot_start >= '12:00' AND slot_start < '13:00' ORDER BY slot_start FOR UPDATE`. Four cells turn blue with lock icons.
3. T2 is the same request at the same moment (the script fires both at once). An orange frame covers the same four cells, the 12:00 cell flashes RED: *T2 waits on the 12:00 row, ORDER BY keeps everyone in the same order*.
4. T1 checks bookings, INSERTs, commits, and releases its locks. T2 takes the slot rows, checks bookings, sees T1's row, and answers *room already booked*. One row in `bookings`. Footnote: *InnoDB takes T2's snapshot at its first plain SELECT, after the wait, so the check sees T1's row.*
5. The catch, as three cards:
   - lock size: one row per room serializes every booking of that room, the demo's 15-minute slots are 96 rows per room per day
   - concurrency leaks into the data model
   - hard to get right, so it's a last resort. Prefer `SERIALIZABLE` (`03-serializable.sh`), or in Postgres an exclusion constraint.

### Scene 5: `scene_two_phase_locking`

**Goal:** one slide. 2PL is DDIA p.257, isolation on one database, not a distributed transaction topic. We only keep two facts from it.

1. Header: **2PL ≠ 2PC**.
2. Two cards:
   - **2PL: two-phase locking (p.257):** isolation on one database. Take locks while the transaction runs, release them all at COMMIT. SERIALIZABLE in InnoDB works this way.
   - **2PC: two-phase commit (p.354):** atomic commit across many databases. Prepare everywhere, then commit everywhere. That is the rest of the deck.
3. Closing line: **Locks are held until commit.** Hint: *it comes back when the 2PC coordinator crashes* (Scene 9, DDIA p.362).

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
4. **Now split it:** `hotel_db` splits into `bookingdb`, `paymentdb` and `accountingdb`, each with its own log ending in `COMMIT ?`. Badge: *three disks, three commit records, which one is the commit point?* Then three lines: each database can only commit its own part · one can say yes while another says no or crashes · nobody is in charge of the final answer. That leads straight into Scene 6.

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

**Goal:** recreate Figure 9-9 with the demo's `Coordinator`. Tag: `05-2pc.sh`.

**Sequence rows** (top → bottom): Coordinator, bookingdb, paymentdb, accountingdb. The log panel sits underneath, full width.

| # | Message | Log line |
|---|---|---|
| 1 | | `COORD  bk-7f2 begin, room 101 for user 1, amount 120.00` |
| 2 | | `COORD  tx_log bk-7f2 = PREPARING` |
| 3 | coord → booking: prepare, booking → coord: YES | `BOOKING  XA START · INSERT booking CONFIRMED · XA END · XA PREPARE → YES` |
| 4 | coord → payment: prepare, payment → coord: YES | `PAYMENT  XA START · INSERT payment · wallet -120.00 · XA PREPARE → YES` |
| 5 | coord → accounting: prepare, accounting → coord: YES | `ACCOUNT  XA START · ledger REVENUE 120.00 · XA PREPARE → YES` |
| 6 | coord writes the decision | `COORD  tx_log bk-7f2 = COMMIT, the decision is on disk` |
| 7 | coord → all: `XA COMMIT` | `ALL  XA COMMIT 'bk-7f2' … locks released` |

- Participants are asked **one at a time**, as in `Coordinator.collectVotes`. Each one does its writes inside the prepare call.
- Each participant's **lock bar** starts when it writes and stretches with time until `XA COMMIT`.
- At step 6, glow the coordinator's disk icon. Label: **commit point**.

Then two "points of no return" cards (p. 358):
1. A participant that votes **yes** gives up the right to abort.
2. Once the coordinator decides, that decision is final. It retries forever.

Optional light touch: the book's wedding analogy as one line, *"I do" = yes vote, minister = coordinator*.

### Scene 8: `scene_2pc_vote_no`

**Goal:** show how an abort goes, as in run 2 of `05-2pc.sh`.

- `bk-8a1`, room 102, user 2 (balance 50.00), amount 120.00. `tx_log = PREPARING`.
- Booking votes YES.
- Payment's debit fails `chk_balance_non_negative`, it rolls back its own branch and votes **NO**. Its lock bar ends there.
- Accounting gets a grey *never asked* chip: the coordinator stops at the first NO.
- `tx_log bk-8a1 = ABORT`, then `XA ROLLBACK` goes to booking only, the one branch still prepared.
- Result badge: *nothing for room 102 anywhere ✓*.

### Scene 9: `scene_2pc_coordinator_crash`

**Goal:** recreate Figure 9-10 the way `06-2pc-in-doubt.sh` does it.

1. Chip: `fail-mode = CRASH_AFTER_VOTES`. `tx_log bk-9c4 = PREPARING`, then all three prepare and vote YES, one at a time.
2. The coordinator gets an `ICON_BOMB` (log: *everyone voted yes and I am walking away*). No decision is written.
3. Each participant gets an **IN DOUBT** chip, and a stopwatch counts up while the lock bars keep growing. Log: `XA RECOVER lists bk-9c4 for booking, payment and accounting`.
4. An unrelated session runs `UPDATE wallets SET balance = balance WHERE user_id = 1` with `innodb_lock_wait_timeout = 5`. Its arrow stops at payment's lock bar. Log: `ERROR 1205 after 5s: Lock wait timeout exceeded`.
5. Beat: restart paymentdb. The chip still says **IN DOUBT**: *after a restart XA RECOVER still lists bk-9c4, the locks are still held* (p. 363).

Callback: bring back the Scene 5 line *Locks are held until commit.*, now with the extra line *… and commit is waiting on a dead coordinator.*

### Scene 10: `scene_2pc_recovery`

**Goal:** show `POST /admin/recover`, and how the escape hatch breaks things.

**Beat A: recovery** (`Coordinator.recover` reads `tx_log`)
- Case 1: `tx_log bk-9c4 = PREPARING`, so no decision was ever written → recover as **ABORT**, `XA ROLLBACK` to all. The blocked `UPDATE wallets` now finishes in milliseconds.
- Case 2 (`fail-mode = COMMIT_LOST_TO_PAYMENT`): `tx_log bk-7f2 = COMMIT`, booking and accounting committed, but the commit message to payment was lost. Pause on the in-between state: booking CONFIRMED and ledger REVENUE are visible, payment is still IN DOUBT. Caption: *atomic commit, but not atomic visibility.* Then recover sends `XA COMMIT` to payment. Branches that already finished answer `XAER_NOTA`, which the code skips.

**Beat B: heuristic decision** (not a script, but it can be typed into `mysql`)
- An admin runs `XA ROLLBACK 'bk-7f2','payment'` by hand.
- The coordinator later sends `XA COMMIT` and payment answers `XAER_NOTA`. The code treats that as already done, so nobody notices.
- End state: booking CONFIRMED, ledger REVENUE, **no payment**. Everything flashes RED.
- Caption (p. 363): *"heuristic" is a polite word for "probably broke atomicity". The coordinator never notices.*

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

Footer: *XA / JTA is the standard API for this across Postgres, MySQL, ActiveMQ …*

---

## Part 3 — Saga

### Scene 12: `scene_saga_intro`

**Goal:** show the idea with a steps + compensations table, using `SagaOrchestrator`'s step names. Tag: `07-saga.sh`.

1. Put the service row back. Each service now commits **its own local transaction** right away.
2. An orchestrator (TEAL, the booking service) sits on top with a `saga_log` panel (one row per step, saga ids look like `sg-xxxxxxxx`).
3. `make_comparison_table`:

| Step | Service | Action | Compensation |
|---|---|---|---|
| 1 reserve | Booking | lock slots, `INSERT booking PENDING` | set `CANCELLED` |
| 2 charge | Payment | `INSERT payment`, wallet -120 | refund, set `REFUNDED` |
| 3 ledger | Accounting | ledger `REVENUE` | ledger `REVERSAL` |
| 4 confirm | Booking | set `CONFIRMED` | none, this is the end |

Caption (p. 355): *a compensation is a **new** transaction, not a rollback.*

### Scene 13: `scene_saga_happy_path`

- Run 1 of `07-saga.sh`. Step 1 → `booking 1 PENDING` (yellow). Step 2 → `booking 1 CHARGED 120.00`. Step 3 → `booking 1 REVENUE 120.00`. Step 4 → the booking row turns CONFIRMED (green).
- Each step adds a `saga_log` line: `1 reserve DONE`, `2 charge DONE`, …
- Contrast with 2PC: the rows appear **one by one**, not together, and no lock bars span the whole flow.

### Scene 14: `scene_saga_failures`

**Beat A: payment fails** (user 2, not in the script, but the code handles it)
- Steps: 1 ✓, 2 ✗ (*user 2: CHECK, 50 < 120*). `saga_log`: `2 charge FAILED`.
- A dashed RED arrow from the orchestrator to Booking: `1 reserve COMPENSATED` → `CANCELLED`.
- Final: booking CANCELLED, no payment, no ledger row.

**Beat B: step 3 fails** (run 2 of `07-saga.sh`, `failAt=3`)
- Steps: 1 ✓, 2 ✓, 3 ✗ (*failAt=3, failing on purpose*).
- Two dashed arrows in reverse order: `2 charge COMPENSATED` (REFUNDED), then `1 reserve COMPENSATED` (CANCELLED).
- Caption: *undo in reverse order. The refund is a new state, not a deleted row.*

### Scene 15: `scene_saga_crash_and_retry`

**Beat A: the orchestrator is killed** (run 3, `killAt=2`, amount 50.00)
- After step 2 the orchestrator gets `ICON_BOMB`. `saga_log`: *dies, nothing compensated*. Caption: *the middle state, booking PENDING and the money already gone. 2PC never shows this.*
- `POST /saga/{id}/resume` reads `saga_log` (last DONE is step 2) and carries on with step 3 and step 4.

**Beat B: duplicate message** (run 4)
- The same charge is sent again. `INSERT IGNORE` hits `booking_id UNIQUE`, it bounces back GREY. Log: `payment  already charged, no-op`, and the balance does not change.
- Caption: *every step and every compensation must be idempotent.*

### Scene 16: `scene_saga_no_isolation`

**Goal:** show the anomaly and its countermeasure.

1. Freeze mid-saga after step 3.
2. A "reader" (a reporting query, `ICON_CHART`) sees a **PENDING** booking and a **REVENUE** row. Its report says *+$120 today*.
3. Then step 4 fails (`failAt=4`) and compensations run: a **REVERSAL** row appears, the payment is REFUNDED, the booking CANCELLED. The report is now wrong. Flash it RED.
4. Caption: *Saga = ACD, no I.* Other readers see the middle.
5. **Countermeasure: semantic lock.** Bob tries to book room 101 while the first booking is PENDING and gets *room already booked*. Show the overlap check from step 1 reserve:

```sql
SELECT COUNT(*) FROM bookings
 WHERE room_id = 101 AND status <> 'CANCELLED'
   AND starts_at < :end AND ends_at > :start
```

Caption: *status <> 'CANCELLED' counts PENDING, so PENDING acts as our lock.*

### Scene 17: `scene_saga_orchestration_vs_choreography`

Two panels side by side:

- **Orchestration**: the orchestrator in the middle with arrows out to each service. Label: *the Process Manager pattern · what the demo uses*.
- **Choreography**: no center. The services publish and consume events on a Kafka topic strip (`ICON_KAFKA` from `section_7/project_weather_stations.py`) (`booking.created → payment.charged → ledger.recorded`). Label: *events over Kafka*.

A small comparison under them:

| | Orchestration | Choreography |
|---|---|---|
| Where the flow lives | one place | spread across services |
| Easy to follow | yes | harder as steps grow |
| Coupling | services know the orchestrator | services only know events |

Footer: failed messages that can't be retried go to a **Dead Letter Channel**.

---

## Part 4 — Distributed Locks (p. 301–304)

### Scene 18: `scene_lock_without_fencing`

**Goal:** recreate Figure 8-4 with the demo's lock.

**Sequence rows** (top → bottom): client 1, `lock_lease`, client 2, bookingdb. Subtitle: *without the token check, the write is a plain INSERT, nothing in bookings stops a second one.*

| # | Event |
|---|---|
| 1 | client 1 → lock_lease: `acquire room:101` → **ok, lease 3s** (the lease bar grows with time) |
| 2 | client 1 greys out: **5s pause** |
| 3 | the lease bar turns RED → *expired* |
| 4 | client 2 → lock_lease: `acquire room:101` → **ok** |
| 5 | client 2 → bookingdb: `INSERT booking` → *booking for user 2* |
| 6 | client 1 wakes up, still thinks it holds the lock: *"I still have the lock"* |
| 7 | client 1 → bookingdb: `INSERT booking` → *booking for user 1* |

End: badge *Room 101 booked twice for 15:00–16:00 ✗*. Caption (p. 302): *a node can't trust its own sense of time. The lease expired while it was paused.*

### Scene 19: `scene_lock_with_fencing`

**Goal:** recreate Figure 8-5, as `04-fencing.sh` runs it.

| # | Event |
|---|---|
| 1 | client 1 acquires → **token 1**, 3s lease |
| 2 | 5s pause, the lease expires |
| 3 | client 2 acquires → **token 2** |
| 4 | client 2 writes with token 2: `rooms.fence_token` 0 → 2, booking for user 2 ✓ |
| 5 | client 1 wakes and writes with token 1 → **stale fencing token 1** ✗ |

Show the check from `BookingRepository.acceptToken` as a `make_code_text` box:

```sql
UPDATE rooms SET fence_token = :t
 WHERE room_id = 101 AND fence_token < :t;
-- 1 row: INSERT the booking   0 rows: reject
```

Result chips: `client 2, token 2 → 1 row` (GREEN), `client 1, token 1 → 0 rows` (RED).

Two closing cards:
1. **The check lives in the storage, not the client.** Client 1 honestly believes it has the lock. Only bookingdb can say no.
2. **Tokens only ever go up:** `lock_lease` does `token = token + 1` on every grant and expiry never resets it. Real systems use ZooKeeper (`zxid`) or etcd (revision), which are linearizable and fault tolerant.

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
