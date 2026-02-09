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

Multi-agent architectures, evaluation harnesses, and more complex behaviors will be explored later, but the initial focus is on a single reflective agent implemented multiple times.

## Frameworks explored

The same agent behavior will be implemented independently using the following frameworks:

- LangChain
- LangGraph  
- Google Agent Development Kit (ADK)  
- Anthropic Agent SDK  
- CrewAI  
- LlamaIndex Agents  

Each implementation lives side-by-side and follows the same conceptual specification, even if the underlying abstractions differ.

## Structure

```
agentic-architectures/
├── spec/              # Task specification + input generator
│   ├── task.md        # Language-agnostic task spec
│   ├── format.md      # Message format spec (used in LLM prompts)
│   ├── generate.py    # Conversation transcript generator
│   ├── requirements.txt
│   └── inputs/        # Generated conversation files
├── langchain/         # LangChain
├── langgraph/         # LangGraph
├── google-adk/        # Google Agent Development Kit
├── anthropic-sdk/     # Anthropic Agent SDK
├── crewai/            # CrewAI
└── llamaindex/        # LlamaIndex Agents
```

Each directory is a fully independent, self-contained project with its own dependencies. Implementations may use different languages depending on the framework ecosystem. There is no shared code between them — all implementations follow the language-agnostic task specification defined in `spec/`.

Conventions:
- Directory names use kebab-case.
- Each directory manages its own environment and dependencies.
- All implementations must conform to the spec in `spec/task.md`.

## Generating input data

The `spec/generate.py` script uses an LLM (via Ollama) to produce conversation transcript files that follow the format in `spec/task.md`.

### Setup

```bash
cd spec/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Usage

```bash
export OLLAMA_BASE_URL="http://<host>:<port>/v1"

python spec/generate.py \
  --characters alice,bob,charlie,diana,eve,frank,grace,henry,iris,jack \
  --count 10 \
  --model gpt-oss:20b \
  --verbose
```

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--characters` | yes* | — | Comma-separated character names |
| `--characters-file` | yes* | — | JSON file with character list |
| `--count` | yes | — | Number of files to generate |
| `--messages` | no | `100` | Approx messages per conversation |
| `--output-dir` | no | `spec/inputs/` | Output directory |
| `--model` | no | `gpt-oss:20b` | Ollama model name |
| `--verbose` | no | off | Debug logging |

\*Mutually exclusive; one is required.

Each generated file is validated against the message format spec. Invalid outputs are retried up to 3 times before being skipped.

