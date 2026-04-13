# Lab 2: Microservices & Data Models

## Overview

This lab builds on a provided Spring Boot microservices application
([github.com/yigiterinc/spring-boot-microservices](https://github.com/yigiterinc/spring-boot-microservices))
and extends it in three main ways, finishing with JMeter performance testing.

---

## Starting Architecture

The app consists of three Spring Boot services:

| Service | Responsibility |
|---|---|
| **Catalog Service** | Aggregates movie info + ratings for a user |
| **Movie Info Service** | Fetches movie metadata from The Movie DB (external API) |
| **Ratings Service** | Stores and retrieves user ratings (currently in-memory) |

---

## Step 1: Ratings → MySQL

Replace the in-memory `ArrayList<Rating>` inside the Ratings Service with a
**MySQL relational database**.

- Create a `ratings` table with at least `movieId` and `rating` columns.
- Update the Spring Boot service to use Spring Data JPA / JDBC.
- Verify that ratings persist across application restarts.

**Discussion questions:**

- What is the correct data model for ratings?
- What indexes would you add and why?

---

## Step 2: Cache MovieDB → MongoDB

The Movie Info Service calls the external MovieDB API on every request.
Add a **MongoDB document cache** to avoid redundant network calls.

- On a cache miss: fetch from MovieDB, persist to MongoDB.
- On a cache hit: return the cached document directly.
- Test with a dataset of 10 million movie records (provided).

**Goal:** Measure and compare P90 latency **before** and **after** introducing the cache.

---

## Step 3: gRPC Trending Movies Service

Add a brand-new microservice called the **Trending Movies Service** that exposes
a gRPC API.

- Define a `.proto` file with a `TrendingResponse` message and a
  `getTrendingMovies` RPC.
- The service queries the Ratings DB to find the top-N most-rated movies.
- The Catalog Service calls this service via gRPC instead of REST.

**Why gRPC?**

- Binary serialization (Protobuf) — smaller payloads
- HTTP/2 transport — multiplexed, lower latency
- Strongly typed schema — `.proto` file as contract

---

## Step 4: JMeter Performance Testing

Use **Apache JMeter** to measure performance before and after each change.

### Thread Group Settings (Performance Test)

- Threads: 100
- Ramp-up: 30 seconds
- Loop count: 10

### Thread Group Settings (Stress Test)

- Threads: 500 (or until breaking point)
- Ramp-up: gradual
- Loop count: until failure

### Metrics to collect

- **Median latency** (ms)
- **P90 latency** (ms) — 90th percentile response time
- **Throughput** (requests/second)

### What to test

1. Baseline: Ratings in memory, no MongoDB cache
2. After MySQL migration
3. After adding MongoDB cache (most significant change)
4. After adding gRPC Trending service

---

## Deliverables

1. MySQL schema — `CREATE TABLE` DDL for ratings
2. MongoDB schema — collection structure and index definitions
3. JMeter P90 latency and throughput — before vs after caching (charts)
4. JMeter test plans — `.jmx` files for both performance and stress tests
5. Running application — all three services + the new Trending service
6. Final report — answer all discussion questions, include measurements

---

## Schema Evolution (Protobuf Reference)

When evolving a `.proto` file, follow these rules to maintain compatibility:

| Change | Safe? | Rule |
|---|---|---|
| **Add a field** | ✓ Yes | Old readers skip unknown fields |
| **Remove a field** | ✓ Yes (v) | Mark tag as `reserved` — never reuse! |
| **Reuse a tag number** | ✗ No | Causes binary deserialization errors |
| **Change a field type** | ⚠ Sometimes | Only safe casts (e.g., `int32` → `int64`) |

**Key insight:** Tag numbers are forever. Never reassign them.

---

## Key Technologies

| Technology | Role |
|---|---|
| **MySQL** | Relational persistence for ratings |
| **MongoDB** | Document cache for movie metadata |
| **gRPC** | Binary RPC protocol for Trending service |
| **Protobuf** | Schema definition and serialization format |
| **JMeter** | Performance and stress testing tool |
| **Spring Boot** | Java microservices framework |

---

## Ratings ID Strategy Follow-Up

A follow-up note comparing auto-increment IDs vs composite keys vs UUID for the
Ratings Service schema is available here:

- [Lab 2 ID follow-up](../../section_3/docs/lab-2-id-follow-up.md)
