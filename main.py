"""One-Sentence Absurd Invention Pitch.

Reads the pitch from pitch.txt (shipped beside this file) and writes it
to /output/entry.txt, exactly as the make.fun program/v1 harness expects.

Gate: /output/entry.txt must be UTF-8 text of 1 to 220 characters, not
only whitespace, and a single sentence. The pitch is validated before
anything is written, and the file is written atomically (temp file +
rename) so a partial write can never be observed.
"""

import os
import sys

MAX_CHARS = 220


def _base_dir():
    """Directory holding this file; the grader's cwd is not the repo."""
    return os.path.dirname(os.path.abspath(__file__))


def _output_dir():
    """Writable output directory: the grader provides /output; local
    runs may point elsewhere with MAKEFUN_OUTPUT_DIR."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def load_pitch():
    path = os.path.join(_base_dir(), "pitch.txt")
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    # The file ends with a single trailing newline; the pitch itself
    # carries no leading or trailing whitespace.
    if text.endswith("\n"):
        text = text[:-1]
    return text


def validate(text):
    """Raise ValueError unless the text passes the sealed gate."""
    if not isinstance(text, str):
        raise ValueError("pitch is not text")
    stripped = text.strip()
    if not stripped:
        raise ValueError("pitch is empty or only whitespace")
    if len(stripped) > MAX_CHARS:
        raise ValueError(
            "pitch is %d characters, over the %d limit"
            % (len(stripped), MAX_CHARS)
        )
    if stripped != text:
        raise ValueError("pitch has leading or trailing whitespace")
    # One sentence: exactly one sentence-ending period, at the end.
    if stripped.count(".") != 1 or not stripped.endswith("."):
        raise ValueError("pitch must be exactly one sentence")
    return stripped


def write_entry(text):
    out_dir = _output_dir()
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, target)
    # Read-back verification: the file on disk must be byte-identical
    # to the validated pitch, or the run has failed.
    with open(target, "r", encoding="utf-8") as fh:
        written = fh.read()
    if written != text:
        raise ValueError("read-back mismatch in %s" % target)
    if os.path.exists(tmp):
        raise ValueError("temporary file %s was not replaced" % tmp)
    return target


def main():
    try:
        pitch = validate(load_pitch())
        target = write_entry(pitch)
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print("wrote %d characters to %s" % (len(pitch), target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
