#!/usr/bin/env python3
"""LangChain agent for the Character Appearance Count task."""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

load_dotenv()

SPEC_DIR = Path(__file__).resolve().parent.parent / "spec"
INPUTS_DIR = SPEC_DIR / "inputs"

SYSTEM_PROMPT = """\
You are an autonomous agent that solves tasks by using the tools available to \
you. Respond with ONLY the final answer in the format requested by the task.\
"""


@tool
def list_input_files() -> str:
    """List all conversation transcript files available for reading.

    Returns a newline-separated list of filenames.
    """
    files = sorted(f.name for f in INPUTS_DIR.iterdir() if f.suffix == ".txt")
    return "\n".join(files)


@tool
def read_file(filename: str) -> str:
    """Read the contents of a conversation transcript file.

    Args:
        filename: Name of the file to read (e.g. '001.txt').
    """
    path = INPUTS_DIR / filename
    if not path.is_file():
        return f"Error: file '{filename}' not found."
    return path.read_text()


def load_task_prompt() -> str:
    """Load the task description from spec files."""
    task_md = (SPEC_DIR / "task.md").read_text()
    format_md = (SPEC_DIR / "format.md").read_text()
    return f"{task_md}\n\n---\n\n{format_md}"


def build_agent(verbose: bool = False):
    base_url = os.environ.get("OLLAMA_BASE_URL")
    model = os.environ.get("OLLAMA_MODEL")

    if not base_url or not model:
        print(
            "Error: OLLAMA_BASE_URL and OLLAMA_MODEL must be set "
            "(in .env or environment).",
            file=sys.stderr,
        )
        sys.exit(1)

    llm = ChatOllama(base_url=base_url, model=model, temperature=0)

    return create_agent(
        model=llm,
        tools=[list_input_files, read_file],
        system_prompt=SYSTEM_PROMPT,
        debug=verbose,
    )


def extract_json(text: str) -> dict | None:
    """Try to parse a JSON object from the agent's output text."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


def run(max_attempts: int = 3, verbose: bool = False) -> dict | None:
    agent = build_agent(verbose=verbose)
    task_prompt = load_task_prompt()

    for attempt in range(1, max_attempts + 1):
        if verbose:
            print(f"\n--- Attempt {attempt}/{max_attempts} ---", file=sys.stderr)

        messages = [{"role": "user", "content": task_prompt}]
        if attempt > 1:
            messages.append(
                {
                    "role": "user",
                    "content": "Your previous answer was not valid JSON. "
                    "Please try again and respond with ONLY a JSON object.",
                }
            )

        result = agent.invoke({"messages": messages})

        # The last AI message contains the final answer
        ai_messages = [
            m for m in result["messages"] if hasattr(m, "type") and m.type == "ai"
        ]
        if ai_messages:
            output = ai_messages[-1].content
            parsed = extract_json(output)
            if parsed:
                return parsed

        if verbose:
            print("Could not parse JSON from output, retrying...", file=sys.stderr)

    print(
        f"Failed to get valid JSON after {max_attempts} attempts.",
        file=sys.stderr,
    )
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Run the LangChain agent for Character Appearance Count."
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Maximum retry attempts (default: 3)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print agent reasoning traces to stderr",
    )
    args = parser.parse_args()

    result = run(max_attempts=args.max_attempts, verbose=args.verbose)

    if result is not None:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
