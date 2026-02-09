# Message Format Specification

Each conversation file MUST strictly follow the format defined below. This rigidity is intentional and part of the task.

## Overall Structure

* UTF-8 encoded plain text
* Messages appear in chronological order
* Blank lines are allowed *only* between messages

## Message Grammar

Each message MUST follow this exact structure:

```
<CHARACTER_NAME>: <MESSAGE_TEXT>
```

Where:

### `<CHARACTER_NAME>`

* A single token identifying the speaker
* Constraints:

  * Lowercase ASCII letters only: `[a-z]+`
  * No spaces
  * No punctuation
  * Same character name MUST be spelled identically across all files

Examples:

```
matt
rob
alice
```

### `<MESSAGE_TEXT>`

* Arbitrary natural language text
* May include spaces and punctuation
* Must NOT contain newline characters
* The content of the message is irrelevant for the task

Examples:

```
Hello everyone, how are we today?
I think this plan could actually work.
Wait — are we sure about that?
```

## Valid Message Examples

```
matt: Hello everyone, how are we today?
rob: Doing well. Ready to start.
matt: Great, let's begin.
```

## Invalid Message Examples

```
Matt: Hello everyone        # invalid (uppercase)
rob : Hello                 # invalid (space before colon)
rob- Hello                  # invalid (wrong separator)
rob: Hello
there                        # invalid (newline in message)
```
