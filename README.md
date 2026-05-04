# Jina Reader — Agent Skill

An [Agent Skill](https://agentskills.io) that converts websites and PDFs into clean, LLM-friendly markdown using [Jina Reader](https://jina.ai/reader). Saves the markdown to local files by default, or loads it directly into the agent's session via `curl`.

## Install

Copy the `jina-reader/` directory into your agent's skills folder:

| Tool              | Skills location       |
| ----------------- | --------------------- |
| Claude Code       | `~/.claude/skills/`   |
| Codex             | `~/.agents/skills/`   |
| Gemini CLI        | `~/.gemini/skills/`   |
| VS Code / Copilot | `.github/skills/` in your repo |

Example for Claude Code:

```bash
git clone <repo-url> /tmp/jina-reader-skill
cp -r /tmp/jina-reader-skill/jina-reader ~/.claude/skills/
```

## Setup

Optional but recommended — set a Jina API key for higher rate limits (500 RPM vs the 20 RPM free tier):

```bash
export JINA_API_KEY="your-key-here"
```

Get a key for free at [jina.ai/reader](https://jina.ai/reader).

## Usage

Once installed, prompt your agent naturally:

- *"Download this page as markdown — https://en.wikipedia.org/wiki/Solaris_(1972_film)"*
- *"Download all URLs in `movies.txt` as markdown"*
- *"Load this page into context as markdown, article only"*

The skill picks the right path automatically: the bundled Python script for save-to-disk asks, `curl` for load-into-context.

## Presets

Four presets cover most use cases:

- **`default`** — clean markdown, strips nav/header/footer/aside and images
- **`full-page`** — full page as markdown, nothing stripped
- **`text-only`** — main content only, no images or links
- **`wait-for-content`** — waits up to 30s for JS-rendered content

For finer control, the script exposes selector and timeout overrides — see `jina-reader/SKILL.md`.

## Notes

- `--insecure` is enabled by default to avoid SSL friction on Python setups without certificates installed. Disable with `--no-insecure` if your environment is locked down.

## License

MIT
