import re

import render


def marks(html):
    """하이라이트된 (번호, 구간 HTML) 목록."""
    return re.findall(r"<mark[^>]*><b[^>]*>(\d+)</b>(.*?)</mark>", html, re.DOTALL)


def test_find_spans_exact_all_occurrences():
    assert render.find_spans("가나 가나 다", "가나") == [(0, 2), (3, 5)]


def test_find_spans_whitespace_normalized():
    text = "Click  the\nbutton."
    assert render.find_spans(text, "the button") == [(7, 17)]
    assert render.find_spans(text, " Click the ") == [(0, 10)]


def test_find_spans_exact_preferred_over_normalized():
    # 정확 일치가 있으면 공백 정규화 일치는 찾지 않는다.
    assert render.find_spans("a b, a  b", "a b") == [(0, 3)]


def test_find_spans_missing_or_empty():
    assert render.find_spans("가나다", "라마") == []
    assert render.find_spans("가나다", "") == []
    assert render.find_spans("가나다", "  ") == []


def test_highlight_escapes_text_and_span():
    html = render.highlight("<script>alert(1)</script> & 끝", [(1, "<script>")])
    assert "<script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt; &amp; 끝" in re.sub(r"<mark[^>]*><b[^>]*>1</b>|</mark>", "", html)
    assert marks(html) == [("1", "&lt;script&gt;")]


def test_highlight_escapes_quotes():
    html = render.highlight('"따옴표" \'작은\'', [])
    assert html == "&quot;따옴표&quot; &#x27;작은&#x27;"


def test_highlight_marks_every_occurrence():
    html = render.highlight("사과와 사과", [(2, "사과")])
    assert marks(html) == [("2", "사과"), ("2", "사과")]


def test_highlight_whitespace_difference_keeps_original_text():
    html = render.highlight("A\nB C", [(1, "A B")])
    assert marks(html) == [("1", "A\nB")]
    assert html.endswith("</mark> C")


def test_highlight_overlap_earlier_start_wins():
    # "나다"는 "가나"와 겹치므로 하이라이트하지 않는다.
    html = render.highlight("가나다라", [(2, "나다"), (1, "가나"), (3, "라")])
    assert marks(html) == [("1", "가나"), ("3", "라")]


def test_highlight_overlap_same_start_lower_number_wins():
    html = render.highlight("가나다", [(2, "가나다"), (1, "가")])
    assert marks(html) == [("1", "가")]


def test_highlight_missing_span_leaves_text():
    assert render.highlight("가나다", [(1, "없음"), (2, "")]) == "가나다"


def test_highlight_uses_inline_style_only():
    html = render.page(render.columns(render.highlight("가", [(1, "가")]), "나"))
    assert "<style" not in html
    assert "class=" not in html
    assert "background:#fff" in html


def test_details_escapes_summary_and_keeps_body():
    html = render.details("행 <1>", "<b>본문</b>")
    assert html.startswith("<details")
    assert "행 &lt;1&gt;" in html
    assert "<b>본문</b>" in html
    assert " open" not in html  # 기본 접힘
