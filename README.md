# chatgpt-export-to-markdown

Turn your **ChatGPT data export** into clean, readable Markdown — one file per conversation.

ChatGPT lets you download your full history (**Settings → Data controls → Export data**), which
emails you a ZIP containing `conversations.json`. That file is a machine format you can't actually
read. This tiny script converts it into tidy `.md` files you can browse, grep, commit to a repo,
or feed into anything that reads Markdown.

- ✅ ✅ Accepts the raw export **.zip** or the extracted `conversations.json`

No dependencies — Python 3 standard library only
- ✅ Handles the **modern export** (mapping-tree format) **and** the older flat `messages` format
- ✅ One `.md` per conversation, messages in order, with titles and timestamps

## Usage

```bash
python3 chatgpt_export_to_markdown.py conversations.json -o out/
```

That writes one Markdown file per conversation into `out/`. Example output:

```markdown
# Fixing a Python bug

*Exported conversation — started 2024-05-29 16:26 UTC*

**You:**

Why does my loop skip the last item?

**ChatGPT:**

Off-by-one: your range stops one short. Use range(len(x)).
```

## Why convert your export?

- **Readable backups** of your own thinking, in plain text you own.
- **Searchable locally** — `grep -ri "that thing I figured out" out/`.
- **Portable** — drop the Markdown into Obsidian, a Git repo, or any notes app.

## Related tools

If you work with your AI history a lot, these pair well with this script:

- **[Backscroll](https://backscroll.xyz)** — import your ChatGPT, Claude, and Gemini exports and get
  them *searchable* (keyword + semantic), and ask questions answered from your own past chats with
  citations. The natural next step once you've exported.
- **[AI Chat Exporter](https://petescribe5.gumroad.com/l/tbnxg)** — a browser extension that grabs a
  *single* ChatGPT or Claude conversation in one click, when you don't want to wait for the full
  account export.

## Part of a small suite of ChatGPT-export tools
- [chatgpt-export-to-markdown](https://github.com/jelonman/chatgpt-export-to-markdown) — turn your export into readable Markdown
- [chatgpt-export-stats](https://github.com/jelonman/chatgpt-export-stats) — wrapped-style stats from your history
- [chatgpt-export-search](https://github.com/jelonman/chatgpt-export-search) — search your history from the CLI
- [claude-export-to-markdown](https://github.com/jelonman/claude-export-to-markdown) — same, for Claude (Claude.ai) exports

## License

MIT — do whatever you like.
