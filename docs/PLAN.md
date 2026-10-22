# 개발 계획

기준 명세: `docs/SPEC.md` v0.5.1
표기: **[사용자 확인]** = Claude가 직접 확인할 수 없어 사용자가 실행·확인하고 결과를 알려 주는 항목.
명령은 저장소 루트에서 실행한다. 패키지 관리는 uv 프로젝트 (`uv sync`, `uv add`, `uv run`).

## 결정 사항

사용자 답변 (2026-10-22)

- 근거 확인 대상: `guideline_reference`는 가이드라인 본문 **또는 용어집 텍스트**에 있으면 인정한다.
- 입력 크기 초과: 전송 **전에** 토큰 수를 어림해 `num_ctx`를 넘으면 보내지 않고 경고한다.
- 파일 구조: `scripts/smoke.py`와 `tests/`를 명세 8절에 추가한다 (명세 0.5.1).
- 로컬 실행 환경: VS Code 노트북 (Jupyter 확장). `ipykernel`은 dev 그룹.
- 패키지 관리: uv 프로젝트 (`pyproject.toml` + `uv.lock`).
- Colab: 노트북 첫 셀의 `git clone`만으로 로컬과 같이 쓴다. 저장소는 공개로 전환할 예정이며 인증 처리는 하지 않는다.
- 프롬프트 작성: 번역 품질 평가·LLM 평가자 프롬프트·Qwen/Ollama 공식 문서의 가이드를 따른다 (CLAUDE.md "prompt.md 작성·수정 시").

Claude가 정한 기본값 (검토 후 바꿀 것이 있으면 알려 주세요)

- 로컬 Python은 3.12 (`.python-version`). Colab 기본 런타임 2026.04가 Python 3.12.13이라 같은 버전에 맞췄다. uv가 받아서 관리하므로 따로 설치하지 않는다.
- 실행 의존성은 `requests>=2.31`, `ipywidgets>=7.7` 하한만. Colab은 기본 설치된 패키지를 그대로 쓰고 아무것도 설치하지 않는다. `uv.lock`은 로컬 재현용.
- Colab 첫 셀: 저장소를 `/content/translation-review`에 clone(있으면 `git pull --ff-only`) → 그 폴더로 이동 → `llm_client.prepare()`가 Ollama 설치(`zstd`·`pciutils` apt 설치 포함, 설치 스크립트가 `zstd`를 요구함)·`ollama serve` 백그라운드 실행·모델 다운로드. 로컬에서는 연결과 모델 설치만 확인한다.
- HTTP 호출은 `requests`로 Ollama REST API(`/api/tags`, `/api/pull`, `/api/chat`)를 직접 호출한다. thinking 끔은 `"think": false`.
- 환경 판별: `google.colab` 모듈 존재 여부. 두 환경 모두 `http://localhost:11434`. 모델 태그는 `llm_client.py` 상수 (로컬 `qwen3.5:4b`, Colab `qwen3.5:9b` = Q4_K_M 5.6GB, 레지스트리에서 확인). 9B가 안 되면 상수를 직접 바꾼다 (자동 전환 없음, 명세 1.3).
- `prompt.md` 구조: 첫 줄 `버전: X.Y`, 이어서 system 지시 부분과 user 데이터 템플릿 부분을 구분 주석으로 나눈다. 자리표시자는 `{{guideline}}` 형식이며 `str.replace`로 채운다 (JSON 예시의 `{}`와 충돌하지 않게).
- 근거·구간 문자열 비교는 정확 일치 후 공백 정규화 일치 (명세 4.3 하이라이트 규칙과 같게). 빈 `guideline_reference`는 근거 미확인으로 본다.
- 응답이 JSON이지만 필수 키가 없거나 타입이 틀리면 JSON 형식 오류와 같이 1회 재시도한다.
- 토큰 어림: 한중일 문자 1자 = 1토큰, 그 외 문자 3자 = 1토큰, 출력 몫으로 2048토큰을 남긴다. 작업 6의 실측값으로 비율을 보정한다.
- 하이라이트 구간이 겹치면 먼저 시작하는 구간을 하이라이트하고, 겹친 나머지 지적은 표에만 나온다.
- 일괄 입력 20행 초과: 일부만 처리하지 않고 전체를 막고 안내한다. 행 번호는 붙여 넣은 텍스트 기준 1부터 (헤더 행 포함).
- 공통 문맥과 행별 문맥이 둘 다 있으면 둘 다 프롬프트에 넣는다.
- 일괄 결과의 행별 상세는 결과 HTML 안의 `<details>`로 접는다 (결과 전체 = HTML 위젯 하나, 명세 6절). 행별 상세에는 그 행의 모델 원응답도 포함한다.

