#!/usr/bin/env python3
"""unslop-ko: 기호 세기와 숫자 대조. 외부 라이브러리 없이 돈다. 글을 고치지 않는다.

  python3 unslop_check.py count  원문.txt
  python3 unslop_check.py compare 원문.txt 고친글.txt

count   기호와 그 밖의 AI 티 개수, 고를 길(short 또는 full)을 JSON으로 낸다.
        길은 글자 수로만 고른다. 500자 이하면 short, 넘으면 full이다.
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
BOLD_LEAD = re.compile(r"^\s*(?:[-*]\s+)?\*\*[^*\n]+\*\*", re.M)
LABEL_LINE = re.compile(r"^\s*(?:[-*]\s+)?[^\s:：|][^:：|\n]{0,14}[:：]\s+\S", re.M)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def marks(text):
    return {m: text.count(m) for m in MARKS}


def nums(text):
    return Counter(NUM.findall(text))


def others(text):
    """기호 말고 눈으로 놓치기 쉬운 AI 티. 진단 에이전트에게 참고로 넘긴다."""
    return {
        "bold_lead": len(BOLD_LEAD.findall(text)),
        "parenthesis": text.count("("),
        "label_line": len(LABEL_LINE.findall(text)),
        "not_x_but_y": text.count("아니라"),
        "quote_pair": (text.count('"') + text.count("“") + text.count("”")) // 2,
    }


def count(path):
    text = read(path)
    m = marks(text)
    route = "short" if len(text) <= SHORT_MAX_CHARS else "full"
    return {"chars": len(text), "marks": m, "mark_total": sum(m.values()), "others": others(text), "route": route}, 0


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
