#!/usr/bin/env python3
"""Tavily toolkit for OpenClaw skill.

Supports subcommands:
- search
- extract
- crawl
- map

All commands support:
- API key from TAVILY_API_KEY or ~/.openclaw/.env
- proxy controls (--proxy / --no-proxy)
- timeout + retry
- output formats (raw/brave/md for search; raw/md for others)
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from typing import Any

API_BASE = "https://api.tavily.com"


def load_key() -> str | None:
    key = os.environ.get("TAVILY_API_KEY")
    if key:
        return key.strip()

    env_path = pathlib.Path.home() / ".openclaw" / ".env"
    if env_path.exists():
        txt = env_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^\s*TAVILY_API_KEY\s*=\s*(.+?)\s*$", txt, re.M)
        if m:
            v = m.group(1).strip().strip('"').strip("'")
            if v:
                return v
    return None


def make_opener(proxy: str | None, no_proxy: bool):
    if no_proxy:
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    if proxy:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
    return urllib.request.build_opener()


def post_json(
    endpoint: str,
    payload: dict[str, Any],
    *,
    proxy: str | None,
    no_proxy: bool,
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    key = load_key()
    if not key:
        raise SystemExit(
            "Missing TAVILY_API_KEY. Set env var TAVILY_API_KEY or add it to ~/.openclaw/.env"
        )

    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )

    opener = make_opener(proxy=proxy, no_proxy=no_proxy)
    attempts = max(1, retries + 1)
    last_err: Exception | None = None

    for i in range(attempts):
        try:
            with opener.open(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:400]
            # Retry on 429/5xx, fail fast otherwise.
            if e.code in (429, 500, 502, 503, 504) and i < attempts - 1:
                time.sleep(1.5 * (i + 1))
                continue
            raise SystemExit(f"Tavily HTTP {e.code}: {detail}")
        except (urllib.error.URLError, socket.timeout, json.JSONDecodeError) as e:
            last_err = e
            if i < attempts - 1:
                time.sleep(1.5 * (i + 1))
                continue
            break

    raise SystemExit(f"Tavily request failed: {last_err}")


def to_markdown_search(obj: dict[str, Any], snippet_max_chars: int) -> str:
    lines: list[str] = []
    if obj.get("answer"):
        lines.append(str(obj["answer"]).strip())
        lines.append("")

    for i, r in enumerate(obj.get("results") or [], 1):
        title = (r.get("title") or "").strip() or r.get("url") or "(no title)"
        url = r.get("url") or ""
        snippet = (r.get("content") or "").strip()
        if len(snippet) > snippet_max_chars:
            snippet = snippet[:snippet_max_chars].rstrip() + "..."

        lines.append(f"{i}. {title}")
        if url:
            lines.append(f"   {url}")
        if snippet:
            lines.append(f"   - {snippet}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def to_markdown_generic(obj: dict[str, Any], limit: int = 20) -> str:
    lines: list[str] = []
    if "base_url" in obj:
        lines.append(f"Base URL: {obj.get('base_url')}")
    if "response_time" in obj:
        lines.append(f"Response time: {obj.get('response_time')}s")
    if "results" in obj and isinstance(obj["results"], list):
        lines.append(f"Results: {len(obj['results'])}")
        lines.append("")
        for i, r in enumerate(obj["results"][:limit], 1):
            url = r.get("url") or r.get("source_url") or ""
            title = r.get("title") or url or f"item-{i}"
            lines.append(f"{i}. {title}")
            if url:
                lines.append(f"   {url}")
            content = (r.get("content") or r.get("raw_content") or "").strip()
            if content:
                lines.append(f"   - {content[:220].rstrip()}" + ("..." if len(content) > 220 else ""))
            lines.append("")
    else:
        lines.append(json.dumps(obj, ensure_ascii=False, indent=2))
    return "\n".join(lines).rstrip() + "\n"


def do_search(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {
        "query": args.query,
        "max_results": max(1, min(args.max_results, 20)),
        "search_depth": args.search_depth,
        "topic": args.topic,
        "include_answer": bool(args.include_answer),
        "include_images": bool(args.include_images),
        "include_image_descriptions": bool(args.include_image_descriptions),
        "include_raw_content": bool(args.include_raw_content),
        "include_favicon": bool(args.include_favicon),
    }
    if args.include_domains:
        payload["include_domains"] = [d.strip() for d in args.include_domains.split(",") if d.strip()]
    if args.exclude_domains:
        payload["exclude_domains"] = [d.strip() for d in args.exclude_domains.split(",") if d.strip()]
    if args.country:
        payload["country"] = args.country
    if args.time_range:
        payload["time_range"] = args.time_range
    if args.start_date:
        payload["start_date"] = args.start_date
    if args.end_date:
        payload["end_date"] = args.end_date
    if args.search_depth == "advanced":
        payload["chunks_per_source"] = max(1, min(args.chunks_per_source, 3))

    obj = post_json(
        "search",
        payload,
        proxy=args.proxy,
        no_proxy=args.no_proxy,
        timeout=max(5, args.timeout),
        retries=max(0, args.retries),
    )

    raw = {
        "query": args.query,
        "answer": obj.get("answer"),
        "results": [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content"),
                "score": r.get("score"),
            }
            for r in (obj.get("results") or [])[: args.max_results]
        ],
    }
    if not args.include_answer:
        raw.pop("answer", None)

    if args.format == "md":
        sys.stdout.write(to_markdown_search(raw, snippet_max_chars=args.snippet_max_chars))
        return 0

    if args.format == "brave":
        brave = {
            "query": raw.get("query"),
            "results": [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "snippet": ((r.get("content") or "")[: args.snippet_max_chars]).rstrip()
                    + ("..." if len(r.get("content") or "") > args.snippet_max_chars else ""),
                }
                for r in raw.get("results") or []
            ],
        }
        if "answer" in raw:
            brave["answer"] = raw.get("answer")
        json.dump(brave, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    json.dump(raw, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def do_extract(args: argparse.Namespace) -> int:
    urls = [u.strip() for u in args.urls.split(",") if u.strip()]
    payload: dict[str, Any] = {
        "urls": urls if len(urls) > 1 else (urls[0] if urls else ""),
        "extract_depth": args.extract_depth,
        "include_images": bool(args.include_images),
        "include_favicon": bool(args.include_favicon),
        "format": args.content_format,
    }
    if args.query:
        payload["query"] = args.query
        payload["chunks_per_source"] = max(1, min(args.chunks_per_source, 5))

    obj = post_json(
        "extract",
        payload,
        proxy=args.proxy,
        no_proxy=args.no_proxy,
        timeout=max(5, args.timeout),
        retries=max(0, args.retries),
    )

    if args.format == "md":
        sys.stdout.write(to_markdown_generic(obj))
    else:
        json.dump(obj, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


def _regex_list(v: str | None) -> list[str] | None:
    if not v:
        return None
    arr = [x.strip() for x in v.split(",") if x.strip()]
    return arr or None


def do_map_or_crawl(args: argparse.Namespace, endpoint: str) -> int:
    payload: dict[str, Any] = {
        "url": args.url,
        "max_depth": max(1, min(args.max_depth, 5)),
        "max_breadth": max(1, min(args.max_breadth, 500)),
        "limit": max(1, args.limit),
        "allow_external": bool(args.allow_external),
        "include_images": bool(args.include_images),
    }
    if args.instructions:
        payload["instructions"] = args.instructions
    if endpoint == "crawl":
        payload["extract_depth"] = args.extract_depth
        payload["format"] = args.content_format
        if args.instructions:
            payload["chunks_per_source"] = max(1, min(args.chunks_per_source, 5))

    for key, val in {
        "select_paths": _regex_list(args.select_paths),
        "exclude_paths": _regex_list(args.exclude_paths),
        "select_domains": _regex_list(args.select_domains),
        "exclude_domains": _regex_list(args.exclude_domains),
    }.items():
        if val:
            payload[key] = val

    obj = post_json(
        endpoint,
        payload,
        proxy=args.proxy,
        no_proxy=args.no_proxy,
        timeout=max(5, args.timeout),
        retries=max(0, args.retries),
    )

    if args.format == "md":
        sys.stdout.write(to_markdown_generic(obj, limit=args.md_limit))
    else:
        json.dump(obj, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


def add_common_net_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--proxy", default=None, help="Explicit proxy, e.g. http://127.0.0.1:7890")
    ap.add_argument("--no-proxy", action="store_true", help="Disable all proxies")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--retries", type=int, default=1)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Tavily toolkit for OpenClaw")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # search
    s = sub.add_parser("search", help="Search the web")
    s.add_argument("--query", required=True)
    s.add_argument("--max-results", type=int, default=5)
    s.add_argument("--search-depth", choices=["advanced", "basic", "fast", "ultra-fast"], default="basic")
    s.add_argument("--topic", choices=["general", "news"], default="general")
    s.add_argument("--include-answer", action="store_true")
    s.add_argument("--include-images", action="store_true")
    s.add_argument("--include-image-descriptions", action="store_true")
    s.add_argument("--include-raw-content", action="store_true")
    s.add_argument("--include-favicon", action="store_true")
    s.add_argument("--include-domains", default=None, help="Comma-separated domains")
    s.add_argument("--exclude-domains", default=None, help="Comma-separated domains")
    s.add_argument("--country", default=None)
    s.add_argument("--time-range", choices=["day", "week", "month", "year"], default=None)
    s.add_argument("--start-date", default=None, help="YYYY-MM-DD")
    s.add_argument("--end-date", default=None, help="YYYY-MM-DD")
    s.add_argument("--chunks-per-source", type=int, default=3)
    s.add_argument("--format", choices=["raw", "brave", "md"], default="brave")
    s.add_argument("--snippet-max-chars", type=int, default=400)
    add_common_net_args(s)
    s.set_defaults(func=do_search)

    # extract
    e = sub.add_parser("extract", help="Extract page content from URLs")
    e.add_argument("--urls", required=True, help="Comma-separated URLs")
    e.add_argument("--query", default=None, help="Optional rerank intent")
    e.add_argument("--chunks-per-source", type=int, default=3)
    e.add_argument("--extract-depth", choices=["basic", "advanced"], default="basic")
    e.add_argument("--include-images", action="store_true")
    e.add_argument("--include-favicon", action="store_true")
    e.add_argument("--content-format", choices=["markdown", "text"], default="markdown")
    e.add_argument("--format", choices=["raw", "md"], default="raw")
    add_common_net_args(e)
    e.set_defaults(func=do_extract)

    # crawl
    c = sub.add_parser("crawl", help="Crawl website with extraction")
    c.add_argument("--url", required=True)
    c.add_argument("--instructions", default=None)
    c.add_argument("--max-depth", type=int, default=1)
    c.add_argument("--max-breadth", type=int, default=20)
    c.add_argument("--limit", type=int, default=50)
    c.add_argument("--select-paths", default=None)
    c.add_argument("--exclude-paths", default=None)
    c.add_argument("--select-domains", default=None)
    c.add_argument("--exclude-domains", default=None)
    c.add_argument("--allow-external", action="store_true")
    c.add_argument("--include-images", action="store_true")
    c.add_argument("--chunks-per-source", type=int, default=3)
    c.add_argument("--extract-depth", choices=["basic", "advanced"], default="basic")
    c.add_argument("--content-format", choices=["markdown", "text"], default="markdown")
    c.add_argument("--format", choices=["raw", "md"], default="raw")
    c.add_argument("--md-limit", type=int, default=20)
    add_common_net_args(c)
    c.set_defaults(func=lambda a: do_map_or_crawl(a, "crawl"))

    # map
    m = sub.add_parser("map", help="Map website links")
    m.add_argument("--url", required=True)
    m.add_argument("--instructions", default=None)
    m.add_argument("--max-depth", type=int, default=1)
    m.add_argument("--max-breadth", type=int, default=20)
    m.add_argument("--limit", type=int, default=50)
    m.add_argument("--select-paths", default=None)
    m.add_argument("--exclude-paths", default=None)
    m.add_argument("--select-domains", default=None)
    m.add_argument("--exclude-domains", default=None)
    m.add_argument("--allow-external", action="store_true")
    m.add_argument("--include-images", action="store_true")
    m.add_argument("--format", choices=["raw", "md"], default="raw")
    m.add_argument("--md-limit", type=int, default=20)
    add_common_net_args(m)
    m.set_defaults(func=lambda a: do_map_or_crawl(a, "map"))

    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
