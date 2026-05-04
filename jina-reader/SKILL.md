---
name: jina-reader
description: Use r.jina.ai to save web pages, articles, PDFs, and URL lists as local markdown files. Use when the user asks to fetch, read, convert, or save URLs to markdown with Jina Reader.
license: MIT
compatibility: Requires Python 3 and internet access
metadata:
  author: onestepplus
  version: "1.0"
---

# Jina AI — Reader

Web reading powered by Jina AI. Fetch clean markdown from URLs with `r.jina.ai`.

> **Trust & Privacy:** By using this skill, URLs are transmitted to Jina AI (`jina.ai`). Only use this skill if you are comfortable sending those URLs to Jina.

## Security & Privacy

- **Authentication:** If `JINA_API_KEY` is set, the helper script sends an `Authorization` header. Without a key, Reader still works (free tier: 20 RPM). All presets work with or without a key.
- **Data sent:** URLs you provide are sent to Jina's servers for processing
- **Local files:** No local files are sent to Jina
- **Local storage:** This skill saves markdown files locally in your repo
- **Environment access:** The helper script optionally reads `JINA_API_KEY`

## Endpoint

| Endpoint | Base URL | Purpose |
| --- | --- | --- |
| **Reader** | `https://r.jina.ai/{url}` | Convert any URL to clean markdown |

`Authorization: Bearer $JINA_API_KEY` is optional, but useful for higher rate limits.

---

## Reader API (`r.jina.ai`)

Fetches any URL and returns clean, LLM-friendly content. Works with web pages, PDFs, and JS-heavy sites.

### Basic Usage

```bash
# Plain text output
curl -s "https://r.jina.ai/https://example.com" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "Accept: text/plain"

# JSON output (includes url, title, content, timestamp)
curl -s "https://r.jina.ai/https://example.com" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "Accept: application/json"
```

Or use the bundled helper script. Resolve `scripts/jina-reader.py` relative to this skill directory, but run it from the user's current project directory so output is saved in that project:

```bash
python3 <skill-dir>/scripts/jina-reader.py <url> [<url> ...]
```

You can also pass a text file with one URL per line:

```bash
python3 <skill-dir>/scripts/jina-reader.py --input-file urls.txt
```

By default, the helper script saves markdown files to `docs/sources/`.

## Custom Presets

These are this skill's presets. They are not the same as Jina Reader's own API defaults.

- `default` - clean markdown with common page chrome removed and images stripped
- `full-page` - keep the full page output
- `text-only` - target `main`, strip images, strip links
- `wait-for-content` - use `X-Respond-Timing: network-idle` and `X-Timeout: 30`; if that still fails, try again with `--wait-for-selector`

Use them like this:

```bash
python3 <skill-dir>/scripts/jina-reader.py --preset default <url>
```

### Parameters (via headers)

#### Content Control

| Header | Values | Default | Description |
| --- | --- | --- | --- |
| `X-Respond-With` | `content`, `markdown`, `html`, `text`, `screenshot`, `pageshot`, `vlm`, `readerlm-v2` | `content` | Output format |
| `X-Retain-Images` | `none`, `all`, `alt`, `all_p`, `alt_p` | `all` | Image handling |
| `X-Retain-Links` | `none`, `all`, `text`, `gpt-oss` | `all` | Link handling |
| `X-With-Generated-Alt` | `true` / `false` | `false` | Auto-caption images |
| `X-With-Links-Summary` | `true` | - | Append links section |
| `X-With-Images-Summary` | `true` / `false` | `false` | Append images section |
| `X-Token-Budget` | number | - | Max tokens for response |

#### CSS Selectors

| Header | Description |
| --- | --- |
| `X-Target-Selector` | Only extract matching elements |
| `X-Wait-For-Selector` | Wait for elements before extracting |
| `X-Remove-Selector` | Remove elements before extraction |

#### Browser & Network

| Header | Description |
| --- | --- |
| `X-Timeout` | Page load timeout (1-180s) |
| `X-Respond-Timing` | When page is "ready" (`html`, `network-idle`, etc.) |
| `X-No-Cache` | Bypass cached content |
| `X-Proxy` | Country code or `auto` for proxy |
| `X-Set-Cookie` | Forward cookies for authenticated content |

The helper script also exposes:
- `--preset` for the custom presets above
- `--respond-timing` to set `X-Respond-Timing`
- `--page-timeout` to set `X-Timeout`
- `--no-cache` to set `X-No-Cache: true`

### Common Patterns

```bash
# Extract main content, remove navigation elements
curl -s "https://r.jina.ai/https://example.com/article" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "X-Retain-Images: none" \
  -H "X-Remove-Selector: nav, footer, .sidebar, .ads" \
  -H "Accept: text/plain"

# Extract specific section
curl -s "https://r.jina.ai/https://example.com" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "X-Target-Selector: article.main-content"

# Parse a PDF
curl -s "https://r.jina.ai/https://example.com/paper.pdf" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "Accept: text/plain"

# Wait for dynamic content
curl -s "https://r.jina.ai/https://spa-app.com" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "X-Wait-For-Selector: .loaded-content" \
  -H "X-Respond-Timing: network-idle"
```

## Helper Script

| Script | Purpose |
| --- | --- |
| `scripts/jina-reader.py` | Read one or more URLs via `r.jina.ai` and save local output files |

The helper script supports:
- `--preset default|full-page|text-only|wait-for-content`
- direct URL arguments or `--input-file`
- `--output-dir` for where files are written
- `--remove-selector`, `--target-selector`, `--wait-for-selector`
- `--retain-images`, `--retain-links`
- `--respond-timing`, `--page-timeout`, `--no-cache`
- `--insecure` for local-dev certificate issues

## Output

The helper script saves one local file per URL. Markdown files include frontmatter like:

```md
---
source_url: https://example.com/page
title: Example Page
fetched_at: 2026-05-03T12:34:56Z
---
```

Then the Reader markdown content follows.

## Rate Limits

- **No key:** 20 RPM (all presets and headers still work)
- **Free API key:** 500 RPM
- If you hit rate limits without a key, set `JINA_API_KEY` and retry

## API Docs

- Reader: [https://jina.ai/reader](https://jina.ai/reader)
- OpenAPI spec: [https://r.jina.ai/openapi.json](https://r.jina.ai/openapi.json)

## When to Use

- Fetch a URL as clean markdown
- Parse a PDF from a URL
- Strip navigation or boilerplate before extraction (use selector headers)
- Save one or many URLs to local markdown files (use `scripts/jina-reader.py`)
