"""Text diff between two TipTap JSON snapshots."""
from __future__ import annotations

import difflib
import html
import json
from typing import Any


def _extract_plain(node: dict[str, Any], lines: list[str]) -> None:
    t = node.get("type")
    if t == "text":
        lines.append(node.get("text") or "")
        return
    for ch in node.get("content") or []:
        _extract_plain(ch, lines)
    if t in ("paragraph", "heading"):
        lines.append("\n")


def json_to_lines(doc_json: str) -> str:
    try:
        root = json.loads(doc_json)
    except json.JSONDecodeError:
        return ""
    parts: list[str] = []
    _extract_plain(root, parts)
    return "".join(parts)


def diff_html(old_json: str, new_json: str) -> str:
    a = json_to_lines(old_json).splitlines(keepends=True)
    b = json_to_lines(new_json).splitlines(keepends=True)
    out: list[str] = ['<div class="diff">']
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag == "equal":
            chunk = "".join(a[i1:i2])
            out.append(f"<span>{html.escape(chunk)}</span>")
        elif tag == "delete":
            chunk = "".join(a[i1:i2])
            out.append(f'<del class="diff-del">{html.escape(chunk)}</del>')
        elif tag == "insert":
            chunk = "".join(b[j1:j2])
            out.append(f'<ins class="diff-ins">{html.escape(chunk)}</ins>')
        elif tag == "replace":
            out.append(
                f'<del class="diff-del">{html.escape("".join(a[i1:i2]))}</del>'
                f'<ins class="diff-ins">{html.escape("".join(b[j1:j2]))}</ins>'
            )
    out.append("</div>")
    return "".join(out)
