#!/usr/bin/env python3
"""Generate theater-style conversation transcript files using an LLM via Ollama."""

import argparse
import json
import logging
import os
import random
import re
import sys
import time
from pathlib import Path

from openai import OpenAI

logger = logging.getLogger(__name__)

MESSAGE_RE = re.compile(r"^([a-z]+): (.+)$")

TOPICS = [
    "planning a surprise birthday party",
    "debating the best pizza toppings",
    "organizing a weekend hiking trip",
    "discussing a mysterious noise in the building",
    "planning a potluck dinner",
    "debating which movie to watch tonight",
    "coordinating a group study session",
    "discussing rumors about a new neighbor",
    "planning a road trip across the country",
    "arguing about the rules of a board game",
    "discussing what to name a new pet",
    "planning a community garden project",
    "debating the merits of early morning vs late night routines",
    "organizing a charity fundraiser",
    "discussing a strange dream someone had",
    "planning a home renovation project",
    "debating the best strategy for a video game",
    "discussing a book everyone just read",
    "planning a camping trip",
    "arguing about whose turn it is to do the dishes",
]


def load_format_spec() -> str:
    """Load the format specification from spec/format.md."""
    format_path = Path(__file__).parent / "format.md"
    return format_path.read_text(encoding="utf-8")


def build_system_prompt(format_spec: str) -> str:
    """Build the system prompt with embedded format rules."""
    return (
        "You are a conversation transcript generator. You produce theater-style "
        "conversation transcripts that strictly follow a specific format.\n\n"
        "## Format Rules\n\n"
        f"{format_spec}\n\n"
        "## Critical Instructions\n\n"
        "- Output ONLY the conversation transcript, nothing else.\n"
        "- No headers, titles, labels, or commentary.\n"
        "- No markdown code fences.\n"
        "- Every non-blank line MUST match the pattern: <lowercase_name>: <message>\n"
        "- Character names must be strictly lowercase letters only.\n"
        "- Do not use any characters outside the ones specified.\n"
        "- Blank lines between messages are allowed but not required.\n"
    )


def build_user_prompt(characters: list[str], message_count: int, topic: str) -> str:
    """Build the user prompt for a specific conversation."""
    char_list = ", ".join(characters)
    return (
        f"Generate a conversation transcript between these characters: {char_list}\n\n"
        f"The conversation should be about: {topic}\n\n"
        f"Requirements:\n"
        f"- Produce approximately {message_count} messages total.\n"
        f"- Only use these exact character names: {char_list}\n"
        f"- Each character should speak multiple times.\n"
        f"- Make the dialogue natural and varied.\n"
        f"- Follow the format rules exactly.\n"
    )


def validate_transcript(text: str, allowed_characters: set[str]) -> tuple[bool, str]:
    """Validate a generated transcript against format rules.

    Returns (is_valid, error_message).
    """
    lines = text.strip().splitlines()
    if not lines:
        return False, "Empty transcript"

    seen_characters = set()
    message_count = 0

    for i, line in enumerate(lines, 1):
        if line.strip() == "":
            continue

        match = MESSAGE_RE.match(line)
        if not match:
            return False, f"Line {i}: invalid format: {line!r}"

        name = match.group(1)
        seen_characters.add(name)

        if name not in allowed_characters:
            return False, f"Line {i}: unexpected character {name!r}"

        message_count += 1

    if message_count == 0:
        return False, "No valid messages found"

    return True, ""


def generate_conversation(
    client: OpenAI,
    model: str,
    system_prompt: str,
    characters: list[str],
    message_count: int,
    max_retries: int = 3,
) -> str | None:
    """Generate a single conversation transcript with retries.

    Returns the validated transcript text, or None if all retries failed.
    """
    topic = random.choice(TOPICS)
    user_prompt = build_user_prompt(characters, message_count, topic)
    allowed = set(characters)

    logger.debug("Characters: %s, Topic: %s", characters, topic)

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,
            )
            text = response.choices[0].message.content.strip()

            is_valid, error = validate_transcript(text, allowed)
            if is_valid:
                return text

            logger.warning("Attempt %d: validation failed: %s", attempt, error)

        except Exception as e:
            logger.warning("Attempt %d: LLM error: %s", attempt, e)
            if attempt < max_retries:
                time.sleep(2**attempt)

    return None


def parse_characters(value: str) -> list[str]:
    """Parse and validate a comma-separated character list."""
    names = [name.strip() for name in value.split(",") if name.strip()]
    for name in names:
        if not re.match(r"^[a-z]+$", name):
            print(f"Error: invalid character name {name!r} (must be lowercase a-z only)", file=sys.stderr)
            sys.exit(1)
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate conversation transcript files using an LLM via Ollama.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--characters", type=str, help="Comma-separated character names")
    group.add_argument("--characters-file", type=str, help="JSON file with character list")
    parser.add_argument("--count", type=int, required=True, help="Number of files to generate")
    parser.add_argument("--messages", type=int, default=100, help="Approx messages per conversation (default: 100)")
    parser.add_argument("--output-dir", type=str, default="spec/inputs/", help="Output directory (default: spec/inputs/)")
    parser.add_argument("--model", type=str, default="gpt-oss:20b", help="Ollama model name (default: gpt-oss:20b)")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Resolve Ollama URL
    base_url = os.environ.get("OLLAMA_BASE_URL")
    if not base_url:
        print("Error: OLLAMA_BASE_URL environment variable is required", file=sys.stderr)
        sys.exit(1)

    # Parse characters
    if args.characters:
        characters = parse_characters(args.characters)
    else:
        char_path = Path(args.characters_file)
        if not char_path.exists():
            print(f"Error: characters file not found: {char_path}", file=sys.stderr)
            sys.exit(1)
        with open(char_path, encoding="utf-8") as f:
            characters = json.load(f)
        if not isinstance(characters, list) or not all(isinstance(c, str) for c in characters):
            print("Error: characters file must contain a JSON array of strings", file=sys.stderr)
            sys.exit(1)
        for name in characters:
            if not re.match(r"^[a-z]+$", name):
                print(f"Error: invalid character name {name!r} in file (must be lowercase a-z only)", file=sys.stderr)
                sys.exit(1)

    if len(characters) < 2:
        print("Error: at least 2 characters are required", file=sys.stderr)
        sys.exit(1)

    # Set up output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set up OpenAI client pointing to Ollama
    client = OpenAI(base_url=base_url, api_key="ollama")

    # Load format spec and build system prompt
    format_spec = load_format_spec()
    system_prompt = build_system_prompt(format_spec)

    logger.debug("Model: %s", args.model)
    logger.debug("Character pool: %s", characters)
    logger.debug("Output directory: %s", output_dir)

    succeeded = 0
    failed = 0

    for i in range(1, args.count + 1):
        # Pick 2-4 random characters for this conversation
        num_chars = random.randint(2, min(4, len(characters)))
        selected = random.sample(characters, num_chars)

        file_name = f"{i:03d}.txt"
        file_path = output_dir / file_name

        print(f"[{i}/{args.count}] Generating {file_name} with {selected}...")

        transcript = generate_conversation(
            client=client,
            model=args.model,
            system_prompt=system_prompt,
            characters=selected,
            message_count=args.messages,
        )

        if transcript is None:
            logger.warning("Skipping %s: all retries failed", file_name)
            failed += 1
            continue

        file_path.write_text(transcript + "\n", encoding="utf-8")
        succeeded += 1
        logger.debug("Wrote %s", file_path)

    print(f"\nDone: {succeeded} succeeded, {failed} failed out of {args.count} total")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
