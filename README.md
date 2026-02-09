# Agent Framework Hello World

This repository is a practical learning project to explore modern agentic frameworks by implementing the same small, non-trivial “hello world” agent across multiple ecosystems.

The goal is not to build a useful product, but to gain hands-on understanding of how different frameworks model agents, control flow, state, tool usage, and iteration. By keeping the use case intentionally simple and consistent, the focus stays on architectural trade-offs rather than domain complexity.

## What “hello world” means here

In this project, a “hello world” agent is not a single prompt or a static chain. Each implementation must include at least a minimal agent loop with decision-making and tool usage.

The baseline agent:
- attempts to solve a small constrained task,
- validates its own output using a deterministic tool,
- reflects and retries when validation fails,
- stops when the task succeeds or a maximum number of attempts is reached.

This pattern is deliberately chosen because it is simple to reason about while still surfacing meaningful differences between frameworks.

## Scope and non-goals

This repository is about learning, comparison, and experimentation. Performance optimization, production hardening, and UX polish are explicitly out of scope. Frameworks are used mostly “as intended” rather than pushed into extreme or contrived designs.

Multi-agent architectures, evaluation harnesses, and more complex behaviors may be explored later, but the initial focus is on a single reflective agent implemented multiple times.

## Frameworks explored

The same agent behavior will be implemented independently using the following frameworks:

- LangChain and LangGraph  
- Google Agent Development Kit (ADK)  
- Anthropic Agent SDK  
- CrewAI  
- LlamaIndex Agents  

Each implementation lives side-by-side and follows the same conceptual specification, even if the underlying abstractions differ.

## Structure

## Why this exists
