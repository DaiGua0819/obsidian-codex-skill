#!/usr/bin/env python3
"""Create a standalone Codex learning Q&A note in an Obsidian vault."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_INDEX_NOTE = "Codex 技术 QA 索引.md"
DEFAULT_FOLDER = "Codex 技术 QA"
LEGACY_LOG_NOTE = "Codex 问答记录.md"
FALLBACK_VAULT = Path.home() / "Documents" / "Obsidian Vault"
GENERIC_TOPICS = {
    "qa",
    "q&a",
    "codex qa",
    "codex q&a",
    "claude qa",
    "claude q&a",
    "claudeqa",
    "学习笔记",
    "问答记录",
    "codex 问答",
}
KNOWLEDGE_MARKERS = (
    "claude code", "agent", "agent loop", "agent_loop", "hook", "hooks",
    "skill", "skills", "tool", "tools", "dispatch", "context compact",
    "compact_history", "micro_compact", "tool_result_budget", "prompt_too_long",
    "memory", "mem0", "mcp", "rag", "api", "sdk", "python", "javascript",
    "typescript", "node", "react", "vue", "git", "github", "debug", "bug",
    "code", "script", "json", "markdown", "regex", "obsidian",
    "架构", "机制", "原理", "区别", "实现", "代码", "脚本", "工具",
    "调试", "接口", "上下文", "压缩", "模型", "智能体", "记忆",
    "短期记忆", "长期记忆", "概念", "教程", "学习", "知识", "方法",
    "流程", "设计", "案例", "示例", "最佳实践", "工作流",
)
LEARNING_SHAPE_MARKERS = (
    "是什么", "为什么", "区别", "机制", "原理", "举例", "例子",
    "怎么实现", "如何判断", "解释", "详细讲", "详细了解", "讲一下",
    "设计", "流程", "怎么做", "如何做", "怎么避免", "如何避免",
    "怎么解决", "如何解决", "怎么处理", "如何处理", "最佳实践", "场景", "案例",
    "what is", "why", "how does", "how to", "explain", "compare",
)
ADMIN_MARKERS = (
    "安装", "下载", "迁移", "移进去", "删除", "改名", "命名", "标题",
    "更新obsidian", "更新 obsidian", "桌面", "vault", "记录到obsidian",
    "记录到 obsidian", "笔记迁移", "放到桌面", "打开obsidian",
    "open folder as vault", "上传到github", "上传到 github", "推送到github", "推送到 github",
    "发布到github", "发布到 github", "git push", "帮我clone", "帮我 clone",
    "帮我提交", "创建commit", "创建 commit", "更新skill", "更新 skill", "安装skill",
    "安装 skill", "skill上传", "skill 上传", "技能维护",
)
TRIVIAL_MESSAGES = {
    "继续",
    "可以",
    "好的",
    "好",
    "对",
    "嗯",
    "谢谢",
    "感谢",
    "ok",
    "yes",
}


def normalize_short_message(text: str) -> str:
    return " ".join((text or "").lower().strip(" \t\r\n。！？!?.,，：:；;").split())


def detect_obsidian_vault() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        config = Path(appdata) / "obsidian" / "obsidian.json"
        if config.exists():
            try:
                data = json.loads(config.read_text(encoding="utf-8-sig"))
                vaults = data.get("vaults", {})
                open_vaults = [
                    value for value in vaults.values()
                    if isinstance(value, dict) and value.get("open") and value.get("path")
                ]
                if open_vaults:
                    return Path(open_vaults[0]["path"])
                for value in vaults.values():
                    if isinstance(value, dict) and value.get("path"):
                        return Path(value["path"])
            except Exception:
                pass
    return FALLBACK_VAULT


def fence(text: str) -> str:
    text = (text or "").rstrip()
    if not text:
        return "_无内容_"
    return text


def short_focus(question: str) -> str:
    first_line = " ".join((question or "").strip().split())
    for prefix in ("[README.md]", "README.md"):
        if first_line.startswith(prefix):
            first_line = first_line[len(prefix):].strip()
    replacements = [
        ("https://github.com/shareAI-lab/learn-claude-code/blob/main/", ""),
        ("你可以帮我", ""),
        ("可以帮我", ""),
        ("请你帮我", ""),
        ("帮我", ""),
    ]
    for old, new in replacements:
        first_line = first_line.replace(old, new)
    first_line = first_line.strip(" ：:，,。.?？")
    if len(first_line) > 42:
        first_line = first_line[:42].rstrip() + "..."
    return first_line or "Specific Question"


def is_knowledge_learning(question: str, answer: str, force: bool = False) -> bool:
    if force:
        return True
    if normalize_short_message(question) in TRIVIAL_MESSAGES:
        return False
    text = f"{question}\n{answer}".lower()
    question_text = question.lower()
    has_knowledge = any(marker in text for marker in KNOWLEDGE_MARKERS)
    has_admin = any(marker in question_text for marker in ADMIN_MARKERS)
    learning_shape = any(marker in text for marker in LEARNING_SHAPE_MARKERS)
    if has_admin:
        return False
    if has_knowledge and learning_shape:
        return True
    if learning_shape and len(answer.strip()) >= 120:
        return True
    if has_knowledge and len(answer.strip()) >= 240:
        return True
    return False


def infer_topic(question: str, answer: str) -> str:
    text = f"{question}\n{answer}".lower()
    focus = short_focus(question)
    if any(word in text for word in ("memory", "mem0", "记忆", "短期记忆", "长期记忆")):
        base = "Claude Memory QA"
    elif any(word in text for word in ("context compact", "compact_history", "micro_compact", "tool_result_budget", "prompt_too_long", "上下文", "压缩")):
        base = "Claude 上下文压缩 QA"
    elif any(word in text for word in ("agentloop", "agent loop", "agent_loop", "主循环")):
        base = "Claude Agent Loop QA"
    elif "dispatch" in text or "分发" in text:
        base = "Claude Dispatch QA"
    elif "hook" in text or "hooks" in text:
        base = "Claude Hook QA"
    elif "skill" in text or "skills" in text or "技能" in text:
        base = "Claude Skill QA"
    elif "tool" in text or "tools" in text or "工具" in text:
        base = "Claude Tools QA"
    elif "github actions" in text:
        base = "GitHub Actions QA"
    elif "github" in text or "git " in text:
        base = "GitHub QA"
    elif "obsidian" in text or "双链" in text or "vault" in text:
        base = "Obsidian QA"
    elif "python" in text:
        base = "Python QA"
    elif "react" in text:
        base = "React QA"
    else:
        base = "知识学习 QA"
    return f"{base} - {focus}"


def normalize_topic(topic: str | None, question: str, answer: str) -> str:
    clean = (topic or "").strip()
    if not clean or clean.lower().strip() in GENERIC_TOPICS:
        return infer_topic(question, answer)
    return clean


def build_entry(question: str, answer: str, topic: str | None, tags: list[str]) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = normalize_topic(topic, question, answer)
    tag_line = " ".join(f"#{tag.strip().replace(' ', '-')}" for tag in tags if tag.strip())
    parts = [
        "",
        "---",
        "",
        f"## {timestamp} - {title}",
        "",
    ]
    if tag_line:
        parts.extend([tag_line, ""])
    parts.extend([
        "### 问题",
        "",
        fence(question),
        "",
        "### 答案",
        "",
        fence(answer),
        "",
    ])
    return "\n".join(parts)


def sanitize_file_name(name: str) -> str:
    for char in '<>:"/\\|?*':
        name = name.replace(char, "-")
    name = " ".join(name.split()).strip(" .-")
    if len(name) > 120:
        name = name[:120].rstrip(" .-")
    return name or "Codex Q&A"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem} {index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find unique path for {path}")


def infer_subfolder(topic: str) -> str:
    text = (topic or "").lower()
    if any(marker in text for marker in ("claude hook", "agent loop", "dispatch")):
        return "Claude Hook"
    if "claude skill" in text:
        return "Claude Skill"
    if "claude memory" in text:
        return "Claude Memory"
    if "claude system prompt" in text:
        return "Claude System Prompt"
    if "claude error recovery" in text:
        return "Claude Error Recovery"
    if "claude 上下文压缩" in text or "context compact" in text:
        return "Claude 上下文压缩"
    if "llm wiki" in text:
        return "LLM Wiki"
    if text.startswith("rag ") or text.startswith("rag loop") or " rag " in f" {text} ":
        return "RAG"
    if "飞书邮箱备份" in topic:
        return "飞书邮箱备份"
    if "codex skill" in text:
        return "Codex Skill"
    if "github actions" in text or text.startswith("github "):
        return "GitHub"
    if "obsidian" in text:
        return "Obsidian"
    if "python" in text:
        return "Python"
    if "react" in text:
        return "React"
    return "未分类"


def build_note_content(question: str, answer: str, topic: str, tags: list[str], timestamp: str) -> str:
    tag_line = " ".join(f"#{tag.strip().replace(' ', '-')}" for tag in tags if tag.strip())
    parts = [
        f"# {topic}",
        "",
        f"> Date: {timestamp}",
        "",
    ]
    if tag_line:
        parts.extend([tag_line, ""])
    parts.extend([
        "## 问题",
        "",
        fence(question),
        "",
        "## 答案",
        "",
        fence(answer),
        "",
    ])
    return "\n".join(parts)


def ensure_index(index_path: Path) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if not index_path.exists():
        index_path.write_text(
            "# Codex Q&A Index\n\n"
            "Each Q&A is saved as a standalone Obsidian note with a specific title.\n\n",
            encoding="utf-8",
        )


def append_index_link(index_path: Path, note_path: Path, title: str, timestamp: str) -> None:
    ensure_index(index_path)
    try:
        link_target = note_path.relative_to(index_path.parent).with_suffix("").as_posix()
    except ValueError:
        link_target = note_path.stem
    line = f"- {timestamp} - [[{link_target}|{title}]]\n"
    current = index_path.read_text(encoding="utf-8-sig")
    if line not in current:
        with index_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)


def ensure_legacy_log(note_path: Path) -> None:
    note_path.parent.mkdir(parents=True, exist_ok=True)
    if not note_path.exists():
        note_path.write_text(
            "# Codex 问答记录\n\n"
            "这里记录用户在 Codex 中提出的问题，以及整理后的答案。\n",
            encoding="utf-8",
        )


def parse_payload(args: argparse.Namespace) -> dict:
    if args.input_json:
        return json.loads(Path(args.input_json).read_text(encoding="utf-8-sig"))
    if args.stdin:
        raw = sys.stdin.read()
        return json.loads(raw)
    return {
        "question": args.question,
        "answer": args.answer,
        "topic": args.topic,
        "tags": args.tag or [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdin", action="store_true", help="Read JSON payload from stdin.")
    parser.add_argument("--input-json", default="", help="Read JSON payload from a UTF-8 file.")
    parser.add_argument("--question", default="")
    parser.add_argument("--answer", default="")
    parser.add_argument("--topic", default="")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--vault", default="")
    parser.add_argument("--folder", default=DEFAULT_FOLDER)
    parser.add_argument("--index-note", default=DEFAULT_INDEX_NOTE)
    parser.add_argument("--append-legacy-log", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = parse_payload(args)
    question = str(payload.get("question", "")).strip()
    answer = str(payload.get("answer", "")).strip()
    raw_topic = str(payload.get("topic", "")).strip() or None
    tags_raw = payload.get("tags", args.tag or ["codex", "qa"])
    force_record = bool(payload.get("force_record", False))
    if isinstance(tags_raw, str):
        tags = [tags_raw]
    else:
        tags = [str(tag) for tag in tags_raw]

    if not question:
        raise SystemExit("Missing question.")
    if not answer:
        raise SystemExit("Missing answer.")
    if not is_knowledge_learning(question, answer, force_record):
        print("Skipped: not a recordable knowledge Q&A.")
        return 0

    vault = Path(args.vault) if args.vault else detect_obsidian_vault()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    topic = normalize_topic(raw_topic, question, answer)
    target_dir = vault / args.folder / infer_subfolder(topic)
    target_dir.mkdir(parents=True, exist_ok=True)
    note_path = unique_path(target_dir / f"{sanitize_file_name(topic)}.md")
    note_content = build_note_content(question, answer, topic, tags, timestamp)
    index_path = vault / args.index_note

    if args.dry_run:
        print(note_content)
        return 0

    note_path.write_text(note_content, encoding="utf-8")
    append_index_link(index_path, note_path, topic, timestamp)

    if args.append_legacy_log:
        legacy_path = vault / LEGACY_LOG_NOTE
        ensure_legacy_log(legacy_path)
        entry = build_entry(question, answer, topic, tags)
        with legacy_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(entry)

    print(str(note_path))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
