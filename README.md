# Obsidian Codex Skill

这个仓库包含一个 Codex skill：`obsidian-qa-recorder`。它用于在 Codex 对话中自动识别值得沉淀的知识性问答，并把整理后的问题、答案和标题写入用户的 Obsidian vault。

## 作用

当用户在 Codex 中提出知识性、技术性、概念性或专业学习问题时，Codex 可以使用这个 skill：

- 判断这轮对话是否值得记录为学习笔记。
- 为问答生成中文优先、可检索的标题。
- 将用户原始问题和最终答案保存为独立 Markdown 笔记。
- 自动维护 Obsidian 索引笔记。
- 跳过普通聊天、安装迁移、文件操作、GitHub 发布、skill 维护、确认和感谢类对话。

## 适合记录的问题

例如：

- `什么是 Agent Loop，和普通 while 循环有什么区别？`
- `Claude Memory 怎么避免记忆污染？`
- `React useEffect 依赖数组为什么会导致重复请求？`
- `GitHub Actions 的 workflow/job/step 是什么关系？`
- `Obsidian 的 vault、笔记、双链分别是什么？`

这些问题会被整理成类似下面的笔记标题：

```text
Claude Memory QA - 短期记忆与长期记忆加载流程
GitHub Actions QA - Workflow Job Step 的区别
Obsidian QA - Vault 与双链的作用
```

## 默认输出位置

脚本会优先从 Obsidian 配置中自动检测当前 vault；如果检测不到，则使用默认路径：

```text
C:\Users\24471\Documents\Obsidian Vault
```

默认笔记目录：

```text
Codex 技术 QA
```

默认索引笔记：

```text
Codex 技术 QA 索引.md
```

## 安装到 Codex

可以直接把本仓库安装为 Codex skill，或者复制到本机 Codex skills 目录：

```text
C:\Users\24471\.codex\skills\obsidian-qa-recorder
```

安装后建议重启 Codex，让新的 skill 元数据在新对话中稳定生效。

## 手动调用脚本

推荐使用 UTF-8 JSON 文件传参，避免 Windows 终端编码问题：

```bash
python scripts/append_qa_to_obsidian.py --input-json payload.json
```

示例 `payload.json`：

```json
{
  "question": "什么是 Agent Loop？",
  "answer": "Agent Loop 是智能体围绕观察、思考、工具调用和结果反馈不断迭代的主循环。",
  "topic": "Claude Agent Loop QA - 基本概念",
  "tags": ["codex", "qa", "agent"]
}
```

也可以使用 `--dry-run` 预览将要生成的 Markdown 内容：

```bash
python scripts/append_qa_to_obsidian.py --input-json payload.json --dry-run
```

## 仓库结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── append_qa_to_obsidian.py
```

其中：

- `SKILL.md` 定义 Codex 何时触发该 skill，以及记录问答的工作流。
- `agents/openai.yaml` 提供 Codex UI 中展示的名称和默认提示。
- `scripts/append_qa_to_obsidian.py` 负责创建 Obsidian Markdown 笔记并更新索引。

## 安全策略

这个 skill 不会记录所有对话。它会跳过：

- 普通聊天、确认、感谢。
- 安装、迁移、下载、文件整理。
- Obsidian housekeeping。
- repo 发布、GitHub 上传、skill 更新。
- 密码、token、私钥等敏感信息。

如果确实需要强制记录某一轮，可以显式要求使用 `$obsidian-qa-recorder`。
