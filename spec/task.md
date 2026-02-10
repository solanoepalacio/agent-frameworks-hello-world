# Character Appearance Count — Task Specification

## Purpose

This task is a **hello‑world benchmark for agent frameworks**. It is intentionally simple, deterministic, and rigidly specified. The goal is *not* to test deep language understanding, but to test whether an agent (or a system of agents) can:

* Read multiple input files
* Parse a strictly defined text format
* Aggregate information across files
* Produce a structured JSON output
* Be validated automatically against ground‑truth

## High‑level Description

The agent is given a set of conversation transcripts written as short theater‑style plays. Each transcript contains messages exchanged between **2 to 4 participants**, chosen from a fixed but *implicit* pool of participants.

The agent’s task is to **count how many times each participant appears** across *all* conversations.

An appearance is defined as:

> A participant having at least one spoken message in a given conversation file. Multiple messages by the same participant in the same file count as a single appearance.

The expected result is compared against a **ground‑truth file** provided by the task author.

---

## Directory Structure

```
spec/cca/
├── task.md            # This document
├── inputs/
│   ├── 001.txt
│   ├── 002.txt
│   ├── ...
│   └── N.txt
└── ground-truth.json        # Ground‑truth counts
```

---

## Inputs

### Conversation Files

* Located in: `spec/cca/inputs/`
* Each file represents **one conversation**
* Each conversation contains:

  * Between **2 and 4 participants**
  * Approximately **100 messages** total
* Participants are chosen from a fixed pool (size ~10), but:

  * **The list of participants is NOT provided explicitly**
  * Participants must be inferred from the conversation content

---

## Message Format Specification

See [`format.md`](format.md) for the full message format specification (grammar, constraints, and examples).

---

## Output

### Expected Agent Output

The agent MUST produce a JSON object where:

* Keys are participant identifiers (`<CHARACTER_NAME>`)
* Values are integers representing total appearances across *all* input files

Example:

```json
{
  "matt": 42,
  "rob": 58
}
```

### Ground‑Truth File

* Located at: `spec/cca/ground-truth.json`
* Contains the **correct counts**, computed manually or via a trusted process
* Used by the test harness to validate the agent’s output

The agent:

* MUST NOT read this file during development
* MUST NOT rely on it when solving the task

---

## Definition of Correctness

An agent’s solution is considered **correct** if:

* All participants appearing in the inputs are present as keys in the output
* No extra participants are included
* All counts exactly match the ground‑truth values

Ordering of keys in the JSON object is irrelevant.

---

## Non‑Goals

This task explicitly does NOT aim to test:

* Semantic understanding of dialogue
* Coreference resolution
* Implicit speakers
* Ambiguous formatting
* Robustness to malformed input

Those concerns are intentionally deferred to later tasks.
