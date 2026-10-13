#!/usr/bin/env python3
"""Append a SA morning practice card to the existing published /home portal."""
from pathlib import Path
import re
import sys

SOURCE_ID = 'id="law-yearly-exam-card"'
CARD_ID = 'id="sa-morning-db-card"'
TARGET = "/sa/"


def patch(html: str) -> str:
    if CARD_ID in html:
        if html.count(CARD_ID) != 1 or not re.search(
            r'<a\b[^>]*\bid="sa-morning-db-card"[^>]*\bhref="/sa/"|<a\b[^>]*\bhref="/sa/"[^>]*\bid="sa-morning-db-card"',
            html, flags=re.I | re.S
        ):
            raise ValueError("Existing SA card is malformed; refusing modification")
        return html

    if "</body>" not in html.lower():
        raise ValueError("Missing body closing tag")
    anchors = list(re.finditer(r"<a\b[^>]*>.*?</a\s*>", html, re.I | re.S))
    matches = [m for m in anchors if SOURCE_ID in m.group(0)]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one law-yearly-exam card, got {len(matches)}")
    anchor = matches[0]
    template = anchor.group(0)
    if (
        "法規・試験回別演習" not in template
        or "年度・午前午後別の12問を自動採点。結果や履歴も保存。" not in template
    ):
        raise ValueError("Source card content differs from audited live portal")

    tag, rest = template.split(">", 1)
    tag = re.sub(
        r"(\bhref\s*=\s*)([\"'])[^\"']*\2",
        lambda m: m.group(1) + m.group(2) + TARGET + m.group(2),
        tag, count=1, flags=re.I,
    )
    tag = tag.replace(SOURCE_ID, CARD_ID, 1)
    clone = tag + ">" + rest
    clone = clone.replace("法規・試験回別演習", "システムアーキテクト・午前過去問", 1)
    clone = clone.replace(
        "年度・午前午後別の12問を自動採点。結果や履歴も保存。",
        "午前I・午前IIを年度別に演習。成績や学習履歴も管理。", 1,
    )
    clone = clone.replace("法規", "情報処理")

    updated = html[:anchor.end()] + "\n" + clone + html[anchor.end():]
    updated = updated.replace("5教材を1階層で直接選択。", "6教材を1階層で直接選択。")
    updated = updated.replace(
        "法規と無線工学を、ここから直接開く。",
        "法規・無線工学・システムアーキテクトを、ここから直接開く。",
    )
    if updated.count(CARD_ID) != 1 or "/sa/" not in clone:
        raise ValueError("SA card verification failed")
    return updated


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_home_sa_link.py /path/to/home/index.html")
    path = Path(sys.argv[1])
    before = path.read_text(encoding="utf-8")
    after = patch(before)
    if after != before:
        path.write_text(after, encoding="utf-8")
        print("Added System Architect card to /home")
    else:
        print("System Architect card already installed")
    assert patch(after) == after


if __name__ == "__main__":
    main()
