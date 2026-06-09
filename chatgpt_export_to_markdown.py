#!/usr/bin/env python3
"""
chatgpt_export_to_markdown.py — turn your ChatGPT data export into clean Markdown.

ChatGPT lets you export your full history (Settings -> Data controls -> Export data),
which emails you a ZIP containing `conversations.json`. That file is a machine format,
not something you can read. This script converts it into one readable .md file per
conversation, with messages in order.

Usage:
    python3 chatgpt_export_to_markdown.py conversations.json -o out/

No dependencies — standard library only. Works with the modern ChatGPT export
(mapping-tree format) and the older flat `messages` format.
"""
import argparse
import json
import os
import re
from datetime import datetime, timezone

ROLE_LABELS = {"user": "You", "assistant": "ChatGPT", "system": "System", "tool": "Tool"}


import zipfile

def _load_export(path):
    """Load conversations from a ChatGPT export — accepts the raw .zip or conversations.json."""
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            name = next((n for n in z.namelist() if n.endswith("conversations.json")), None)
            if not name:
                raise SystemExit("No conversations.json found inside the zip.")
            with z.open(name) as f:
                return json.loads(f.read().decode("utf-8"))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _slug(text, fallback):
    text = (text or "").strip() or fallback
    s = re.sub(r"[^\w\- ]+", "", text).strip().replace(" ", "-").lower()
    return (s or fallback)[:80]


def _ts(t):
    if not t:
        return ""
    try:
        return datetime.fromtimestamp(float(t), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError, OverflowError):
        return ""


def _parts_to_text(content):
    """Extract plain text from a message's content (handles text + multimodal parts)."""
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts")
    if isinstance(parts, list):
        out = []
        for p in parts:
            if isinstance(p, str):
                out.append(p)
            elif isinstance(p, dict):
                out.append(p.get("text") or p.get("content") or "")
        return "\n".join(s for s in out if s).strip()
    return (content.get("text") or "").strip()


def _ordered_messages(convo):
    """Return [(role, text, create_time)] in conversation order, both formats."""
    mapping = convo.get("mapping")
    if isinstance(mapping, dict):
        # Modern format: walk the active path from current_node up to the root.
        nodes, current = mapping, convo.get("current_node")
        path = []
        seen = set()
        while current and current in nodes and current not in seen:
            seen.add(current)
            path.append(nodes[current])
            current = nodes[current].get("parent")
        path.reverse()
        if not path:  # fallback: every node, sorted by time
            path = sorted(nodes.values(), key=lambda n: ((n.get("message") or {}).get("create_time") or 0))
        rows = []
        for node in path:
            msg = node.get("message")
            if not msg:
                continue
            role = ((msg.get("author") or {}).get("role")) or "user"
            text = _parts_to_text(msg.get("content"))
            if text and role != "system":
                rows.append((role, text, msg.get("create_time")))
        return rows
    # Older flat format
    rows = []
    for msg in convo.get("messages", []) or []:
        role = ((msg.get("author") or {}).get("role")) or msg.get("role") or "user"
        text = _parts_to_text(msg.get("content")) or (msg.get("content") if isinstance(msg.get("content"), str) else "")
        if text and role != "system":
            rows.append((role, (text or "").strip(), msg.get("create_time")))
    return rows


def convo_to_markdown(convo):
    title = convo.get("title") or "Untitled conversation"
    created = _ts(convo.get("create_time"))
    lines = [f"# {title}", ""]
    if created:
        lines += [f"*Exported conversation — started {created} UTC*", ""]
    for role, text, _ in _ordered_messages(convo):
        lines += [f"**{ROLE_LABELS.get(role, role.title())}:**", "", text, ""]
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Convert a ChatGPT conversations.json export to Markdown.")
    ap.add_argument("input", help="Path to conversations.json OR the export .zip")
    ap.add_argument("-o", "--out", default="chatgpt-markdown", help="Output directory (default: chatgpt-markdown)")
    args = ap.parse_args()

    data = _load_export(args.input)
    convos = data if isinstance(data, list) else data.get("conversations", [data])

    os.makedirs(args.out, exist_ok=True)
    used, n = set(), 0
    for i, convo in enumerate(convos):
        if not isinstance(convo, dict):
            continue
        base = _slug(convo.get("title"), f"conversation-{i+1}")
        name = base
        k = 2
        while name in used:
            name, k = f"{base}-{k}", k + 1
        used.add(name)
        with open(os.path.join(args.out, f"{name}.md"), "w", encoding="utf-8") as f:
            f.write(convo_to_markdown(convo))
        n += 1
    print(f"Wrote {n} conversation(s) to {args.out}/")


if __name__ == "__main__":
    main()
