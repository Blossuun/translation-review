"""결과 HTML 생성. 인라인 style만 쓰고 흰 배경을 명시한다 (명세 6절)."""

import html
import re

_PAGE = (
    "background:#fff;color:#1f2328;padding:12px;border-radius:6px;"
    "font-family:sans-serif;font-size:14px;line-height:1.6"
)
_MARK = "background:#fff3a3;color:#1f2328;padding:0 2px;border-radius:3px"
_NUM = (
    "display:inline-block;background:#d1242f;color:#fff;font-size:11px;"
    "line-height:16px;min-width:16px;text-align:center;border-radius:8px;margin-right:2px"
)
_COLUMN = "flex:1;min-width:0;white-space:pre-wrap;border:1px solid #d0d7de;border-radius:6px;padding:8px"


def find_spans(text, span):
    """text에서 span이 나오는 모든 (시작, 끝) 위치.

    정확 일치를 먼저 찾고, 없으면 공백 연속을 하나로 보고 다시 찾는다.
    """
    if not span.strip():
        return []
    found = [(m.start(), m.end()) for m in re.finditer(re.escape(span), text)]
    if found:
        return found
    pattern = r"\s+".join(re.escape(w) for w in span.split())
    return [(m.start(), m.end()) for m in re.finditer(pattern, text)]


def highlight(text, spans):
    """text를 이스케이프하고 지적 구간에 번호를 붙여 하이라이트한다.

    spans: (번호, 구간 문자열) 목록. 같은 구간이 여러 번 나오면 모두 표시한다.
    구간이 겹치면 먼저 시작하는 구간(같으면 번호가 작은 쪽)만 표시한다.
    """
    hits = sorted(
        (start, num, end) for num, span in spans for start, end in find_spans(text, span)
    )
    out, pos = [], 0
    for start, num, end in hits:
        if start < pos:
            continue
        out.append(html.escape(text[pos:start]))
        out.append(
            f'<mark style="{_MARK}"><b style="{_NUM}">{num}</b>'
            f"{html.escape(text[start:end])}</mark>"
        )
        pos = end
    out.append(html.escape(text[pos:]))
    return "".join(out)


def columns(left, right):
    """원문·번역문 HTML을 좌우 2단으로 놓는다. 줄바꿈은 원본대로 보인다."""
    return (
        '<div style="display:flex;gap:12px">'
        f'<div style="{_COLUMN}">{left}</div>'
        f'<div style="{_COLUMN}">{right}</div>'
        "</div>"
    )


def details(summary, body):
    """접고 펼치는 영역 (기본 접힘). summary는 평문, body는 HTML."""
    return (
        '<details style="margin:6px 0">'
        f'<summary style="cursor:pointer">{html.escape(summary)}</summary>'
        f'<div style="margin-top:6px">{body}</div>'
        "</details>"
    )


def page(body):
    """결과 전체를 흰 배경 상자로 감싼다 (다크 테마에서도 읽히게)."""
    return f'<div style="{_PAGE}">{body}</div>'
