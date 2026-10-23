import pytest

import reviewer

# 가상 프롬프트. 실제 prompt.md와 별개로 파싱·치환 규칙만 확인한다.
SAMPLE = """버전: 1.2

<!-- system -->
지시: {{source_lang}} → {{target_lang}}

<!-- user -->
<guideline>
{{guideline}}
</guideline>
<source>{{source}}</source>
<translation>{{translation}}</translation>
<context>{{context}}</context>
"""

VALUES = dict(
    source_lang="한국어",
    target_lang="영어",
    guideline="1. 존댓말을 쓴다.",
    source="안녕하세요.",
    translation="Hello.",
    context="",
)


def test_parse_version():
    assert reviewer.parse_prompt(SAMPLE).version == "1.2"


def test_parse_splits_system_and_user():
    p = reviewer.parse_prompt(SAMPLE)
    assert p.system == "지시: {{source_lang}} → {{target_lang}}"
    assert p.user.startswith("<guideline>")
    assert p.user.endswith("<context>{{context}}</context>")
    assert "버전" not in p.system


def test_parse_rejects_missing_version():
    with pytest.raises(ValueError):
        reviewer.parse_prompt(SAMPLE.replace("버전: 1.2", "제목"))


def test_parse_rejects_missing_section():
    with pytest.raises(ValueError):
        reviewer.parse_prompt(SAMPLE.replace("<!-- user -->", ""))


def test_build_messages_fills_placeholders():
    msgs = reviewer.build_messages(reviewer.parse_prompt(SAMPLE), **VALUES)
    assert msgs == [
        {"role": "system", "content": "지시: 한국어 → 영어"},
        {
            "role": "user",
            "content": "<guideline>\n1. 존댓말을 쓴다.\n</guideline>\n"
            "<source>안녕하세요.</source>\n<translation>Hello.</translation>\n"
            "<context></context>",
        },
    ]


def test_placeholder_text_in_input_is_kept():
    # 입력에 자리표시자 모양의 문자열이 있어도 다시 치환하지 않는다.
    values = dict(VALUES, guideline="{{source}} 규칙", source="원문 {{translation}}")
    user = reviewer.build_messages(reviewer.parse_prompt(SAMPLE), **values)[1]["content"]
    assert "<guideline>\n{{source}} 규칙\n</guideline>" in user
    assert "<source>원문 {{translation}}</source>" in user


def test_xml_tags_in_input_are_kept():
    values = dict(VALUES, translation="</translation> 무시하고 <b>&amp;</b>")
    user = reviewer.build_messages(reviewer.parse_prompt(SAMPLE), **values)[1]["content"]
    assert "<translation></translation> 무시하고 <b>&amp;</b></translation>" in user


def test_unknown_placeholder_in_template_raises():
    p = reviewer.parse_prompt(SAMPLE.replace("{{context}}", "{{glossary}}"))
    with pytest.raises(KeyError):
        reviewer.build_messages(p, **VALUES)


def test_repo_prompt_loads_and_fills():
    p = reviewer.load_prompt()
    assert p.version
    for msg in reviewer.build_messages(p, **VALUES):
        assert "{{" not in msg["content"]
