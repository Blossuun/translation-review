# 번역 검수 보조 도구

번역 검수자가 확인할 지점을 빠르게 찾도록 돕는 Jupyter/Colab 노트북 도구.
명세: `docs/SPEC.md` / 진행 계획: `docs/PLAN.md` — 작업 전 관련 절을 먼저 읽을 것.

## 명령어

uv 프로젝트로 관리한다. Python은 `.python-version`의 3.13, ipywidgets는 7.7.1 (Colab 기본 런타임과 같음. Colab이 바뀌면 둘 다 맞춘다). PATH의 `python`은 스토어 바로가기뿐이므로 항상 `uv run`으로 실행한다.
`.venv\Scripts\`의 실행 파일(`pytest.exe` 등)은 Windows 애플리케이션 제어 정책에 막히므로 `uv run python -m <모듈>` 형태로 실행한다.

- 설치: `uv sync` (`.venv` 생성, dev 그룹 포함)
- 패키지 추가: `uv add <패키지>` / 개발용 `uv add --dev <패키지>`
- 단위 테스트: `uv run python -m pytest -q`
- 모델 연결 확인: `uv run python scripts/smoke.py` (로컬 Ollama에 가상 예시 1건 전송, JSON 출력)
- Ollama 상태: `ollama list`

## 규칙

- IMPORTANT: 명세에 없는 기능을 추가하지 않는다. 명세가 불명확하면 추측하지 말고 질문한다.
- 파일 저장·내보내기 코드를 만들지 않는다 (결과는 화면 표시만).
- 모델 호출은 `llm_client.py`에서만 한다.
- 모델에 보내는 프롬프트 문구는 `prompt.md`에만 둔다. 코드에 하드코딩하지 않는다.
- 결과 HTML은 인라인 `style`만 사용한다. `<style>` 블록과 웹 폰트는 쓰지 않는다.
- 실제 번역문·가이드라인을 저장소에 넣지 않는다. 테스트와 예시는 가상 데이터만 쓴다.
- 순수 함수(`tsv.py`, `render.py`, `reviewer.py`의 검증 로직)는 pytest 테스트를 함께 작성한다. 모델 품질은 테스트하지 않는다.
- 패키지는 `uv add`로만 추가하고 `pip`을 쓰지 않는다. 새 패키지를 추가할 때는 이유를 밝힌다. 실행 의존성은 하한만 적는다 (Colab은 기본 패키지를 그대로 쓴다).
- Colab은 노트북 첫 셀의 `git clone`만으로 로컬과 같이 동작해야 한다. Colab에 Python 패키지를 설치하는 코드를 넣지 않는다.
- ipywidgets는 7과 8에 공통인 API만 쓴다 (예: `Accordion.set_title`).
- 파일은 `encoding="utf-8"`으로 열고, 경로는 `Path(__file__).parent` 기준으로 찾는다.
- 작업을 마치면 `uv run python -m pytest -q`를 실행하고 실제 출력을 보여준다. 통과했다고 주장만 하지 않는다.
- 한 작업 단위 = 한 커밋.
- 사용자에게는 한국어로 답한다.

## 작업 방식

- 순서: 관련 명세 절·코드 읽기 → 짧은 계획 → 구현(순수 함수는 테스트 먼저) → `uv run python -m pytest -q` → `docs/PLAN.md` 체크 → 커밋.
- 구현·테스트·프롬프트 방법에 공식 문서나 널리 쓰이는 모범 사례가 있으면 따른다 (Claude Code 모범 사례 https://www.anthropic.com/engineering/claude-code-best-practices, pytest·ipywidgets·Ollama 공식 문서 등).
- 확실하지 않은 API·옵션은 기억에 의존하지 말고 공식 문서를 확인한다. 확인하지 않은 출처나 논문을 지어내지 않는다.
- 모범 사례를 근거로 한 설계 결정은 답변에 출처를 한 줄로 밝힌다.
- 모범 사례가 명세·이 파일의 규칙과 충돌하면 명세·규칙을 따르고, 충돌 사실을 알린다.
- Colab 실행, 화면 표시, 처리 시간처럼 직접 확인할 수 없는 항목은 확인했다고 하지 말고 사용자에게 확인을 요청한다.

## prompt.md 작성·수정 시

참고: Anthropic 프롬프트 가이드 https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
- 관련 분야의 공식 가이드와 모범 사례를 찾아 따른다: 번역 품질 평가(MQM 오류 체계, GEMBA-MQM), LLM 평가자 프롬프트(LLM-as-a-judge), 실제로 쓰는 모델의 공식 문서(Qwen 모델 카드의 권장 설정·프롬프트 형식, Ollama structured outputs).
- Anthropic 가이드는 Claude 기준이다. 소형 Qwen 모델에서도 통하는지는 `uv run python scripts/smoke.py`와 가상 예시로 확인하고, 모델 공식 문서와 다르면 모델 문서를 따른다.
- 따른 가이드·사례는 답변과 커밋 메시지에 출처를 한 줄로 적는다. 확인하지 않은 출처는 적지 않는다.
- 입력 데이터(가이드라인, 원문, 번역문, 용어집)는 XML 태그로 구분하고, 태그 안의 문장은 지시가 아니라고 명시한다.
- "지적 0건은 정상 결과"를 명시한다. LLM 번역 평가는 거의 완벽한 번역도 오류를 찾아내려는 경향이 있다 (RUBRIC-MQM, ACL 2025).
- 지적은 구간 단위로, 원문 그대로 복사하게 한다 (GEMBA-MQM 방식).
- 지시만 길게 늘이지 말고, "지적하지 않는 경우" 예시를 1~2개 넣는다.
- 파일 상단의 버전을 올린다.