#!/usr/bin/env python3
"""Local automation for TikDownloader capture flow (no CLI input required)."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlencode
from urllib.request import Request, urlopen

REQUEST_BODY_PATH = Path("00012_POST_tikdownloader.io_api_ajaxSearch/02-request-body.txt")
API_URL = "https://tikdownloader.io/api/ajaxSearch"
DEFAULT_QUERY = "https://vt.tiktok.com/ZS5cvC8ua/"
DEFAULT_LANG = "id"


@dataclass(frozen=True)
class DownloadLink:
    label: str
    url: str


class DownloadLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_link = False
        self._current_href: str | None = None
        self._current_label: list[str] = []
        self.links: list[DownloadLink] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr_map = {name: value for name, value in attrs}
        class_value = attr_map.get("class", "") or ""
        if "tik-button-dl" not in class_value:
            return
        href = attr_map.get("href")
        if not href:
            return
        self._in_link = True
        self._current_href = href
        self._current_label = []

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._in_link or not self._current_href:
            return
        label = "".join(self._current_label).strip() or "download"
        self.links.append(DownloadLink(label=label, url=self._current_href))
        self._in_link = False
        self._current_href = None
        self._current_label = []

    def handle_data(self, data: str) -> None:
        if self._in_link:
            self._current_label.append(data)


@dataclass(frozen=True)
class ConvertMetadata:
    exp: str | None
    token: str | None
    url: str | None


def load_request_payload() -> dict[str, str]:
    if REQUEST_BODY_PATH.exists():
        raw = REQUEST_BODY_PATH.read_text(encoding="utf-8").strip()
        parsed = parse_qs(raw, keep_blank_values=True)
        query = parsed.get("q", [DEFAULT_QUERY])[0]
        lang = parsed.get("lang", [DEFAULT_LANG])[0]
        return {"q": query, "lang": lang}
    return {"q": DEFAULT_QUERY, "lang": DEFAULT_LANG}


def post_search(payload: dict[str, str]) -> dict[str, str]:
    data = urlencode(payload).encode("utf-8")
    request = Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (local-script)",
        },
    )
    with urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def parse_download_links(html: str) -> list[DownloadLink]:
    parser = DownloadLinkParser()
    parser.feed(html)
    return parser.links


def parse_convert_metadata(html: str) -> ConvertMetadata:
    exp = re.search(r'k_exp\s*=\s*"(\d+)"', html)
    token = re.search(r'k_token\s*=\s*"([a-f0-9]+)"', html)
    url = re.search(r'k_url_convert\s*=\s*"(https?://[^"]+)"', html)
    return ConvertMetadata(
        exp=exp.group(1) if exp else None,
        token=token.group(1) if token else None,
        url=url.group(1) if url else None,
    )


def print_links(links: Iterable[DownloadLink]) -> None:
    print("Download links:")
    for link in links:
        print(f"- {link.label}: {link.url}")


def print_metadata(metadata: ConvertMetadata) -> None:
    print("\nConvert metadata:")
    print(f"- k_exp: {metadata.exp or 'n/a'}")
    print(f"- k_token: {metadata.token or 'n/a'}")
    print(f"- k_url_convert: {metadata.url or 'n/a'}")


def main() -> int:
    payload = load_request_payload()
    print(f"Using payload: {payload}")
    try:
        response = post_search(payload)
    except Exception as exc:
        print(f"Request failed: {exc}")
        return 1

    if response.get("status") != "ok":
        print("Response status not ok:", response)
        return 1

    html = response.get("data", "")
    links = parse_download_links(html)
    metadata = parse_convert_metadata(html)
    print_links(links)
    print_metadata(metadata)
    return 0


if __name__ == "__main__":
    sys.exit(main())
