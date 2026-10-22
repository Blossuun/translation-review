# translation-review

번역 검수자가 확인할 지점을 빠르게 찾도록 돕는 노트북 도구. 명세는 [docs/SPEC.md](docs/SPEC.md).

## Colab

[Colab에서 열기](https://colab.research.google.com/github/Blossuun/translation-review/blob/main/translation_review.ipynb) → 런타임 유형을 GPU로 바꾸고 첫 셀을 실행한다.
첫 셀이 저장소를 받고 Ollama 설치·실행, `qwen3.5:9b` 다운로드까지 한다. Python 패키지는 따로 설치하지 않는다.

Colab에서는 입력이 클라우드로 전송된다. 비공개 자료는 로컬에서만 검토한다.

## 로컬 (Windows)

준비물: [uv](https://docs.astral.sh/uv/), [Ollama](https://ollama.com/) (`ollama pull qwen3.5:4b`)

```
uv sync
```

VS Code에서 `translation_review.ipynb`를 열고 커널로 `.venv`를 고른 뒤 첫 셀을 실행한다.

## 개발

```
uv run python -m pytest -q
```
