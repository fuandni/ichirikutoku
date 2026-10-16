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


def patch_focus(html: str) -> str:
    """Add a separate link card for the relocated SA focus exercises."""
    focus_id = 'id="sa-focus-card"'
    if focus_id in html:
        if html.count(focus_id) != 1 or 'href="/home/focus/"' not in html:
            raise ValueError("Existing SA focus card is malformed")
        return html
    anchors = list(re.finditer(r"<a\\b[^>]*>.*?</a\\s*>", html, re.I | re.S))
    matches = [m for m in anchors if CARD_ID in m.group(0)]
    if len(matches) != 1:
        raise ValueError("Expected one SA morning card before adding focus link")
    src = matches[0].group(0)
    dest = src.replace(CARD_ID, focus_id, 1).replace('href="/sa/"', 'href="/home/focus/"', 1)
    dest = dest.replace("システムアーキテクト・午前過去問", "SA・弱点集中演習", 1)
    dest = dest.replace(
        "午前I・午前IIを年度別に演習。成績や学習履歴も管理。",
        "基礎・応用・計算問題を6分野別に演習。進捗と苦手を記録。", 1,
    )
    if dest == src or 'href="/home/focus/"' not in dest:
        raise ValueError("Unable to construct focus card")
    updated = html[:matches[0].end()] + "\n" + dest + html[matches[0].end():]
    updated = updated.replace("6教材を1階層で直接選択。", "7教材を1階層で直接選択。")
    if updated.count(focus_id) != 1:
        raise ValueError("Focus card insertion failed")
    return updated


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_home_sa_link.py /path/to/home/index.html")
    path = Path(sys.argv[1])
    before = path.read_text(encoding="utf-8")
    after = patch_focus(patch(before))
    if after != before:
        path.write_text(after, encoding="utf-8")
        print("Added System Architect card to /home")
    else:
        print("System Architect card already installed")
    assert patch_focus(patch(after)) == after


if __name__ == "__main__":
    main()
