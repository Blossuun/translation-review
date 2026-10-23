"""모델 연결 확인 (개발용). 가상 예시 1건을 조립해 로컬 Ollama에 보내고 결과를 출력한다.

실행: uv run python scripts/smoke.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import llm_client  # noqa: E402
import reviewer  # noqa: E402

# 가상 데이터. 규칙 2(존댓말)를 어긴 번역이다.
EXAMPLE = dict(
    source_lang="영어",
    target_lang="한국어",
    guideline=(
        "1. 제품명 'Lumo'는 번역하지 않고 그대로 쓴다.\n"
        "2. 사용자에게 하는 말은 존댓말(합니다체)로 쓴다.\n"
        "등급: 통과 / 수정 필요"
    ),
    context="앱 설정 화면의 안내 문구",
    source="Restart Lumo to apply the new settings.",
    translation="새 설정을 적용하려면 Lumo를 다시 시작해.",
)


def main():
    problem = llm_client.check()
    if problem:
        print(problem, file=sys.stderr)
        return 1

    prompt = reviewer.load_prompt()
    messages = reviewer.build_messages(prompt, **EXAMPLE)
    result = llm_client.chat(messages)

    try:
        print(json.dumps(json.loads(result.content), ensure_ascii=False, indent=2))
    except ValueError:
        print("JSON이 아닌 응답:")
        print(result.content)
    print()
    print(f"모델: {llm_client.MODEL} / 프롬프트 버전: {prompt.version}")
    print(f"소요 시간: {result.seconds}초")
    print(f"입력 글자 수: {sum(len(m['content']) for m in messages)}")
    print(f"prompt_eval_count: {result.prompt_eval_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
