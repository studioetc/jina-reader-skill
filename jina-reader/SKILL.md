---
name: jina-reader
description: Convert web pages, PDFs, and URL lists into clean markdown via r.jina.ai. Use when the user wants the output as markdown (save, download, bulk-fetch, or load page into session with curl).
license: MIT
allowed-tools: Bash(python3 *) Bash(curl *) Read
compatibility: Requires Python 3.8+ and curl; network access to r.jina.ai
metadata:
  author: studioetc
  version: "1.3"
---

# Jina Reader

Converts any public URL into clean markdown via [r.jina.ai](https://jina.ai/reader), with controls for selector targeting, image retention, and JS-rendered pages.

Two ways to use this skill. Pick based on what the user wants.

## 1. Save to disk → use the script

When the user wants files on disk (download, save, archive, bulk fetch), run:

```bash
python3 <path-to-skill>/scripts/jina-reader.py <URL>
```

Resolve `scripts/jina-reader.py` relative to this skill's directory, but run the command from the user's current project directory. The script auto-creates `./docs/sources/` and writes the file there — no `--output-dir` needed unless the user wants a different location.

Common forms:

```bash
# Single URL with a preset
python3 <SCRIPT> --preset text-only https://example.com/article

# Multiple URLs
python3 <SCRIPT> https://one.com https://two.com

# Bulk from a file (one URL per line, # for comments)
python3 <SCRIPT> --input-file urls.txt

# Custom output dir (default is docs/sources/)
python3 <SCRIPT> https://example.com --output-dir ./saved-pages
```

## 2. Load into context → use curl

When the user wants to read the page now (summarise, extract, answer a question about it), don't write a file. Use curl directly — Bash captures the response into your context:

```bash
curl -s "https://r.jina.ai/<URL>" \
  -H "Accept: text/plain" \
  -H "X-Respond-With: markdown" \
  -H "X-Remove-Selector: nav, header, footer, aside" \
  -H "X-Retain-Images: none"
```

Add `-H "Authorization: Bearer $JINA_API_KEY"` if the env var is set.

## Presets (script only)

| Preset             | What it does                                               |
| ------------------ | ---------------------------------------------------------- |
| `default`          | Clean markdown, strips nav/header/footer/aside and images  |
| `full-page`        | Full page as markdown, nothing stripped                    |
| `text-only`        | Main content only, no images or links, strips page chrome  |
| `wait-for-content` | Waits up to 30s for JS-rendered content before extracting  |

## Override flags (script only)

The five most useful flags. For everything else, run the script with `--help` or see the [Jina Reader docs](https://jina.ai/reader).

| Flag                  | Description                                                                                                                                          |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--remove-selector`   | CSS selector(s) to strip before extraction (e.g. `"nav, footer, aside"`). Use to remove chrome/boilerplate from the output.                          |
| `--retain-images`     | Image output: `none` (lowest tokens, default in most presets), `all` (keep all), `alt` (only images with alt text).                                  |
| `--target-selector`   | CSS selector to scope extraction to one element (e.g. `"article"`, `".post-body"`). Use when you want a single section, not the full page.           |
| `--wait-for-selector` | CSS selector Reader waits for before extracting. Use for JS-rendered pages where content loads after the initial HTML.                               |
| `--timeout`           | Local socket timeout in seconds for this script (default 60). To control how long Reader waits for the remote page to load, use `--page-timeout`.    |

## Auth & rate limits

If `JINA_API_KEY` is set, both modes use it (500 RPM). Without one, free tier is 20 RPM.

## Troubleshooting

- **Empty content from `text-only`**: Try `--preset default`. As a last resort, `--target-selector` can aim at a specific element.
- **JS-heavy pages return stubs**: Use `--preset wait-for-content`, optionally with `--wait-for-selector .your-class`.
- **Too much page chrome**: `--remove-selector` strips additional elements.
- **Rate limited**: Set `JINA_API_KEY` for 500 RPM.

## Reference

- [Jina Reader docs](https://jina.ai/reader)
