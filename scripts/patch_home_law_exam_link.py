#!/usr/bin/env python3
"""Add a fifth, exam-specific home card without changing existing routes/data."""
from pathlib import Path
import re
import sys

MARKER = 'id="law-yearly-exam-card"'
TARGET = '/houki-practice/#houkiSessionCards'

def patch(html: str) -> str:
    if MARKER in html:
        return html
    if '</body>' not in html.lower():
        raise ValueError("Missing body closing tag")
    cards = list(re.finditer(r'<a\b[^>]*>.*?</a\s*>', html, re.I | re.S))
    matches = [
        m for m in cards
        if '法規・演習' in m.group(0)
        and re.search(r'href\s*=\s*["\'][^"\']*houki-practice/?["\']', m.group(0), re.I)
        and re.search(r'class\s*=\s*["\'][^"\']*\bcard\b', m.group(0), re.I)
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one existing law practice card, got {len(matches)}")
    anchor = matches[0]
    template = anchor.group(0)
    if '問題を解いて知識を確認する。' not in template:
        raise ValueError("Existing law-practice description differs; inspect before patching")

    tag, rest = template.split('>', 1)
    tag = re.sub(
        r'(\bhref\s*=\s*)(["\'])[^"\']*\2',
        lambda m: m.group(1) + m.group(2) + TARGET + m.group(2),
        tag, count=1, flags=re.I,
    )
    tag += ' ' + MARKER
    clone = tag + '>' + rest
    clone = clone.replace('法規・演習', '法規・試験回別演習', 1)
    clone = clone.replace('問題を解いて知識を確認する。',
                          '年度・午前午後別の12問を自動採点。結果や履歴も保存。', 1)
    result = html[:anchor.end()] + '\n' + clone + html[anchor.end():]

    # Keep portal copy accurate: five cards instead of four, responsive two-column grid.
    result = result.replace('4教材を1階層で直接選択。', '5教材を1階層で直接選択。')
    result = result.replace('広い画面では2×2表示。', '広い画面では2列表示。')
    return result

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_home_law_exam_link.py /path/to/home/index.html")
    path = Path(sys.argv[1])
    before = path.read_text(encoding='utf-8')
    after = patch(before)
    if before == after:
        print('Home law-exam card already exists; no changes')
    else:
        path.write_text(after, encoding='utf-8')
        print('Added law exam-session card to home')
    assert after.count(MARKER) == 1
    assert 'href="' + TARGET + '"' in after or "href='" + TARGET + "'" in after

if __name__ == '__main__':
    main()
