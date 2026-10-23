"""프롬프트 조립과 응답 검증. 프롬프트 문구는 prompt.md에만 둔다."""

import re
from dataclasses import dataclass
from pathlib import Path

PROMPT_PATH = Path(__file__).parent / "prompt.md"

_VERSION = re.compile(r"\A버전:\s*(\S+)[ \t]*\n")
_SECTION = re.compile(r"^<!-- (system|user) -->[ \t]*$", re.MULTILINE)
_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class Prompt:
    version: str
    system: str  # system 메시지 템플릿
    user: str  # user 메시지 템플릿 (입력 데이터 자리)


def parse_prompt(text):
    """prompt.md 내용을 버전과 system·user 템플릿으로 나눈다.

    첫 줄은 `버전: X.Y`, 이어서 `<!-- system -->`, `<!-- user -->` 줄이 차례로 구간을 연다.
    """
    m = _VERSION.match(text)
    if not m:
        raise ValueError("prompt.md 첫 줄에 '버전: X.Y'가 없습니다.")
    parts = _SECTION.split(text[m.end():])
    # split 결과: [머리말, 'system', 본문, 'user', 본문]
    if parts[1::2] != ["system", "user"]:
        raise ValueError("prompt.md에 <!-- system -->, <!-- user --> 구분 줄이 차례로 있어야 합니다.")
    return Prompt(version=m.group(1), system=parts[2].strip(), user=parts[4].strip())


def load_prompt(path=PROMPT_PATH):
    return parse_prompt(Path(path).read_text(encoding="utf-8"))


def fill(template, values):
    """`{{이름}}` 자리표시자를 한 번에 채운다.

    채운 값은 다시 훑지 않으므로 입력 속 `{{...}}`·XML 태그 문자열은 그대로 남는다.
    템플릿에 values에 없는 자리표시자가 있으면 KeyError.
    """
    return _PLACEHOLDER.sub(lambda m: values[m.group(1)], template)


def build_messages(prompt, *, source_lang, target_lang, guideline, source, translation, context=""):
    """/api/chat에 보낼 messages를 만든다."""
    values = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "guideline": guideline,
        "source": source,
        "translation": translation,
        "context": context,
    }
    return [
        {"role": "system", "content": fill(prompt.system, values)},
        {"role": "user", "content": fill(prompt.user, values)},
    ]
