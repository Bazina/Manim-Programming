# Lab 4: JMS vs Kafka — Lab Guide

## Overview

Message queues are ubiquitous in data-intensive applications. They enable **reactive programming** — a service submits a message for transmission and remains responsive without blocking.

Two dominant options:

| Tool | Model | Language |
|---|---|---|
| **JMS (ActiveMQ)** | Broker — point-to-point & pub/sub | Java EE standard |
| **Apache Kafka** | Partitioned Log — distributed event store | Java / Scala |

**Goal:** Act as a decision-maker for your organization. Test both tools across Performance, Usability, and Integrations — then recommend one.

---

## Setup

**Constraints:**
- Message size: fixed at **1 KB**
- Programming API: **Java only**
- Kafka: install locally; start **Zookeeper** then **Kafka broker**

---

## Requirements

### A) Performance

#### 1. Response Time
Median of **1000 runs** for both produce and consume APIs.

**JMS approach:**
```java
long start = System.currentTimeMillis();
producer.send(msg);
long elapsed = System.currentTimeMillis() - start;
```

**Kafka approach:** same pattern with `producer.send(record).get()`.

**Protocol:**
- Produce 1000 × 1 KB messages → record produce median
- Leave 1000 messages in queue → consume 1000 × 1 KB → record consume median

#### 2. Maximum Throughput
Find the highest sustainable message rate without dropped messages.

**Algorithm:**
```
for X in [exponentially increasing values]:
    period T = 1000ms / X
    for each of X requests:
        send message
        sleep(T - 0.2*T)   # compensate for thread-switch overhead
    verify: all X messages consumed
    if any failures: report X-prev as max throughput
```

Kafka provides built-in scripts:
```
kafka-producer-perf-test.sh  --topic test --num-records 10000 ...
kafka-consumer-perf-test.sh  --topic test --messages 10000 ...
```

JMS: use **JMeter** (justify thread count, ramp-up time).

#### 3. Median Latency (End-to-End)
Time from production to consumption across **10 000 messages**.

**Algorithm:**
```
consumer: actively poll all messages
producer: embed send_timestamp in message body
on consume: latency = now() - send_timestamp
report median of 10000 measurements
```

---

### B) Usability

Report for each tool:

| Metric | JMS (ActiveMQ) | Kafka |
|---|---|---|
| Setup steps | count | count |
| Time to "Hello World" | minutes | minutes |
| Lines to produce | count | count |
| Lines to consume | count | count |
| API calls per operation | count | count |

**JMS produce (minimum skeleton):**
```java
ConnectionFactory cf = new ActiveMQConnectionFactory(url);
Connection conn = cf.createConnection();
Session session = conn.createSession(false, Session.AUTO_ACKNOWLEDGE);
Topic topic = session.createTopic("myTopic");
MessageProducer producer = session.createProducer(topic);
conn.start();
producer.send(session.createTextMessage(payload));
```

**Kafka produce (minimum skeleton):**
```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer",   "...StringSerializer");
props.put("value.serializer", "...StringSerializer");
KafkaProducer<String,String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("myTopic", payload));
```

---

### C) Integrations

Research (with references) for each tool:
- Hadoop Ecosystem (HDFS, Hive, HBase)
- Columnar stores (Cassandra, ClickHouse)
- Cloud platforms (AWS, GCP, Azure)
- Connectors / plugins available out-of-the-box

---

## Deliverables

| Item | Description |
|---|---|
| Performance table | Produce RT, Consume RT, Max Throughput, Median Latency |
| Code snippets | Measurement code for each metric in both tools |
| Usability table | Setup steps, LoC, API calls per operation |
| Integrations | Research summary with references |
| Summary | Advantages & Disadvantages per tool |
| Conclusion | Recommendation with justification |

---

## Notes

- Work in groups of four
- All members must be ready to answer questions in the discussion
- ChatGPT / LLMs allowed — but you must understand and justify the output
- Copying from other teams → severe penalty

---

## Key Concepts Reference

| Term | Definition |
|---|---|
| **JMS** | Java Message Service — Java EE API for asynchronous messaging |
| **ActiveMQ** | Open-source JMS broker (Apache) |
| **Kafka** | Distributed partitioned log — high-throughput event streaming |
| **Broker model** | Central router receives, queues, and delivers messages |
| **Partitioned log** | Append-only ordered log; consumers track own offset |
| **Response time** | Duration of a single API call (produce or consume) |
| **Throughput** | Messages per second sustained without loss |
| **Median latency** | 50th percentile of end-to-end produce→consume delay |
| **JMeter** | Load-testing tool; useful for JMS throughput testing |
