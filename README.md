# Jina Reader -- Agent Skill

An [Agent Skill](https://agentskills.io) that fetches clean markdown from URLs using [Jina Reader](https://jina.ai/reader). Works with web pages, PDFs, and JS-heavy sites.

## Install

Copy the `jina-reader/` directory into your agent's skills folder:

| Tool | Skills location |
|------|----------------|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| VS Code / Copilot | `.github/skills/` in your repo |

Example for Claude Code:

```bash
git clone <repo-url> /tmp/jina-reader-skill
cp -r /tmp/jina-reader-skill/jina-reader ~/.claude/skills/
```

## Setup

Optionally set a Jina API key for higher rate limits:

```bash
export JINA_API_KEY="your-key-here"
```

The skill works without a key (free tier rate limits apply). Get a key at [jina.ai](https://jina.ai).

## Usage

Once installed, ask your agent to fetch URLs as markdown:

- "Fetch https://example.com as markdown"
- "Save these URLs to local markdown files"
- "Read this PDF and save it locally"

The skill includes a Python helper script and supports presets: `default`, `full-page`, `text-only`, and `wait-for-content`.

## License

MIT