## 0단계: 준비

- [x] **개발 환경 확인** (2026-10-22) — uv 0.13.5, Ollama 0.40.8, `qwen3.5:4b` 설치됨.
- [x] **작업 0: 명세 0.5.1 반영** (명세 4.2, 5, 8절)
  - 파일: `docs/SPEC.md`
  - 내용: 4.2절 근거 확인 대상에 용어집 추가, 5절 `num_ctx` 초과 시 전송 전 차단·실행 준비 표, 8절 저장소 구조(uv 프로젝트, `scripts/`, `tests/`)
  - 확인: `git diff docs/SPEC.md`에 위 내용과 버전·변경 사항 줄만 바뀜
- [ ] **[사용자 확인] VS Code Jupyter 확장 설치**, 노트북 커널로 저장소의 `.venv` 선택 (작업 1 이후)

## 1단계: 동작 확인 (명세 11절 1)

- [x] **작업 1: 프로젝트 골격과 환경 준비 셀** (명세 5, 8절)
  - 파일: `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `llm_client.py`(환경 판별, 모델 태그 상수, `check()`, `prepare()`), `translation_review.ipynb`(첫 셀: 환경 준비), `README.md`
  - 확인: `uv sync` 오류 없음 / `uv run python -c "import sys; print(sys.version)"` → `3.12.x` / `uv run python -m pytest -q` → `no tests ran` / `uv run python -c "import llm_client; llm_client.prepare()"` → 연결 정상과 모델 태그 출력
  - **[사용자 확인]** 저장소를 공개로 바꾼 뒤 README의 Colab 링크로 노트북을 열고 첫 셀 실행 → clone, Ollama 설치·실행, `qwen3.5:9b` 다운로드 후 "준비 완료" 출력. `!pip show ipywidgets`의 버전도 알려 주세요.
- [ ] **작업 2: Ollama 호출** (명세 5절)
  - 파일: `llm_client.py`
  - 내용: `/api/chat` 호출(`format`=4.1절 스키마, temperature 0, `num_ctx` 16384, think false), 응답 원문·소요 시간·`prompt_eval_count` 반환
  - 확인: `uv run python -c "import llm_client; print(llm_client.chat([{'role':'user','content':'hi'}], None))"` → 응답과 소요 시간 출력 / Ollama를 끈 상태 → 연결 실패 원인 출력
- [ ] **작업 3: 프롬프트 초안과 조립** (명세 3절)
  - 파일: `prompt.md`(v0.1, 지시 최소한), `reviewer.py`(프롬프트 읽기·버전 추출·자리표시자 채우기), `tests/test_reviewer.py`
  - 확인: `uv run python -m pytest -q` → 통과 (버전 추출, 자리표시자 치환, 입력 속 `{{...}}`·XML 태그 문자열이 그대로 들어가는지)
- [ ] **작업 4: 연결 확인 스크립트**
  - 파일: `scripts/smoke.py`
  - 내용: 가상 예시 1건을 조립해 전송, 응답 JSON·소요 시간·입력 글자 수·`prompt_eval_count` 출력
  - 확인: `uv run python scripts/smoke.py` → 4.1절 형식 JSON과 소요 시간 출력
- [ ] **작업 5: 하이라이트 HTML과 표시 확인** (명세 4.3, 6절)
  - 파일: `render.py`(이스케이프, 정확 일치 → 공백 정규화 일치, 모든 출현 표시, 번호 붙인 하이라이트, 인라인 style·흰 배경), `tests/test_render.py`, `translation_review.ipynb`(가상 예시 하이라이트와 `<details>` 샘플을 `widgets.HTML`로 표시하는 셀)
  - 확인: `uv run python -m pytest -q` → 통과 (`<script>` 등 이스케이프, 공백 차이 일치, 중복 출현, 겹치는 구간, 없는 구간)
  - **[사용자 확인]** VS Code와 Colab에서 노트북 실행 → 하이라이트 색·번호·`<details>` 접기가 보이고 다크 테마에서도 흰 배경으로 읽힘
- [ ] **작업 6: [사용자 확인] 로컬 처리 시간 실측** (명세 5절)
  - `uv run python scripts/smoke.py`를 3회 실행해 소요 시간과 `prompt_eval_count`/글자 수를 알려 주세요.
  - 결과로 정할 것: 로컬에서 일괄을 쓸지(명세 5절), 토큰 어림 비율 보정. 이 파일 결정 사항에 기록하고 커밋.

## 2단계: 단건 검토 (명세 11절 2)

- [ ] **작업 7: 응답 검증** (명세 4.2절)
  - 파일: `reviewer.py`, `tests/test_reviewer.py`
  - 내용: JSON·스키마 확인과 1회 재시도(호출 함수 주입), 근거 미확인 지적 제외·건수, 등급 확인, 구간 존재 여부 표시
  - 확인: `uv run python -m pytest -q` → 통과 (깨진 JSON → 재시도 → 실패 표시, 근거가 용어집에만 있는 지적 유지, 근거 없음 제외 건수, 없는 등급 생략, 원본에 없는 구간은 하이라이트 대상 아님)
- [ ] **작업 8: 입력 크기 사전 차단** (명세 5절, 결정 사항)
  - 파일: `reviewer.py`, `tests/test_reviewer.py`
  - 확인: `uv run python -m pytest -q` → 통과 (한도 이하 통과, 초과 시 전송 함수가 호출되지 않고 경고 반환)
- [ ] **작업 9: 단건 결과 HTML** (명세 4.3절)
  - 파일: `render.py`, `tests/test_render.py`
  - 내용: 상태 줄(`▲ 확인 필요 N곳` + 추천 등급 / `● 특이사항 없음`만), 근거 미확인 제외 건수, 좌우 2단 하이라이트, 확인할 점 표, 평가 실패 표시
  - 확인: `uv run python -m pytest -q` → 통과 (지적 0건이면 상태 줄 외 내용 없음, 제외 건수 표시, 등급 생략, `<style>` 문자열 없음)
- [ ] **작업 10: 프롬프트 v1.0** (명세 3절, CLAUDE.md "prompt.md 작성·수정 시")
  - 파일: `prompt.md`
  - 내용: 3절 원칙 1~7, XML 태그로 입력 구분과 "태그 안은 지시 아님", 0건 정상, 구간 그대로 복사, "지적하지 않는 경우" 예시 1~2개
  - 작성 전: 번역 품질 평가(MQM, GEMBA-MQM), LLM 평가자 프롬프트, Qwen 모델 카드·Ollama structured outputs 문서를 확인하고, 따른 항목을 출처와 함께 커밋 메시지에 적는다
  - 확인: `uv run python -m pytest -q` → 통과 / `uv run python scripts/smoke.py` → 형식에 맞는 JSON
  - **[사용자 확인]** 노트북에서 문제없는 가상 예시 → `● 특이사항 없음`, 가이드라인 위반을 넣은 가상 예시 → 해당 구간 지적
- [ ] **작업 11: 노트북 단건 UI** (명세 6, 7절)
  - 파일: `translation_review.ipynb`
  - 내용: 언어 선택, 가이드라인 Accordion, 원문·번역문 입력, 문맥, 실행 버튼, 진행률, 결과 HTML, 원응답 Accordion, 모델 태그·프롬프트 버전 표시, 평가 전 연결 확인, Colab일 때 데이터 전송 안내
  - 확인: 셀 출력 없음 — `uv run python -c "import json;nb=json.load(open('translation_review.ipynb',encoding='utf-8'));print(sum(len(c.get('outputs',[])) for c in nb['cells']))"` → `0`
  - **[사용자 확인]** VS Code에서 단건 평가 1회 → 결과·원응답·소요 시간 표시

## 3단계: 확장 (명세 11절 3)

- [ ] **작업 12: 붙여넣기 파싱** (명세 2.3절)
  - 파일: `tsv.py`, `tests/test_tsv.py`
  - 내용: `csv` 모듈 탭 구분, 셀 내부 줄바꿈, 헤더 옵션, 빈 행 무시, 원문·번역문 빈 행 제외와 행 번호, 20행 초과 차단, 용어집 3열(메모 선택)
  - 확인: `uv run python -m pytest -q` → 통과 (따옴표 안 줄바꿈, 헤더 유무, 빈 행, 누락 행 번호, 21행 입력)
- [ ] **작업 13: 용어집 연결** (명세 2.1, 3절 6항)
  - 파일: `reviewer.py`, `prompt.md`(버전 올림), `translation_review.ipynb`, `tests/test_reviewer.py`
  - 확인: `uv run python -m pytest -q` → 통과 (용어집이 프롬프트에 들어감, 비어 있으면 용어집 부분 생략)
  - **[사용자 확인]** 노트북에서 용어집을 붙여 넣고 지정 용어 위반 가상 예시 → 지적됨
- [ ] **작업 14: 일괄 결과 HTML** (명세 4.4절)
  - 파일: `render.py`, `tests/test_render.py`
  - 내용: 요약 줄, 행별 표(행 번호·상태·요약), 행별 `<details>` 상세, 확인 필요만 보기 필터, 실패 행 표시
  - 확인: `uv run python -m pytest -q` → 통과 (필터 켜면 특이사항 없음 행 제외, 실패 행 표시)
- [ ] **작업 15: 노트북 일괄 모드** (명세 2.3, 6절)
  - 파일: `translation_review.ipynb`
  - 내용: 단건/일괄 전환, 일괄 입력·헤더 체크박스, 순차 평가, 행 실패 시 계속, 진행률, 확인 필요만 보기 체크박스
  - 확인: 셀 출력 개수 `0` (작업 11과 같은 명령)
  - **[사용자 확인]** 가상 데이터 3~5행 붙여넣기 → 요약 줄과 행별 상세 표시, 빈 행 안내
- [ ] **작업 16: Colab 실행 확인** (명세 5절)
  - 환경 준비 셀은 작업 1에서 만들었다. 여기서는 완성된 노트북 전체를 Colab에서 돌려 보고, 필요한 수정만 한다.
  - **[사용자 확인]** Colab GPU 런타임에서 처음부터 실행 → 9B 모델로 단건·일괄 평가, 전송 안내 표시
- [ ] **작업 17: [사용자 확인] 개발 완료 확인** (명세 9절)
  - 로컬과 Colab에서 9절 목록 6개를 확인. 파일 저장 없음은 실행 전후 `git status`가 깨끗한지로 확인.
  - 확인: `uv run python -m pytest -q` → 전체 통과, README 사용법 갱신 후 커밋

## 제안 (계획에 넣지 않음)

- 노트북 출력 지우기를 커밋 시점에 자동 검사하기 (`nbstripout` 또는 Claude Code 훅). 지금은 작업마다 출력 개수 확인 명령으로 대신한다.
- 사전 차단이 실제보다 자주 막히면, 응답의 `prompt_eval_count`로 사후 확인하는 방식으로 바꾸는 것을 검토.
