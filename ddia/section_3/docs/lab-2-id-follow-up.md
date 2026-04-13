# Lab 2 Follow-Up: Ratings ID Strategy

## Context

In Step 1 of Lab 2, teams move the Ratings Service from in-memory data to MySQL. A recurring design question is:

- Should the table use an auto-increment numeric ID?
- Should it use a composite key?
- Should it use UUID?

This note compares the three options for the ratings data model.

---

## Candidate Schemas

### Option A: Auto-Increment Surrogate ID

```sql
CREATE TABLE ratings (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  movie_id VARCHAR(32) NOT NULL,
  rating TINYINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_user_movie (user_id, movie_id),
  KEY idx_movie_id (movie_id),
  KEY idx_user_id (user_id)
);
```

### Option B: Composite Primary Key

```sql
CREATE TABLE ratings (
  user_id VARCHAR(64) NOT NULL,
  movie_id VARCHAR(32) NOT NULL,
  rating TINYINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, movie_id),
  KEY idx_movie_id (movie_id)
);
```

### Option C: UUID Primary Key

```sql
CREATE TABLE ratings (
  id CHAR(36) PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  movie_id VARCHAR(32) NOT NULL,
  rating TINYINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_user_movie (user_id, movie_id),
  KEY idx_movie_id (movie_id),
  KEY idx_user_id (user_id)
);
```

---

## Comparison

| Criterion | Auto-Increment ID | Composite PK (`user_id`, `movie_id`) | UUID ID |
|---|---|---|---|
| Enforces one-rating-per-user-per-movie | Only with extra unique index | Yes, by primary key | Only with extra unique index |
| Read path for `getUserRating(user, movie)` | 2-index strategy (`uq_user_movie`) | Direct PK lookup | 2-index strategy (`uq_user_movie`) |
| Read path for `getAllRatings(movie)` | Needs `idx_movie_id` | Needs secondary index on `movie_id` | Needs `idx_movie_id` |
| Insert/write complexity | Low | Low | Moderate (UUID generation) |
| Storage efficiency | Best (small PK) | Good (wider PK) | Worst (largest PK) |
| Join friendliness | Very good | Moderate | Good |
| Migration/distributed friendliness | Tied to DB sequence behavior | Good | Best across distributed writers |
| Human readability/debugging | Best | Good | Lowest |

---

## Recommended Model For This Lab

For the Ratings Service semantics, each user should have at most one rating per movie. Because that uniqueness is the core business rule, the cleanest model is:

- **Primary key:** `(user_id, movie_id)`
- **Secondary index:** `movie_id` (to support top-N and aggregation queries)

Use this when the table is treated as a fact table keyed by domain identity.

If teams prefer a surrogate key for ORM convenience, keep `id` but still enforce:

```sql
UNIQUE KEY uq_user_movie (user_id, movie_id)
```

Without that unique constraint, duplicates become possible and trending/top-rated calculations can be corrupted.

---

## Practical Guidance

1. If your API updates ratings with `upsert` by `(user, movie)`, composite PK is usually the simplest and safest.
2. If your architecture requires globally unique identifiers generated outside MySQL, UUID is valid, but keep `(user_id, movie_id)` unique.
3. If you use auto-increment ID, treat it as a technical surrogate only, not business identity.

---

## Suggested Discussion Answer (Short Form)

- **Auto-increment ID**: simple and compact, but does not encode domain uniqueness by itself.
- **Composite key**: best matches the rating domain rule (one user, one movie, one rating).
- **UUID**: useful in distributed systems and offline ID generation, but larger and less efficient for indexing.

For Lab 2, **composite primary key (`user_id`, `movie_id`) is the most semantically correct default**.
