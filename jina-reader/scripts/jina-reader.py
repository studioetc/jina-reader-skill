#!/usr/bin/env python3
"""Fetch one or more URLs through r.jina.ai and save markdown files."""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List
from urllib import error, parse, request


DEFAULT_JINA_API_KEY = ""  # Set JINA_API_KEY in your environment, or hard-code your own here for personal use. Do not commit a real key.
PRESETS = {
    "default": {
        "headers": {
            "X-Respond-With": "markdown",
            "X-Remove-Selector": "nav, header, footer, aside",
            "X-Retain-Images": "none",
        },
    },
    "full-page": {
        "headers": {
            "X-Respond-With": "markdown",
        },
    },
    "text-only": {
        "headers": {
            "X-Respond-With": "markdown",
            "X-Target-Selector": "main",
            "X-Retain-Images": "none",
            "X-Retain-Links": "none",
            "X-Remove-Selector": "nav, header, footer, aside",
        },
    },
    "wait-for-content": {
        "headers": {
            "X-Respond-With": "markdown",
            "X-Respond-Timing": "network-idle",
            "X-Timeout": "30",
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch URLs through r.jina.ai and save markdown files locally."
    )
    parser.add_argument("urls", nargs="*", help="One or more public URLs to fetch.")
    parser.add_argument(
        "--input-file",
        help="Text file containing one URL per line. Blank lines and # comments are ignored.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/sources",
        help="Folder to write markdown files into. Default: docs/sources",
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS.keys()),
        help="Apply a named preset of Reader headers before any explicit overrides.",
    )
    parser.add_argument(
        "--retain-images",
        choices=["none", "all", "alt", "all_p", "alt_p"],
        help="Override Reader image retention behavior.",
    )
    parser.add_argument(
        "--retain-links",
        choices=["none", "all", "text", "gpt-oss"],
        help="Override Reader link retention behavior.",
    )
    parser.add_argument(
        "--remove-selector",
        help="CSS selectors to remove before extraction.",
    )
    parser.add_argument(
        "--target-selector",
        help="CSS selector to extract instead of the full page.",
    )
    parser.add_argument(
        "--wait-for-selector",
        help="CSS selector Reader should wait for before extracting.",
    )
    parser.add_argument(
        "--respond-timing",
        choices=["html", "network-idle"],
        help="When Reader should consider the page ready.",
    )
    parser.add_argument(
        "--page-timeout",
        type=int,
        help="Reader page load timeout in seconds (1-180).",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ask Reader to bypass cached content.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Local request timeout in seconds for this script. Default: 60",
    )
    parser.add_argument(
        "--insecure",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Disable TLS certificate verification. Default: enabled for local testing.",
    )
    return parser.parse_args()


def load_urls(cli_urls: Iterable[str], input_file: str | None) -> List[str]:
    urls: List[str] = []
    for raw in cli_urls:
        raw = raw.strip()
        if raw:
            urls.append(raw)

    if input_file:
        for line in Path(input_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)

    deduped: List[str] = []
    seen = set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped


def build_headers(args: argparse.Namespace) -> Dict[str, str]:
    headers: Dict[str, str] = {
        "Accept": "application/json",
        "X-Respond-With": "markdown",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        ),
    }

    api_key = os.environ.get("JINA_API_KEY") or DEFAULT_JINA_API_KEY
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if args.preset:
        headers.update(PRESETS[args.preset]["headers"])

    if args.retain_images:
        headers["X-Retain-Images"] = args.retain_images
    if args.retain_links:
        headers["X-Retain-Links"] = args.retain_links
    if args.remove_selector:
        headers["X-Remove-Selector"] = args.remove_selector
    if args.target_selector:
        headers["X-Target-Selector"] = args.target_selector
    if args.wait_for_selector:
        headers["X-Wait-For-Selector"] = args.wait_for_selector
    if args.respond_timing:
        headers["X-Respond-Timing"] = args.respond_timing
    if args.page_timeout is not None:
        headers["X-Timeout"] = str(args.page_timeout)
    if args.no_cache:
        headers["X-No-Cache"] = "true"

    return headers


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "page"


def make_filename(source_url: str, title: str, used_names: set[str]) -> str:
    parsed = parse.urlparse(source_url)
    path_part = parsed.path.rstrip("/").split("/")[-1] if parsed.path else ""
    stem = slugify(title or path_part or parsed.netloc or source_url)
    candidate = f"{stem}.md"
    counter = 2
    while candidate in used_names:
        candidate = f"{stem}-{counter}.md"
        counter += 1
    used_names.add(candidate)
    return candidate


def fetch_reader_json(
    source_url: str,
    headers: Dict[str, str],
    timeout: int,
    insecure: bool,
) -> Dict[str, object]:
    reader_url = f"https://r.jina.ai/{source_url}"
    req = request.Request(reader_url, headers=headers)
    context = ssl._create_unverified_context() if insecure else None
    with request.urlopen(req, timeout=timeout, context=context) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    return json.loads(body)


def unwrap_reader_payload(payload: Dict[str, object]) -> Dict[str, object]:
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload


def build_frontmatter(source_url: str, title: str, fetched_at: str) -> str:
    lines = [
        "---",
        f"source_url: {source_url}",
        f"title: {title or 'Untitled'}",
        f"fetched_at: {fetched_at}",
        "---",
        "",
    ]
    return "\n".join(lines)


def write_markdown(output_path: Path, source_url: str, title: str, content: str) -> None:
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    frontmatter = build_frontmatter(source_url, title, fetched_at)
    output_path.write_text(frontmatter + content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    urls = load_urls(args.urls, args.input_file)

    if not urls:
        print("No URLs provided. Pass URLs directly or use --input-file.", file=sys.stderr)
        return 2

    headers = build_headers(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    used_names: set[str] = set()
    failures = 0

    for url in urls:
        try:
            payload = fetch_reader_json(url, headers, args.timeout, args.insecure)
            data = unwrap_reader_payload(payload)
            source_url = str(data.get("url") or url)
            title = str(data.get("title") or "")
            content = str(data.get("content") or "").strip()

            if not content:
                raise ValueError("Reader returned empty content.")

            filename = make_filename(source_url, title, used_names)
            output_path = output_dir / filename
            write_markdown(output_path, source_url, title, content)
            print(f"Wrote {output_path} <- {source_url}")
        except (error.HTTPError, error.URLError, json.JSONDecodeError, ValueError) as exc:
            failures += 1
            print(f"Failed {url}: {exc}", file=sys.stderr)
            if args.preset == "wait-for-content" and not args.wait_for_selector:
                print(
                    "Tip: try again with --wait-for-selector if the page loads content via JavaScript.",
                    file=sys.stderr,
                )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
