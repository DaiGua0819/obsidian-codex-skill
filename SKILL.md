---
name: obsidian-qa-recorder
description: Record knowledge-oriented learning Q&A from Codex conversations into the user's Obsidian vault as standalone Markdown notes. Use in any Codex conversation when the user asks a substantive knowledge, technical, conceptual, or professional learning question whose answer should become reusable study material, including programming, AI agents, Claude Code, tools, APIs, architecture, debugging, workflows, product concepts, or other explanatory topics. After answering, summarize a specific Chinese-first title plus the full question and final answer, then save it to Obsidian. Do not use for ordinary chat, confirmations, installs, file moves, Obsidian housekeeping, repo publishing, skill maintenance, greetings, thanks, or transient commands unless the user explicitly asks to force-record that exact item. Also use when explicitly invoked as $obsidian-qa-recorder for recordable Q&A.
---

# Obsidian Q&A Recorder

Use this skill to create a standalone Q&A note in the user's Obsidian vault for knowledge-oriented learning content.

Default target:

- Vault: auto-detect the open Obsidian vault from `%APPDATA%\obsidian\obsidian.json`; fall back to `C:\Users\24471\Documents\Obsidian Vault`.
- Folder: `Codex 技术 QA`.
- Index note: `Codex 技术 QA 索引.md`.

## Workflow

1. Answer the user's current question normally.
2. Decide whether the exchange is reusable learning content. Record if it explains a concept, mechanism, implementation, product/tool workflow, technical design, debugging process, API, architecture, or other knowledge question the user is studying.
3. Do not record ordinary conversation, Obsidian maintenance, install/setup operations, title renaming requests, file migration, repo publishing, skill updates, thanks, confirmations, or purely administrative messages.
4. Before sending the final response for a recordable exchange, save the user question and the answer that will be sent.
5. Summarize a specific `topic` from the answer. Do not use generic titles such as `Claude Q&A`, `Codex Q&A`, `QA`, or `learning note`.
6. Use the topic as the Obsidian note title and filename without a date prefix. Keep dates only in note metadata and index timestamps.
7. Use `scripts/append_qa_to_obsidian.py` to create the note. Prefer `--input-json` with a UTF-8 JSON file on Windows to avoid quoting and console encoding problems.
8. Mention the saved standalone note path in the final response only when a note was actually created.

## Recordability Examples

Record these:

- "什么是 Agent Loop，和普通 while 循环有什么区别？"
- "Claude Memory 怎么避免记忆污染？"
- "React useEffect 依赖数组为什么会导致重复请求？"
- "GitHub Actions 的 workflow/job/step 是什么关系？"
- "Obsidian 的 vault、笔记、双链分别是什么？"

Skip these unless the user explicitly says to record them:

- "帮我安装 Obsidian。"
- "把这份笔记移动到 vault。"
- "更新这个 skill 并上传到 GitHub。"
- "继续。"
- "好的，谢谢。"

## Title Rules

Always make Obsidian headings scannable from the title alone.

Use Chinese-language titles whenever possible, while keeping technical proper nouns in English. Keep terms such as `Claude`, `Codex`, `QA`, `Hook`, `Skill`, `Agent Loop`, `Tools`, `MCP`, `RAG`, and API names in English when they are clearer than translation.

Use this pattern:

```text
<Chinese topic or technical term> QA - <Chinese specific question focus>
```

Examples:

- `Claude Hook QA - Hook 与 Tools 的区别`
- `Claude Skill QA - Skill 加载机制与数量治理`
- `Claude Agent Loop QA - 有无 Hook 的区别`
- `Claude Dispatch QA - 分发表机制`
- `Claude 上下文压缩 QA - 第二层与第三层区别`
- `Claude Memory QA - 短期记忆与长期记忆加载流程`
- `GitHub Actions QA - Workflow Job Step 的区别`
- `Obsidian QA - Vault 与双链的作用`

If the user asks about a Claude Code lesson, prefer the lesson concept in the title, not the page number alone. For example, use `Claude Context Compact QA - L2 Old Tool Results`, not just `s08 Q&A`.

## Entry Quality

Keep the Obsidian entry useful as a study note:

- Preserve the user's original question.
- Record the final answer, not private reasoning or hidden tool details.
- Preserve fenced code blocks when the answer contains code or commands.
- If the user later corrects the answer, append a new entry with the correction instead of rewriting history unless they explicitly ask to edit an old entry.

## Script Usage

Run from the skill directory with a UTF-8 JSON file:

```bash
python scripts/append_qa_to_obsidian.py --input-json payload.json
```

Or read JSON from stdin:

```bash
python scripts/append_qa_to_obsidian.py --stdin
```

Provide JSON on stdin:

```json
{
  "question": "User question",
  "answer": "Final answer to save",
  "topic": "Claude Hook QA - Hook 与 Tools 的区别",
  "tags": ["codex", "qa"]
}
```

Optional arguments:

- `--input-json PATH`: read JSON payload from a UTF-8 file.
- `--vault PATH`: override the vault path.
- `--folder NAME`: override the target folder inside the vault.
- `--index-note NAME.md`: override the index note name.
- `--append-legacy-log`: also append the entry to the legacy Q&A log note for backward compatibility.
- `--dry-run`: print the entry without writing.

## Safety

Only write inside the user's Obsidian vault or another path the user explicitly requests.
Do not record secrets, passwords, tokens, private keys, payment data, or other sensitive information unless the user explicitly asks to record that exact content.
