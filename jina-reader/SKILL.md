---
name: jina-reader
description: Fetch web pages, articles, and PDFs as clean markdown files using r.jina.ai. Use this skill whenever the user wants to download a URL as markdown, save web content locally, process a list of URLs into markdown files, or grab readable text from a web page. Always use this skill rather than building curl commands to r.jina.ai yourself.
license: MIT
metadata:
  author: onestepplus
  version: "1.1"
---

# Jina Reader

Download clean markdown from URLs via [r.jina.ai](https://jina.ai/reader) and save to local files.

> **Privacy:** URLs are sent to Jina AI for processing. Only use with URLs you're comfortable sharing.

## How It Works

Run the bundled Python script. It calls the r.jina.ai API, extracts the markdown content from the response, and writes one `.md` file per URL with source metadata in the frontmatter. The markdown is saved to disk, not loaded into your context.

The script lives at: `scripts/jina-reader.py` (relative to this skill's directory).

## Quick Start

Single URL:

```bash
python <skill-path>/scripts/jina-reader.py https://example.com/article
```

Multiple URLs:

```bash
python <skill-path>/scripts/jina-reader.py https://one.com https://two.com https://three.com
```

Bulk from a file (one URL per line, `#` comments and blank lines ignored):

```bash
python <skill-path>/scripts/jina-reader.py --input-file urls.txt
```

Output goes to `docs/sources/` by default. Override with `--output-dir`:

```bash
python <skill-path>/scripts/jina-reader.py https://example.com --output-dir ./saved-pages
```

## Presets

Presets bundle common header configurations. Pass them with `--preset`:

| Preset | What it does |
|--------|-------------|
| `default` | Clean markdown, strips nav/header/footer/aside and images |
| `full-page` | Full page as markdown, nothing stripped |
| `text-only` | Main content only, no images or links, strips page chrome |
| `wait-for-content` | Waits up to 30s for JS-rendered content before extracting |

```bash
python <skill-path>/scripts/jina-reader.py --preset text-only https://example.com
```

If no preset is specified, the script uses Jina Reader's own defaults (full markdown with images and links).

## Override Options

Override or combine with presets:

```bash
python <skill-path>/scripts/jina-reader.py https://example.com \
  --preset default \
  --retain-images all \
  --target-selector "article.main-content"
```

| Flag | Values | Effect |
|------|--------|--------|
| `--retain-images` | `none`, `all`, `alt`, `all_p`, `alt_p` | Control image inclusion |
| `--retain-links` | `none`, `all`, `text`, `gpt-oss` | Control link inclusion |
| `--remove-selector` | CSS selector | Remove matching elements |
| `--target-selector` | CSS selector | Extract only matching elements |
| `--wait-for-selector` | CSS selector | Wait for element before extracting |
| `--respond-timing` | `html`, `network-idle` | When to consider the page ready |
| `--page-timeout` | seconds (1-180) | Reader-side page load timeout |
| `--no-cache` | flag | Bypass Jina's cached content |
| `--timeout` | seconds | Local HTTP request timeout (default: 60) |

## Output Format

Each saved file includes frontmatter:

```md
---
source_url: https://example.com/page
title: Example Page
fetched_at: 2026-05-03T12:34:56+00:00
---

(markdown content here)
```

Filenames are derived from the page title or URL path, deduplicated automatically.

## Authentication

If `JINA_API_KEY` is set in the environment, the script uses it for higher rate limits. Without a key, the free tier applies (20 RPM). The script has a built-in default key for convenience.

## When to Use This Skill

- User asks to fetch/download/save a URL as markdown
- User has a list of URLs to process in bulk
- User wants to read a web page or PDF and save it locally
- User wants clean text from a web page without boilerplate

When the user wants web content, reach for the script. Do not build curl commands to r.jina.ai yourself -- the script handles authentication, presets, error handling, and file saving.

## Troubleshooting

- **Empty content from `text-only`**: Some sites don't use `<main>`. The script will need a manual `--target-selector` pointing at the right element, or try `--preset default` instead.
- **JS-heavy pages returning stubs**: Use `--preset wait-for-content`. If still incomplete, add `--wait-for-selector .your-content-class`.
- **Rate limited**: Set `JINA_API_KEY` in your environment for 500 RPM.

## API Reference

- [Jina Reader docs](https://jina.ai/reader)
- [OpenAPI spec](https://r.jina.ai/openapi.json)
