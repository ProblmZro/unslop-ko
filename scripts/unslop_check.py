#!/usr/bin/env python3
"""unslop-ko: 기호 세기와 숫자 대조. 외부 라이브러리 없이 돈다. 글을 고치지 않는다.

  python3 unslop_check.py count  원문.txt
  python3 unslop_check.py compare 원문.txt 고친글.txt

count   기호 개수와 고를 길(short 또는 full)을 JSON으로 낸다.
compare 원문에만 있는 숫자, 고친 글에만 있는 숫자, 기호 개수, 바뀐 비율을 낸다.
        숫자가 어긋나면 종료 코드 1, 바뀐 비율이 50%를 넘으면 2.
"""
import difflib
import json
import re
import sys
from collections import Counter

MARKS = "·→—"
NUM = re.compile(r"\d+(?:[.,:/~]\d+)*%?")
SHORT_MAX_CHARS = 500
SHORT_MAX_MARKS = 5


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def marks(text):
    return {m: text.count(m) for m in MARKS}


def nums(text):
    return Counter(NUM.findall(text))


def count(path):
    text = read(path)
    m = marks(text)
    total = sum(m.values())
    short = len(text) <= SHORT_MAX_CHARS or total <= SHORT_MAX_MARKS
    return {"chars": len(text), "marks": m, "mark_total": total, "route": "short" if short else "full"}, 0


def compare(before_path, after_path):
    before, after = read(before_path), read(after_path)
    missing = nums(before) - nums(after)
    added = nums(after) - nums(before)
    rate = 1 - difflib.SequenceMatcher(None, before, after, autojunk=False).ratio()
    out = {
        "missing_numbers": dict(missing),
        "added_numbers": dict(added),
        "marks_before": marks(before),
        "marks_after": marks(after),
        "change_rate": round(rate, 3),
        "numbers_ok": not missing and not added,
    }
    code = 1 if (missing or added) else (2 if rate > 0.5 else 0)
    return out, code


def main(argv):
    if len(argv) == 3 and argv[1] == "count":
        out, code = count(argv[2])
    elif len(argv) == 4 and argv[1] == "compare":
        out, code = compare(argv[2], argv[3])
    else:
        print(__doc__)
        return 64
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
