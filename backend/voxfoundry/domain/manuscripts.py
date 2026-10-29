import hashlib
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from uuid import uuid4

from voxfoundry.domain.errors import DomainError

MAX_TEXT_BYTES = 1024 * 1024
MAX_UNITS = 2000
KINDS = ("part", "chapter", "episode", "manuscript", "research", "reference", "note")


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate_text(text: str) -> str:
    try:
        encoded = text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise DomainError("Text contains invalid Unicode") from exc
    if len(encoded) > MAX_TEXT_BYTES:
        raise DomainError("Manuscript text limit is 1 MiB; split into chapters", 413)
    if any(ord(c) < 32 and c not in "\r\n\t" for c in text):
        raise DomainError("Binary/control characters are not accepted as manuscript text")
    if len(paragraphs(text)) > MAX_UNITS:
        raise DomainError("Limit is 2000 paragraphs per document; split into chapters", 413)
    return text


def decode_import(filename: str, raw: bytes) -> str:
    if not filename.lower().endswith((".txt", ".md", ".markdown")):
        raise DomainError("Import a TXT or Markdown file")
    if len(raw) > MAX_TEXT_BYTES:
        raise DomainError("Manuscript import limit is 1 MiB", 413)
    try:
        text = raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
    except UnicodeError as exc:
        raise DomainError(
            "Use UTF-8 (optional BOM) or BOM-marked UTF-16; original not changed"
        ) from exc
    return validate_text(text.replace("\r\n", "\n").replace("\r", "\n"))


def paragraphs(text):
    return [
        {"start": m.start(), "end": m.end(), "text": m.group()}
        for m in re.finditer(r"\S[^\n]*(?:\n(?!\s*\n)[^\n]+)*", text)
    ]


def identify_units(old_units, text):
    """Paragraph anchors, not engine segments. Ambiguous duplicates get fresh IDs."""
    new = paragraphs(text)
    previous = [u["text"] for u in old_units]
    current = [u["text"] for u in new]
    old_counts, new_counts = Counter(previous), Counter(current)
    unique = {u["text"]: u["id"] for u in old_units if old_counts[u["text"]] == 1}
    lineage = {}
    for tag, a, b, c, d in SequenceMatcher(None, previous, current, autojunk=False).get_opcodes():
        if tag != "equal":
            for i in range(c, d):
                lineage[i] = [u["id"] for u in old_units[a:b]]
    for i, unit in enumerate(new):
        preserved = new_counts[unit["text"]] == 1 and unit["text"] in unique
        unit.update(
            id=unique[unit["text"]] if preserved else str(uuid4()),
            parents=[] if preserved else lineage.get(i, []),
        )
    return new


def resolve_pronunciation(text, rules, node_id):
    """Case-sensitive whole-term literal replacement, simultaneous/non-cascading."""
    chosen = {}
    for rule in rules:
        if rule.get("node_id") in (None, node_id):
            key = rule["term"]
            if (
                key not in chosen
                or chosen[key].get("node_id") is None
                or rule.get("node_id") == node_id
            ):
                chosen[key] = rule
    if not chosen:
        return {
            "spoken_text": text,
            "matches": [],
            "fingerprint": hashlib.sha256(canonical([]).encode()).hexdigest(),
        }
    pattern = re.compile(
        r"(?<!\w)("
        + "|".join(re.escape(k) for k in sorted(chosen, key=lambda k: (-len(k), k)))
        + r")(?!\w)"
    )
    matches = []

    def replace(match):
        rule = chosen[match.group()]
        matches.append(
            {
                "term": rule["term"],
                "replacement": rule["replacement"],
                "start": match.start(),
                "end": match.end(),
            }
        )
        return rule["replacement"]

    spoken = pattern.sub(replace, text)
    return {
        "spoken_text": spoken,
        "matches": matches,
        "fingerprint": hashlib.sha256(canonical(matches).encode()).hexdigest(),
    }
